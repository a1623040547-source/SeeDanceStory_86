#!/usr/bin/env python3
"""
第一段视频一键流程：即梦生图（首帧，16:9）→ 首帧 base64 传入即梦图生视频（16:9）。尾帧由本段视频截取，不单独生尾帧图。
用法：
  python scripts/jimeng_volc_phase01.py --project-root . [--no-poll]
"""

import argparse
import os
import subprocess
import sys

REFS_DIR = "section04/refs"
PHASE01_IMG_FIRST = "section04/phases/phase01/phase01_img_first.txt"
PHASE01_VIDEO = "section04/phases/phase01/phase01.txt"
PHASE01_FIRST_FRAME = "section04/phases/phase01/phase01_first_frame.png"


def main():
    parser = argparse.ArgumentParser(description="Phase01 一键：即梦生图(16:9)得首帧 → 图生视频(16:9)")
    parser.add_argument("--project-root", type=str, default=os.getcwd())
    parser.add_argument("--img-prompt-file", type=str, default=PHASE01_IMG_FIRST, help="首帧生图提示词文件")
    parser.add_argument("--phase-prompt-file", type=str, default=PHASE01_VIDEO, help="生视频提示词文件 phase01.txt")
    parser.add_argument("--no-poll", action="store_true", help="视频仅提交不轮询")
    args = parser.parse_args()

    root = os.path.abspath(args.project_root)
    os.chdir(root)

    cmd_img_first = [
        sys.executable,
        "scripts/jimeng_volc_img.py",
        "--prompt-file", args.img_prompt_file,
        "--refs-dir", REFS_DIR,
        "--output", PHASE01_FIRST_FRAME,
        "--project-root", root,
    ]
    print("Step 1: 即梦生图（首帧）...", flush=True)
    r = subprocess.run(cmd_img_first, capture_output=True, text=True, cwd=root)
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        sys.exit(r.returncode)
    base64_str = r.stdout.strip()
    if not base64_str:
        print("生图未返回 base64", file=sys.stderr)
        sys.exit(1)

    cmd_video = [
        sys.executable,
        "scripts/jimeng_volc_generate.py",
        "--prompt-file", args.phase_prompt_file,
        "--image-base64", base64_str,
        "--project-root", root,
    ]
    if args.no_poll:
        cmd_video.append("--no-poll")
    print("Step 2: 即梦图生视频（首帧 base64）...", flush=True)
    subprocess.run(cmd_video, cwd=root)


if __name__ == "__main__":
    main()
