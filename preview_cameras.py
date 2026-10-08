"""Live preview of the OpenCV cameras, to check framing/focus before recording.

Usage:
    python preview_cameras.py          # previews indices 1 and 0 (index 1 opened first)
    python preview_cameras.py 0 1      # previews the given indices in the given order

Press q or ESC to quit.

Note: on some Windows machines the second USB camera only opens if it is
initialised before the first one, so the default order is "1 0".
"""

import sys

import cv2
import numpy as np

indices = [int(a) for a in sys.argv[1:]] or [1, 0]

caps = []
for i in indices:
    cap = cv2.VideoCapture(i)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    caps.append((i, cap))
    print(f"camera index {i}: opened={cap.isOpened()}")

if not any(c.isOpened() for _, c in caps):
    print("No camera could be opened.")
    sys.exit(1)

print("Press q or ESC to quit.")
while True:
    frames = []
    for i, cap in caps:
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        cv2.putText(frame, f"index {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        frames.append(cv2.resize(frame, (480, 360)))
    if frames:
        cv2.imshow("cameras (q to quit)", np.hstack(frames))
    if (cv2.waitKey(1) & 0xFF) in (27, ord("q")):
        break

for _, cap in caps:
    cap.release()
cv2.destroyAllWindows()
