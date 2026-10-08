#!/usr/bin/env python

# Copyright 2026 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Interactive GUI to calibrate the AmazingHand open/close angles and the leader
gripper direction.

Layout (top -> bottom):
  - Hand section: 4 finger sliders + [Save Open] / [Save Close] / [Reset]
  - Leader section: live gripper value + [Capture Open] / [Capture Close]
  - Log panel: colour-coded status lines (which device, and the saved state)

The window is resizable: the content area and the log panel each get their own
always-visible scroll bar, and long log lines wrap to the panel width.

When both finger poses and both gripper captures are set, everything is
auto-saved to `hand_angles.json` in the robot calibration dir.

Usage:
    python -m lerobot.scripts.lerobot_calibrate_amazing_hand \
        --hand_port COM11 --leader_port COM54
"""

import argparse
import json
import logging
import time
from pathlib import Path

import numpy as np
import pygame
from rustypot import Scs0009PyController

from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig
from lerobot.teleoperators.so_leader.so_leader import SO101Leader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# servo id -> (finger, m1/m2)
FINGERS = {
    "index":  (1, 2),
    "middle": (3, 4),
    "ring":   (5, 6),
    "thumb":  (7, 8),
}
FINGER_ORDER = ["index", "middle", "ring", "thumb"]

# Middle positions (degrees) for the 8 servos, in servo-id order 1..8.
MIDDLE_POS = [3.0, 0.0, -5.0, -8.0, -2.0, 5.0, -12.0, 0.0]

ANGLE_MIN, ANGLE_MAX = -144, 144  # scs0009 angle limits

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
BG = (24, 26, 30)
PANEL = (32, 35, 40)
PANEL_HDR = (44, 48, 56)
SEP = (60, 64, 72)
TEXT = (235, 235, 235)
SUBTEXT = (160, 168, 178)
SLIDER_BG = (60, 64, 72)
SLIDER_ACTIVE = (70, 200, 120)
HANDLE = (240, 240, 240)
BTN = (70, 74, 84)
BTN_HL = (110, 116, 128)
YELLOW = (235, 200, 70)
SCROLL_TRACK = (50, 54, 62)
SCROLL_THUMB = (110, 116, 128)
SCROLL_THUMB_HL = (140, 146, 158)

LOG_OK = (90, 210, 120)
LOG_ERR = (230, 90, 90)
LOG_INFO = (170, 178, 188)
LOG_HL = (110, 230, 150)

# --------------------------------------------------------------------------
# Layout constants (fixed; many derive from window size at draw time)
# --------------------------------------------------------------------------
WINDOW_W = 820
WINDOW_H = 700
TITLE_H = 44
LOG_H = 170
PAD = 24
ROW_H = 46
BTN_H = 34
BTN_W = 130
BTN_GAP = 12
LINE_H = 22          # content line spacing
SCROLLBAR_W = 8
SCROLLBAR_MARGIN = 4


def fmt_angles(angles, max_len=3):
    """Compact display of an 8-element angle list: [-70, 70, 0, ...]."""
    shown = [round(a) for a in angles[:max_len]]
    return "[" + ", ".join(str(a) for a in shown) + (", ...]" if len(angles) > max_len else "]")


def load_cjk_font(size=20):
    """Load a font that contains CJK glyphs, so Chinese labels render properly.

    pygame's default font (Font(None, ...)) has no Chinese glyphs, so any Chinese
    text shows as boxes. This tries common CJK fonts per OS and falls back to the
    default font if none is found.
    """
    import sys

    import pygame as pg

    candidates = {
        "win32": [
            "msyh", "msyhbd", "simhei", "simsun", "kaiti", "dengxian", "Microsoft YaHei",
        ],
        "linux": [
            "notosanscjk", "notosanscjksc", "notosanscjkregular", "wqy-microhei",
            "wqyzenhei", "sourcehansans", "arplumingcn", "droidsansfallback",
        ],
        "darwin": ["pingfangsc", "stheiti", "hiraginosansgb", "helveticaneue"],
    }
    platform_key = "win32" if sys.platform.startswith("win") else ("darwin" if sys.platform == "darwin" else "linux")
    for name in candidates.get(platform_key, []):
        path = pg.font.match_font(name)
        if path:
            try:
                return pg.font.Font(path, size)
            except Exception:
                continue
    # Fall back to pygame's built-in font (no CJK, but at least renders).
    return pg.font.Font(None, size)


def wrap_text(text, font, max_width):
    """Wrap a string to a list of lines that each fit within max_width.

    Breaks on spaces when present (Latin); otherwise breaks by character, which
    is what Chinese text needs (no spaces between hanzi).
    """
    if max_width <= 0:
        return [text]
    lines = []
    current = ""
    for ch in text:
        if ch == "\n":
            lines.append(current)
            current = ""
            continue
        trial = current + ch
        if font.size(trial)[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


class FingerSlider:
    """One slider per finger. angle is relative to the finger's middle position."""

    def __init__(self, finger, idx, ctrl, base_y):
        self.finger = finger
        self.idx = idx
        self.ctrl = ctrl
        self.y = base_y + idx * ROW_H      # absolute content y
        self.angle = 0.0
        self.dragging = False
        self.font = load_cjk_font(22)

    def servo_ids(self):
        return list(FINGERS[self.finger])

    def _x_from_angle(self, angle, slider_x, slider_w):
        frac = (angle - ANGLE_MIN) / (ANGLE_MAX - ANGLE_MIN)
        return slider_x + frac * slider_w

    def _angle_from_x(self, x, slider_x, slider_w):
        frac = max(0.0, min(1.0, (x - slider_x) / slider_w))
        return ANGLE_MIN + frac * (ANGLE_MAX - ANGLE_MIN)

    def write(self):
        # m1 = +angle, m2 = -angle, applied as offsets from each servo's middle position.
        targets = []
        ids = self.servo_ids()
        for sid in ids:
            mid = MIDDLE_POS[sid - 1]
            offset = self.angle if sid == ids[0] else -self.angle
            targets.append(np.deg2rad(mid + offset))
        self.ctrl.sync_write_goal_speed(ids, [5] * len(ids))
        self.ctrl.sync_write_goal_position(ids, targets)

    def handle_event(self, e, scroll_y, slider_x, slider_w):
        click_y = e.pos[1] + scroll_y
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            hx = self._x_from_angle(self.angle, slider_x, slider_w)
            if abs(e.pos[0] - hx) <= 12 and abs(click_y - self.y) <= 10:
                self.dragging = True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.dragging = False
        elif e.type == pygame.MOUSEMOTION and self.dragging:
            self.angle = round(self._angle_from_x(e.pos[0], slider_x, slider_w))
            self.write()

    def draw(self, surf, scroll_y, slider_x, slider_w, view_h):
        dy = self.y - scroll_y
        if dy < -ROW_H or dy > view_h + ROW_H:
            return
        surf.blit(self.font.render(self.finger, True, TEXT), (12, dy - 8))
        pygame.draw.rect(surf, SLIDER_BG, (slider_x, dy - 4, slider_w, 8))
        mid_x = self._x_from_angle(0.0, slider_x, slider_w)
        hx = self._x_from_angle(self.angle, slider_x, slider_w)
        lo, hi = sorted((mid_x, hx))
        pygame.draw.rect(surf, SLIDER_ACTIVE, (lo, dy - 4, hi - lo, 8))
        pygame.draw.circle(surf, HANDLE, (int(hx), dy), 9)
        surf.blit(self.font.render(f"{self.angle:.0f}°", True, YELLOW), (slider_x + slider_w + 16, dy - 8))


