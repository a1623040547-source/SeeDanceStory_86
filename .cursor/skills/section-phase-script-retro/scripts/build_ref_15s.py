#!/usr/bin/env python3
"""
全能参考：拆成两个独立视频——一个 7s（环境/风格）、一个 8s（连续性），分别上传使用，不拼接。
- 7s：从 section 第一段（phase01）视频截取前 7 秒 -> ref_env_7s.mp4
- 8s：从最新 phase 视频截取后 8 秒 -> ref_continuity_8s.mp4
若仅第一段有视频，则 7s 与 8s 均从该段截取。
依赖：ffmpeg。
用法：python build_ref_15s.py --section section03 [--project-root /path]
"""

import argparse
import os
import subprocess
import sys
from typing import Optional, Tuple

# 脚本所在 skill 的 scripts/ -> section-phase-script-retro/
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 项目根：section-phase-script-retro -> skills -> .cursor -> 项目根
DEFAULT_ROOT = os.path.normpath(os.path.join(SKILL_DIR, "..", "..", ".."))

FIRST_SEC = 7
LAST_SEC = 8
OUT_ENV = "ref_env_7s.mp4"
OUT_CONTINUITY = "ref_continuity_8s.mp4"


def phase_video_path(project_root: str, section: str, phase_num: int) -> str:
    name = f"phase{phase_num:02d}"
    return os.path.join(project_root, section, "phases", name, f"{name}.mp4")


def find_phase_range(project_root: str, section: str) -> Tuple[Optional[int], Optional[int]]:
    """返回 (有视频的最小 phase 号, 有视频的最大 phase 号)，从 1 到 12 扫描。"""
    first, last = None, None
    for n in range(1, 13):
        p = phase_video_path(project_root, section, n)
        if os.path.isfile(p):
            if first is None:
                first = n
            last = n
    return first, last


def run_ffmpeg(args: list[str], check: bool = True) -> bool:
    try:
        r = subprocess.run(
            ["ffmpeg", "-y"] + args,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if check and r.returncode != 0:
            print(r.stderr or r.stdout or "ffmpeg failed", file=sys.stderr)
            return False
        return True
    except FileNotFoundError:
        print("错误：未找到 ffmpeg，请先安装并加入 PATH", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("错误：ffmpeg 执行超时", file=sys.stderr)
        return False


def main() -> None:
    ap = argparse.ArgumentParser(
        description="全能参考：拆成两个独立视频（7s 环境 + 8s 连续性），不拼接",
    )
    ap.add_argument("--section", required=True, help="Section 名，如 section03")
    ap.add_argument("--project-root", type=str, default=DEFAULT_ROOT, help="项目根目录")
    args = ap.parse_args()

    root = os.path.abspath(args.project_root)
    if not os.path.isdir(root):
        print(f"错误：项目根不存在 {root}", file=sys.stderr)
        sys.exit(1)

    section = args.section
    phases_dir = os.path.join(root, section, "phases")
    if not os.path.isdir(phases_dir):
        print(f"错误：phases 目录不存在 {phases_dir}", file=sys.stderr)
        sys.exit(1)

    first_phase, last_phase = find_phase_range(root, section)
    if first_phase is None or last_phase is None:
        print(f"错误：{section}/phases 下未找到任一 phaseNN/phaseNN.mp4", file=sys.stderr)
        sys.exit(1)

    first_video = phase_video_path(root, section, first_phase)
    last_video = phase_video_path(root, section, last_phase)
    if first_phase == last_phase:
        print(f"[1] 仅 phase{first_phase:02d} 有视频，从中截取 7s（环境）与 8s（连续性）")
    else:
        print(f"[1] 7s 来源：phase{first_phase:02d}；8s 来源：phase{last_phase:02d}")

    for p in (first_video, last_video):
        if not os.path.isfile(p):
            print(f"错误：视频不存在 {p}", file=sys.stderr)
            sys.exit(1)

    out_7s = os.path.join(phases_dir, OUT_ENV)
    out_8s = os.path.join(phases_dir, OUT_CONTINUITY)

    # 截取前 7s -> ref_env_7s.mp4
    if not run_ffmpeg(["-i", first_video, "-t", str(FIRST_SEC), "-c", "copy", out_7s]):
        sys.exit(1)
    print(f"[2] 已生成 7s 环境参考：{out_7s}")

    # 截取后 8s -> ref_continuity_8s.mp4
    if not run_ffmpeg(["-sseof", f"-{LAST_SEC}", "-i", last_video, "-c", "copy", out_8s]):
        sys.exit(1)
    print(f"[3] 已生成 8s 连续性参考：{out_8s}")

    print("    两个视频分别上传/使用，不要拼成一条。")


if __name__ == "__main__":
    main()
