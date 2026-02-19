#!/usr/bin/env python3
"""
Prepare a transition folder between two adjacent phases: copy tail frame from
phase N, extract first frame from phase N+1, and write a Seedance prompt template.
Transition video duration default 2s (1-3s acceptable); user generates in Seedance
and saves as transition_<from>_<to>.mp4 in this folder.
Requires: ffmpeg on PATH (for first-frame extraction).
"""

import argparse
import os
import shutil
import subprocess
import sys


def get_project_root(args) -> str:
    root = os.path.abspath(args.project_root or os.getcwd())
    if not os.path.isdir(root):
        print(f"Error: project root not found: {root}", file=sys.stderr)
        sys.exit(1)
    return root


def phase_dir(project_root: str, section: str, phase_num: int) -> str:
    return os.path.join(project_root, section, "phases", f"phase{phase_num:02d}")


def phase_video_path(project_root: str, section: str, phase_num: int) -> str:
    name = f"phase{phase_num:02d}"
    return os.path.join(project_root, section, "phases", name, f"{name}.mp4")


def tail_frame_path(project_root: str, section: str, phase_num: int) -> str:
    return os.path.join(
        phase_dir(project_root, section, phase_num),
        f"{section}_tail_{phase_num:02d}.png",
    )


def extract_first_frame_ffmpeg(video_path: str, out_path: str) -> bool:
    """Extract the first frame of the video."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", video_path,
                "-vframes", "1", "-q:v", "2", out_path,
            ],
            check=True,
            capture_output=True,
        )
        return os.path.isfile(out_path)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Prepare transition folder between two adjacent phases (tail + first frame + prompt template)."
    )
    ap.add_argument("--section", type=str, required=True, help="Section name, e.g. section03")
    ap.add_argument("--from", dest="from_num", type=int, required=True, help="First phase number (e.g. 2)")
    ap.add_argument("--to", dest="to_num", type=int, required=True, help="Second phase number (must be from + 1, e.g. 3)")
    ap.add_argument("--duration", type=int, default=2, help="Transition duration in seconds for prompt template (default 2, use 1-3)")
    ap.add_argument("--project-root", type=str, default=None, help="Project root (default: cwd)")
    args = ap.parse_args()

    if args.to_num != args.from_num + 1:
        print("Error: --to must be --from + 1 (adjacent phases only)", file=sys.stderr)
        sys.exit(1)
    if not 1 <= args.duration <= 3:
        print("Warning: --duration typically 1-3 seconds", file=sys.stderr)

    project_root = get_project_root(args)
    section = args.section
    from_num, to_num = args.from_num, args.to_num

    trans_name = f"transition_{from_num:02d}_{to_num:02d}"
    trans_dir = os.path.join(project_root, section, "phases", trans_name)
    os.makedirs(trans_dir, exist_ok=True)

    tail_src = tail_frame_path(project_root, section, from_num)
    tail_dst = os.path.join(trans_dir, "tail.png")
    if not os.path.isfile(tail_src):
        print(f"Error: tail frame not found: {tail_src}", file=sys.stderr)
        sys.exit(1)
    shutil.copy2(tail_src, tail_dst)
    print(f"Copied tail frame: {tail_dst}")

    video_next = phase_video_path(project_root, section, to_num)
    first_dst = os.path.join(trans_dir, "first.png")
    if not os.path.isfile(video_next):
        print(f"Error: next phase video not found: {video_next}", file=sys.stderr)
        sys.exit(1)
    if not extract_first_frame_ffmpeg(video_next, first_dst):
        print("Error: ffmpeg failed to extract first frame; ensure ffmpeg is on PATH", file=sys.stderr)
        sys.exit(1)
    print(f"Extracted first frame: {first_dst}")

    prompt_path = os.path.join(trans_dir, f"{trans_name}.txt")
    prompt_content = f"""# Seedance 过渡片段提示词（{args.duration} 秒）

【用途】phase{from_num:02d} 与 phase{to_num:02d} 之间的补差过渡，使衔接更平滑。

【素材】
- 首图（起点）：本文件夹 tail.png（即 phase{from_num:02d} 尾帧）
- 尾图/目标（终点）：本文件夹 first.png（即 phase{to_num:02d} 首帧）

【时长】约 {args.duration} 秒。

【提示词方向】从当前画面自然、连贯地过渡到下一镜画面，保持人物与场景一致，避免跳跃。可强调细微动作或镜头缓动。

生成后将视频命名为 {trans_name}.mp4 放入本文件夹，再使用合并脚本：
  python3 .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode phase-test --section {section} --from {from_num} --to {to_num} --with-transition
"""
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_content)
    print(f"Wrote prompt template: {prompt_path}")
    print(f"Ready. Generate transition in Seedance (~{args.duration}s), save as {trans_name}.mp4 in: {trans_dir}")
    if os.path.isfile(os.path.join(trans_dir, f"{trans_name}.mp4")):
        print("(Transition video already present; merge with --with-transition will include it.)")


if __name__ == "__main__":
    main()