class Scrollbar:
    """A simple vertical scroll bar for a content area."""

    def __init__(self, x, y, h):
        self.rect = pygame.Rect(x, y, SCROLLBAR_W, h)
        self.dragging = False

    def draw(self, surf, scroll_y, content_h, hover):
        max_scroll = max(0, content_h - self.rect.h)
        pygame.draw.rect(surf, SCROLL_TRACK, self.rect, border_radius=4)
        if max_scroll <= 0:
            # No overflow: draw a full-height thumb to indicate "nothing to scroll".
            pygame.draw.rect(surf, SCROLL_THUMB, self.rect, border_radius=4)
            return
        frac = scroll_y / max_scroll
        thumb_h = max(28, int(self.rect.h * self.rect.h / content_h))
        thumb_y = self.rect.y + int(frac * (self.rect.h - thumb_h))
        thumb = pygame.Rect(self.rect.x, thumb_y, SCROLLBAR_W, thumb_h)
        clr = SCROLL_THUMB_HL if (hover or self.dragging) else SCROLL_THUMB
        pygame.draw.rect(surf, clr, thumb, border_radius=4)

    def hit(self, pos):
        return self.rect.collidepoint(pos)


class CalibrationApp:
    def __init__(self, ctrl, leader, args):
        self.ctrl = ctrl
        self.leader = leader
        self.args = args
        self.servo_ids = list(range(1, 9))

        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
        pygame.display.set_caption("AmazingHand + 主动臂 标定工具")
        self.font = load_cjk_font(26)
        self.small = load_cjk_font(21)
        self.tiny = load_cjk_font(18)

        # Absolute content coordinates (independent of window size; the content
        # area just scrolls). These derive from fixed step sizes.
        y = TITLE_H + 16
        self.hand_title_y = y
        y += 34
        self.sliders = [FingerSlider(finger, i, ctrl, y) for i, finger in enumerate(FINGER_ORDER)]
        y += len(FINGER_ORDER) * ROW_H + 12
        self.save_open_btn = pygame.Rect(PAD, y, BTN_W, BTN_H)
        self.save_close_btn = pygame.Rect(PAD + BTN_W + BTN_GAP, y, BTN_W, BTN_H)
        self.reset_btn = pygame.Rect(PAD + 2 * (BTN_W + BTN_GAP), y, BTN_W, BTN_H)
        y += BTN_H + 22

        self.leader_title_y = y
        y += 34
        self.gripper_live_y = y
        y += 26
        self.cap_open_btn = pygame.Rect(PAD, y, BTN_W, BTN_H)
        self.cap_close_btn = pygame.Rect(PAD + BTN_W + BTN_GAP, y, BTN_W, BTN_H)
        y += BTN_H + 16
        self.content_h = y  # total content height for the scrollable area

        self.scroll_y = 0
        self.log_scroll = 0
        self._live_frame = 0
        self._live_val = None

        self.saved_open = None
        self.saved_close = None
        self.gripper_open = None
        self.gripper_close = None
        self.logs = []  # list of (time_str, color, text)

        self.running = True
        self.clock = pygame.time.Clock()

        # Scroll bars are (re)positioned each frame from the current window size.
        self.content_scrollbar = Scrollbar(0, 0, 0)
        self.log_scrollbar = Scrollbar(0, 0, 0)
        self._dragging_content = False
        self._dragging_log = False

    # ------------------------------------------------------------------ geometry
    @property
    def win_w(self):
        return self.screen.get_width()

    @property
    def win_h(self):
        return self.screen.get_height()

    @property
    def view_top(self):
        return TITLE_H

    @property
    def view_bottom(self):
        return self.win_h - LOG_H

    @property
    def view_h(self):
        return max(0, self.view_bottom - self.view_top)

    @property
    def log_top(self):
        return self.win_h - LOG_H

    @property
    def log_view_h(self):
        return max(0, LOG_H - 34)

    @property
    def content_max_scroll(self):
        return max(0, self.content_h - self.view_h)

    @property
    def slider_x(self):
        return PAD + 80

    @property
    def slider_w(self):
        # Sliders shrink/grow with the window, leaving room for the scroll bar.
        return max(120, self.win_w - self.slider_x - PAD - SCROLLBAR_W - SCROLLBAR_MARGIN - 90)

    @property
    def log_text_width(self):
        return self.win_w - PAD * 2 - SCROLLBAR_W - SCROLLBAR_MARGIN - 4

    # ------------------------------------------------------------------ log
    def add_log(self, color, text):
        ts = time.strftime("%H:%M:%S")
        self.logs.append((ts, color, text))
        if len(self.logs) > 300:
            self.logs = self.logs[-300:]
        self.log_scroll = 0

    def wrapped_log_lines(self):
        """Return [(color, wrapped_line, text)] where wrapped_line is the rendered string."""
        width = self.log_text_width
        out = []
        for ts, color, text in self.logs:
            msg = f"{ts}  {text}"
            for line in wrap_text(msg, self.tiny, width):
                out.append((color, line))
        return out

    # --------------------------------------------------------------- helpers
    def current_angles(self):
        angles = [0.0] * 8
        for slider in self.sliders:
            id1, id2 = FINGERS[slider.finger]
            angles[id1 - 1] = slider.angle
            angles[id2 - 1] = -slider.angle
        return angles

    def read_gripper_pos(self, force=False):
        if self.leader is None:
            return None
        self._live_frame += 1
        if not force and self._live_frame % 12 != 0:
            return self._live_val
        try:
            action = self.leader.get_action()
            self._live_val = float(action["gripper.pos"])
        except Exception:
            self._live_val = None
        return self._live_val

    def save_path(self):
        return self.args.output if self.args.output is not None else (
            Path.home()
            / ".cache"
            / "huggingface"
            / "lerobot"
            / "calibration"
            / "robots"
            / "so101_amazing_hand"
            / "hand_angles.json"
        )

    def maybe_autosave(self):
        if self.saved_open is None or self.saved_close is None:
            return None
        if self.leader is not None and (self.gripper_open is None or self.gripper_close is None):
            return None
        out = self.save_path()
        out.parent.mkdir(parents=True, exist_ok=True)
        data = {"hand_open_angles": self.saved_open, "hand_close_angles": self.saved_close}
        if self.leader is not None:
            data["gripper_open_pos"] = self.gripper_open
            data["gripper_close_pos"] = self.gripper_close
        out.write_text(json.dumps(data, indent=4))
        return out

    # ------------------------------------------------------------------ events
    def handle_click(self, e):
        click_y = e.pos[1] + self.scroll_y
        if self.save_open_btn.collidepoint((e.pos[0], click_y)):
            self.saved_open = self.current_angles()
            self.add_log(LOG_OK, f"[灵巧手] 张开角度已保存 {fmt_angles(self.saved_open)}")
        elif self.save_close_btn.collidepoint((e.pos[0], click_y)):
            self.saved_close = self.current_angles()
            self.add_log(LOG_OK, f"[灵巧手] 握拳角度已保存 {fmt_angles(self.saved_close)}")
        elif self.reset_btn.collidepoint((e.pos[0], click_y)):
            for s in self.sliders:
                s.angle = 0.0
                s.write()
            self.add_log(LOG_INFO, "[灵巧手] 已复位到中位")
        elif self.cap_open_btn.collidepoint((e.pos[0], click_y)):
            val = self.read_gripper_pos(force=True)
            if val is None:
                self.add_log(LOG_ERR, "[主动臂] 读取失败，请检查主动臂连接")
            else:
                self.gripper_open = round(val, 1)
                self.add_log(LOG_OK, f"[主动臂] 张开夹爪捕获 gripper={self.gripper_open}")
        elif self.cap_close_btn.collidepoint((e.pos[0], click_y)):
            val = self.read_gripper_pos(force=True)
            if val is None:
                self.add_log(LOG_ERR, "[主动臂] 读取失败，请检查主动臂连接")
            else:
                self.gripper_close = round(val, 1)
                self.add_log(LOG_OK, f"[主动臂] 闭合夹爪捕获 gripper={self.gripper_close}")

        saved = self.maybe_autosave()
        if saved is not None:
            self.add_log(LOG_HL, f"✔ 全部标定完成，已保存 {saved}")

    def handle_wheel(self, e):
        mouse_y = pygame.mouse.get_pos()[1]
        if mouse_y >= self.log_top:
            total = len(self.wrapped_log_lines())
            visible = max(1, self.log_view_h // LINE_H)
            self.log_scroll = max(0, min(total - visible, self.log_scroll + e.y))
        else:
            self.scroll_y = max(0, min(self.content_max_scroll, self.scroll_y - e.y * 36))

    def handle_scrollbar_drag(self, e):
        if self._dragging_content:
            if self.content_max_scroll <= 0:
                return
            frac = (e.pos[1] - self.content_scrollbar.rect.y) / max(1, self.content_scrollbar.rect.h)
            self.scroll_y = max(0, min(self.content_max_scroll, int(frac * self.content_max_scroll)))
        elif self._dragging_log:
            total = len(self.wrapped_log_lines())
            visible = max(1, self.log_view_h // LINE_H)
            max_scroll = max(0, total - visible)
            frac = (e.pos[1] - self.log_scrollbar.rect.y) / max(1, self.log_scrollbar.rect.h)
            self.log_scroll = max(0, min(max_scroll, int(frac * max_scroll)))

    def handle_mousedown(self, e):
        # Check content scroll bar first, then log scroll bar.
        if self.content_scrollbar.hit(e.pos) and self.content_max_scroll > 0:
            self._dragging_content = True
            self.handle_scrollbar_drag(e)
            return
        if self.log_scrollbar.hit(e.pos):
            self._dragging_log = True
            self.handle_scrollbar_drag(e)
            return
        self.handle_click(e)
        # Let the finger sliders also see the press (so a handle can be grabbed).
        for s in self.sliders:
            s.handle_event(e, self.scroll_y, self.slider_x, self.slider_w)

    # ------------------------------------------------------------------ draw
    def draw_scrollbars(self, mouse):
        # Content scroll bar.
        self.content_scrollbar.rect = pygame.Rect(
            self.win_w - SCROLLBAR_W - SCROLLBAR_MARGIN, self.view_top, SCROLLBAR_W, self.view_h
        )
        self.content_scrollbar.draw(self.screen, self.scroll_y, self.content_h,
                                    self.content_scrollbar.hit(mouse))

        # Log scroll bar.
        self.log_scrollbar.rect = pygame.Rect(
            self.win_w - SCROLLBAR_W - SCROLLBAR_MARGIN, self.log_top + 32, SCROLLBAR_W, self.log_view_h - 2
        )
        total_log = len(self.wrapped_log_lines())
        visible_log = max(1, self.log_view_h // LINE_H)
        self.log_scrollbar.draw(self.screen, self.log_scroll, total_log * LINE_H,
                                self.log_scrollbar.hit(mouse))

    def draw(self):
        self.screen.fill(BG)
        mouse = pygame.mouse.get_pos()
        win_w, win_h = self.win_w, self.win_h

        # Title bar
        pygame.draw.rect(self.screen, PANEL_HDR, (0, 0, win_w, TITLE_H))
        self.screen.blit(self.font.render("AmazingHand 灵巧手 + 主动臂 标定工具", True, TEXT),
                         (PAD, TITLE_H // 2 - 12))
        status = "模拟模式" if (self.leader is not None and hasattr(self.leader, "get_action") and getattr(self.args, "simulate", False)) else ("已连接" if self.leader is not None else "仅灵巧手")
        self.screen.blit(self.tiny.render(f"主动臂: {status}", True, SUBTEXT), (win_w - 220, TITLE_H // 2 - 8))

        # ---- scrollable content area ----
        slider_x, slider_w = self.slider_x, self.slider_w
        for s in self.sliders:
            s.draw(self.screen, self.scroll_y, slider_x, slider_w, self.view_h)

        section_title(self.screen, self.font, "灵巧手 · 手指开合角度", self.hand_title_y, win_w)
        click_y = mouse[1] + self.scroll_y
        draw_button(self.screen, self.save_open_btn, "保存张开", self.font,
                    self.save_open_btn.collidepoint((mouse[0], click_y)), self.scroll_y)
        draw_button(self.screen, self.save_close_btn, "保存握拳", self.font,
                    self.save_close_btn.collidepoint((mouse[0], click_y)), self.scroll_y)
        draw_button(self.screen, self.reset_btn, "复位中位", self.font,
                    self.reset_btn.collidepoint((mouse[0], click_y)), self.scroll_y)

        section_title(self.screen, self.font, "主动臂 · 夹爪方向", self.leader_title_y, win_w)
        live = self.read_gripper_pos()
        live_txt = f"gripper.pos = {live:.1f}" if live is not None else "读取失败"
        self.screen.blit(self.small.render(f"实时夹爪位置: {live_txt}", True, YELLOW),
                         (PAD, self.gripper_live_y - self.scroll_y))
        draw_button(self.screen, self.cap_open_btn, "捕获张开", self.font,
                    self.cap_open_btn.collidepoint((mouse[0], click_y)), self.scroll_y)
        draw_button(self.screen, self.cap_close_btn, "捕获闭合", self.font,
                    self.cap_close_btn.collidepoint((mouse[0], click_y)), self.scroll_y)

        # Saved-state summary.
        sy = self.cap_close_btn.y + BTN_H + 12
        if self.saved_open is not None:
            self.screen.blit(self.tiny.render(f"张开: {fmt_angles(self.saved_open)}", True, LOG_OK),
                             (PAD, sy - self.scroll_y))
            sy += 20
        if self.saved_close is not None:
            self.screen.blit(self.tiny.render(f"握拳: {fmt_angles(self.saved_close)}", True, LOG_OK),
                             (PAD, sy - self.scroll_y))
            sy += 20
        if self.gripper_open is not None:
            self.screen.blit(self.tiny.render(f"夹爪张开 = {self.gripper_open}", True, LOG_OK),
                             (PAD, sy - self.scroll_y))
            sy += 20
        if self.gripper_close is not None:
            self.screen.blit(self.tiny.render(f"夹爪闭合 = {self.gripper_close}", True, LOG_OK),
                             (PAD, sy - self.scroll_y))

        # ---- fixed log panel ----
        log_y = self.log_top
        pygame.draw.rect(self.screen, PANEL, (0, log_y, win_w, LOG_H))
        pygame.draw.line(self.screen, SEP, (0, log_y), (win_w, log_y), 1)
        self.screen.blit(self.font.render("日志", True, TEXT), (PAD, log_y + 6))

        wrapped = self.wrapped_log_lines()
        visible_log = max(1, self.log_view_h // LINE_H)
        start = max(0, len(wrapped) - visible_log - self.log_scroll)
        lines = wrapped[start:start + visible_log]
        ly = log_y + 32
        for color, text in lines:
            self.screen.blit(self.tiny.render(text, True, color), (PAD, ly))
            ly += LINE_H
        if not wrapped:
            self.screen.blit(self.tiny.render("等待操作...", True, SUBTEXT), (PAD, ly))

        self.draw_scrollbars(mouse)
        pygame.display.flip()

    # ------------------------------------------------------------------ run
    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.VIDEORESIZE:
                    # Rebuild the surface at the new size.
                    self.screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.handle_mousedown(e)
                elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    self._dragging_content = False
                    self._dragging_log = False
                    for s in self.sliders:
                        s.handle_event(e, self.scroll_y, self.slider_x, self.slider_w)
                elif e.type == pygame.MOUSEMOTION:
                    if self._dragging_content or self._dragging_log:
                        self.handle_scrollbar_drag(e)
                    for s in self.sliders:
                        s.handle_event(e, self.scroll_y, self.slider_x, self.slider_w)
                elif e.type == pygame.MOUSEWHEEL:
                    self.handle_wheel(e)
            self.draw()
            self.clock.tick(60)

    def cleanup(self):
        self.ctrl.sync_write_torque_enable(self.servo_ids, [0] * 8)
        if self.leader is not None:
            self.leader.disconnect()
        pygame.quit()


def section_title(surf, font, text, y, width):
    """Draw a section header with an accent bar."""
    bar = pygame.Rect(PAD, y, 5, 20)
    pygame.draw.rect(surf, SLIDER_ACTIVE, bar, border_radius=2)
    surf.blit(font.render(text, True, TEXT), (PAD + 14, y))
    pygame.draw.line(surf, SEP, (PAD, y + 30), (width - PAD, y + 30), 1)


def draw_button(surf, rect, text, font, hover, scroll_y=0):
    r = rect.move(0, -scroll_y)
    clr = BTN_HL if hover else BTN
    pygame.draw.rect(surf, clr, r, border_radius=6)
    t = font.render(text, True, TEXT)
    surf.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))


# --------------------------------------------------------------------------
# Simulated devices (used with --simulate so the GUI can be previewed without
# any hardware attached).
# --------------------------------------------------------------------------
class SimulatedScsController:
    def sync_write_torque_enable(self, ids, vals):
        pass

    def sync_write_goal_speed(self, ids, sp):
        pass

    def sync_write_goal_position(self, ids, pos):
        pass


class SimulatedLeader:
    def __init__(self):
        self._frame = 0

    def get_action(self):
        self._frame += 1
        import math
        val = 50 + 47 * math.sin(self._frame / 20.0)
        return {"gripper.pos": max(0.0, min(100.0, val))}

    def connect(self, calibrate=True):
        pass

    def disconnect(self):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hand_port", default=None,
                        help="Serial port of the AmazingHand (e.g. COM11). Required unless --simulate.")
    parser.add_argument("--baudrate", type=int, default=1_000_000)
    parser.add_argument(
        "--leader_port", type=str, default=None,
        help="Serial port of the leader arm (e.g. COM54). Enables gripper-direction calibration. "
        "If omitted, only hand finger angles are calibrated.",
    )
    parser.add_argument("--leader_id", type=str, default="amazing_hand_leader",
                        help="Robot id of the leader arm (default: amazing_hand_leader).")
    parser.add_argument(
        "--output", type=Path, default=None,
        help="JSON file to auto-save to (default: "
        "~/.cache/huggingface/lerobot/calibration/robots/so101_amazing_hand/hand_angles.json).",
    )
    parser.add_argument(
        "--simulate", action="store_true",
        help="Run without hardware using simulated devices (preview the GUI).",
    )
    args = parser.parse_args()

    if args.simulate:
        ctrl = SimulatedScsController()
        leader = SimulatedLeader()
        logger.info("Running in SIMULATE mode (no hardware).")
    else:
        if not args.hand_port:
            parser.error("--hand_port is required when not using --simulate.")
        ctrl = Scs0009PyController(serial_port=args.hand_port, baudrate=args.baudrate, timeout=0.5)
        ctrl.sync_write_torque_enable(list(range(1, 9)), [1] * 8)
        logger.info("AmazingHand torque enabled on %s", args.hand_port)

        leader = None
        if args.leader_port:
            leader_cfg = SOLeaderTeleopConfig(
                port=args.leader_port, id=args.leader_id, use_degrees=True, num_read_retries=2,
            )
            leader = SO101Leader(leader_cfg)
            leader.connect(calibrate=True)
            logger.info("Leader arm connected on %s", args.leader_port)

    app = CalibrationApp(ctrl, leader, args)
    if args.simulate:
        app.add_log(LOG_INFO, "模拟模式 · 未连接真实硬件")
        app.add_log(LOG_INFO, "主动臂已连接 (模拟)")
    else:
        app.add_log(LOG_INFO, "灵巧手扭矩已启用")
        if leader is not None:
            app.add_log(LOG_INFO, f"主动臂已连接 ({args.leader_port})")
    try:
        app.run()
    finally:
        app.cleanup()
        logger.info("AmazingHand torque disabled, done.")


if __name__ == "__main__":
    main()
