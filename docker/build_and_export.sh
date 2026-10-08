#!/usr/bin/env bash
#
# SO-ARM101 + AmazingHand 镜像 构建 / 导出脚本
#
# 用法（在项目根目录执行）：
#   bash docker/build_and_export.sh cpu      # 只做 CPU 版（约 1 GB）
#   bash docker/build_and_export.sh cuda     # 只做 CUDA 版（约 3.5 GB）
#   bash docker/build_and_export.sh both     # 两版都做
#
# 产出：./dist/lerobot-amazinghand-cpu.tar / -cuda.tar
# 客户侧导入：docker load -i lerobot-amazinghand-cpu.tar
#
set -euo pipefail

TARGET="${1:-cpu}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"

# ── 国内网络加速（按需修改或注释掉）─────────────────────────
# Docker Hub 基础镜像加速地址
BASE_IMAGE_MIRROR="${BASE_IMAGE_MIRROR:-docker.m.daocloud.io/library/python:3.12-slim}"
# pip 源
PIP_INDEX="${PIP_INDEX:-https://pypi.tuna.tsinghua.edu.cn/simple}"
# torch 源（国内建议用阿里云）
TORCH_INDEX_CPU="${TORCH_INDEX_CPU:-https://download.pytorch.org/whl/cpu}"
TORCH_INDEX_CUDA="${TORCH_INDEX_CUDA:-https://mirrors.aliyun.com/pytorch-wheels/cu128}"
# ──────────────────────────────────────────────────────────

cd "${PROJECT_ROOT}"
mkdir -p "${DIST_DIR}"

build_cpu() {
  echo "==> 构建 CPU 版镜像 ..."
  docker build \
    -f docker/Dockerfile.amazinghand.cpu \
    --build-arg BASE_IMAGE="${BASE_IMAGE_MIRROR}" \
    --build-arg PIP_INDEX="${PIP_INDEX}" \
    --build-arg TORCH_INDEX="${TORCH_INDEX_CPU}" \
    -t lerobot-amazinghand:cpu \
    .
  echo "==> 导出 CPU 版 ..."
  docker save -o "${DIST_DIR}/lerobot-amazinghand-cpu.tar" lerobot-amazinghand:cpu
  ls -lh "${DIST_DIR}/lerobot-amazinghand-cpu.tar"
}

build_cuda() {
  echo "==> 构建 CUDA 版镜像 ..."
  docker build \
    -f docker/Dockerfile.amazinghand.cuda \
    --build-arg BASE_IMAGE="${BASE_IMAGE_MIRROR}" \
    --build-arg PIP_INDEX="${PIP_INDEX}" \
    --build-arg TORCH_INDEX="${TORCH_INDEX_CUDA}" \
    -t lerobot-amazinghand:cuda \
    .
  echo "==> 导出 CUDA 版 ..."
  docker save -o "${DIST_DIR}/lerobot-amazinghand-cuda.tar" lerobot-amazinghand:cuda
  ls -lh "${DIST_DIR}/lerobot-amazinghand-cuda.tar"
}

case "${TARGET}" in
  cpu)  build_cpu ;;
  cuda) build_cuda ;;
  both) build_cpu; build_cuda ;;
  *) echo "用法: bash docker/build_and_export.sh [cpu|cuda|both]"; exit 1 ;;
esac

echo
echo "完成。镜像已导出到 ${DIST_DIR}/"
echo "客户侧执行: docker load -i <tar 文件>"
