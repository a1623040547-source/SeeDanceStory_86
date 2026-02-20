#!/usr/bin/env python3
"""
Section03 phase05：视频改名 → 尾帧提取 → 与 phase04 合并。
在项目根目录执行：python3 section03/do_phase05_rename_tail_merge.py
依赖：ffmpeg（合并+尾帧），可选 opencv-python（尾帧）
"""

import os
import subprocess
import sys

# 项目根 = 本文件所在目录的上一级
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
PHASE05_DIR = os.path.join(ROOT, "section03", "phases", "phase05")
PHASE05_MP4 = os.path.join(PHASE05_DIR, "phase05.mp4")


def step1_rename():
    """将 phase05 下唯一的 .mp4（即梦长文件名）改名为 phase05.mp4"""
    if os.path.isfile(PHASE05_MP4):
        print("[1] 已是 phase05.mp4，跳过重命名")
        return True
    mp4s = [f for f in os.listdir(PHASE05_DIR) if f.lower().endswith(".mp4")]
    if not mp4s:
        print("[1] 错误：phase05 下没有 .mp4 文件", file=sys.stderr)
        return False
    if len(mp4s) > 1:
        print("[1] 错误：phase05 下有多于一个 .mp4，请手动保留一个并命名为 phase05.mp4", file=sys.stderr)
        return False
    src = os.path.join(PHASE05_DIR, mp4s[0])
    os.rename(src, PHASE05_MP4)
    print(f"[1] 已重命名: {mp4s[0]} -> phase05.mp4")
    return True


def step2_tail():
    """从 phase05.mp4 提取尾帧 -> section03_tail_05.png"""
    script = os.path.join(ROOT, ".cursor", "skills", "extract-video-tail", "scripts", "extract_tail_frame.py")
    if not os.path.isfile(script):
        print("[2] 错误：未找到 extract_tail_frame.py", file=sys.stderr)
        return False
    r = subprocess.run(
        [sys.executable, script, PHASE05_MP4, "--segment", "5", "--section", "section03"],
        cwd=ROOT,
    )
    if r.returncode != 0:
        print("[2] 尾帧提取失败", file=sys.stderr)
        return False
    print("[2] 尾帧已保存: section03/phases/phase05/section03_tail_05.png")
    return True


def step3_merge():
    """合并 phase04 + phase05 -> phase_test_04_05.mp4"""
    merge_script = os.path.join(ROOT, ".cursor", "skills", "merge-video", "scripts", "merge_phase_videos.py")
    if not os.path.isfile(merge_script):
        print("[3] 错误：未找到 merge_phase_videos.py", file=sys.stderr)
        return False
    r = subprocess.run(
        [
            sys.executable, merge_script,
            "--mode", "phase-test",
            "--section", "section03",
            "--from", "4",
            "--to", "5",
            "--project-root", ROOT,
        ],
        cwd=ROOT,
    )
    if r.returncode != 0:
        print("[3] 合并失败（请确认 section03/phases/phase04/phase04.mp4 存在）", file=sys.stderr)
        return False
    print("[3] 已合并: section03/phases/phase_test_04_05.mp4")
    return True


def main():
    print("Section03 phase05：改名 → 尾帧 → 与 phase04 合并\n")
    if not step1_rename():
        sys.exit(1)
    if not step2_tail():
        sys.exit(1)
    if not step3_merge():
        sys.exit(1)
    print("\n全部完成。")


if __name__ == "__main__":
    main()
