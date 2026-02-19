#!/usr/bin/env python3
"""
Phase 视频后期：改名 → 尾帧提取 → 与上一段合并（通用）。
用法：python rename_tail_merge.py --section section03 --phase 5 [--project-root /path] [--no-merge]
"""

import argparse
import os
import subprocess
import sys

# 脚本所在 skill 的根：scripts/ -> phase-video-post/
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 项目根：phase-video-post -> skills -> .cursor -> 项目根
DEFAULT_ROOT = os.path.normpath(os.path.join(SKILL_DIR, "..", "..", ".."))


def phase_dir(project_root: str, section: str, phase_num: int) -> str:
    name = f"phase{phase_num:02d}"
    return os.path.join(project_root, section, "phases", name)


def step1_rename(project_root: str, section: str, phase_num: int) -> bool:
    """将 phase 下唯一的 .mp4 改名为 phaseNN.mp4"""
    d = phase_dir(project_root, section, phase_num)
    target = os.path.join(d, f"phase{phase_num:02d}.mp4")
    if not os.path.isdir(d):
        print(f"[1] 错误：目录不存在 {d}", file=sys.stderr)
        return False
    if os.path.isfile(target):
        print("[1] 已是 phase{:02d}.mp4，跳过重命名".format(phase_num))
        return True
    mp4s = [f for f in os.listdir(d) if f.lower().endswith(".mp4")]
    if not mp4s:
        print(f"[1] 错误：{d} 下没有 .mp4 文件", file=sys.stderr)
        return False
    if len(mp4s) > 1:
        print(f"[1] 错误：{d} 下有多个 .mp4，请手动保留一个并命名为 phase{phase_num:02d}.mp4", file=sys.stderr)
        return False
    src = os.path.join(d, mp4s[0])
    os.rename(src, target)
    print(f"[1] 已重命名: {mp4s[0]} -> phase{phase_num:02d}.mp4")
    return True


def step2_tail(project_root: str, section: str, phase_num: int) -> bool:
    """从 phaseNN.mp4 提取尾帧 -> {section}_tail_NN.png"""
    video_path = os.path.join(phase_dir(project_root, section, phase_num), f"phase{phase_num:02d}.mp4")
    if not os.path.isfile(video_path):
        print(f"[2] 错误：视频不存在 {video_path}", file=sys.stderr)
        return False
    script = os.path.join(project_root, ".cursor", "skills", "extract-video-tail", "scripts", "extract_tail_frame.py")
    if not os.path.isfile(script):
        print("[2] 错误：未找到 extract_tail_frame.py", file=sys.stderr)
        return False
    r = subprocess.run(
        [
            sys.executable,
            script,
            video_path,
            "--segment",
            str(phase_num),
            "--section",
            section,
        ],
        cwd=project_root,
    )
    if r.returncode != 0:
        print("[2] 尾帧提取失败", file=sys.stderr)
        return False
    print(f"[2] 尾帧已保存: {section}/phases/phase{phase_num:02d}/{section}_tail_{phase_num:02d}.png")
    return True


def step3_merge(project_root: str, section: str, phase_num: int) -> bool:
    """合并 phase(N-1) + phase(N) -> phase_test_(N-1)_N.mp4"""
    if phase_num < 2:
        print("[3] phase 1 无上一段，跳过合并")
        return True
    merge_script = os.path.join(project_root, ".cursor", "skills", "merge-video", "scripts", "merge_phase_videos.py")
    if not os.path.isfile(merge_script):
        print("[3] 错误：未找到 merge_phase_videos.py", file=sys.stderr)
        return False
    r = subprocess.run(
        [
            sys.executable,
            merge_script,
            "--mode", "phase-test",
            "--section", section,
            "--from", str(phase_num - 1),
            "--to", str(phase_num),
            "--project-root", project_root,
        ],
        cwd=project_root,
    )
    if r.returncode != 0:
        print("[3] 合并失败（请确认上一段 phase{:02d}.mp4 存在）".format(phase_num - 1), file=sys.stderr)
        return False
    print(f"[3] 已合并: {section}/phases/phase_test_{phase_num-1:02d}_{phase_num:02d}.mp4")
    return True


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Phase 视频后期：改名 → 尾帧 → 与上一段合并",
    )
    ap.add_argument("--section", required=True, help="Section 名，如 section03")
    ap.add_argument("--phase", type=int, required=True, help="段号 1～12（刚生成视频的那一段）")
    ap.add_argument("--project-root", type=str, default=DEFAULT_ROOT, help="项目根目录")
    ap.add_argument("--no-merge", action="store_true", help="只做改名和尾帧，不合并")
    args = ap.parse_args()

    root = os.path.abspath(args.project_root)
    if not os.path.isdir(root):
        print(f"错误：项目根不存在 {root}", file=sys.stderr)
        sys.exit(1)
    if args.phase < 1 or args.phase > 12:
        print("警告：--phase 建议 1～12", file=sys.stderr)

    print(f"Section {args.section} phase {args.phase}：改名 → 尾帧 → 合并\n")
    if not step1_rename(root, args.section, args.phase):
        sys.exit(1)
    if not step2_tail(root, args.section, args.phase):
        sys.exit(1)
    if not args.no_merge and not step3_merge(root, args.section, args.phase):
        sys.exit(1)
    print("\n全部完成。")


if __name__ == "__main__":
    main()
