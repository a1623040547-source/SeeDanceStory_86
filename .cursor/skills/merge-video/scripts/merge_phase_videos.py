#!/usr/bin/env python3
"""
Merge phase videos for phase-test (two adjacent phases) or section-test (all phases).
Uses ffmpeg concat filter with re-encode so duration and playback are correct
(concat demuxer + -c copy can produce wrong duration / stuck frame when timebases differ).
Requires: ffmpeg on PATH.
"""

import argparse
import os
import subprocess
import sys


def get_project_root(args) -> str:
    root = os.path.abspath(args.project_root or os.getcwd())
    if not os.path.isdir(root):
        print(f"Error: project root not found: {root}", file=sys.stderr)
        sys.exit(1)
    return root


def phase_video_path(project_root: str, section: str, phase_num: int) -> str:
    name = f"phase{phase_num:02d}"
    return os.path.join(project_root, section, "phases", name, f"{name}.mp4")


def _has_audio(path: str) -> bool:
    """Return True if the file has at least one audio stream."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index", "-of", "csv=p=0", path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return r.returncode == 0 and (r.stdout or "").strip() != ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_ffmpeg_concat(project_root: str, video_paths: list[str], out_path: str) -> bool:
    """Concat using filter + re-encode; include audio when all inputs have audio."""
    if not video_paths:
        print("Error: no video files to merge", file=sys.stderr)
        return False
    for p in video_paths:
        if not os.path.isfile(p):
            print(f"Error: video not found: {p}", file=sys.stderr)
            return False

    n = len(video_paths)
    with_audio = all(_has_audio(p) for p in video_paths)

    cmd = ["ffmpeg", "-y"]
    for p in video_paths:
        cmd.extend(["-i", os.path.abspath(p)])

    if with_audio:
        # [0:v][0:a][1:v][1:a]...concat=n=N:v=1:a=1[outv][outa]
        in_parts = "".join(f"[{i}:v][{i}:a]" for i in range(n))
        filter_complex = f"{in_parts}concat=n={n}:v=1:a=1[outv][outa]"
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            out_path,
        ])
    else:
        in_parts = "".join(f"[{i}:v]" for i in range(n))
        filter_complex = f"{in_parts}concat=n={n}:v=1:a=0[outv]"
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-an", out_path,
        ])

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return os.path.isfile(out_path)
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(f"Error: ffmpeg failed: {e.stderr.decode()}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install ffmpeg and ensure it is on PATH.", file=sys.stderr)
        return False


def mode_phase_test(project_root: str, section: str, from_num: int, to_num: int) -> None:
    if to_num != from_num + 1:
        print("Error: phase-test requires two adjacent phases (--to must be --from + 1)", file=sys.stderr)
        sys.exit(1)
    p1 = phase_video_path(project_root, section, from_num)
    p2 = phase_video_path(project_root, section, to_num)
    out_name = f"phase_test_{from_num:02d}_{to_num:02d}.mp4"
    out_dir = os.path.join(project_root, section, "phases")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, out_name)
    if run_ffmpeg_concat(project_root, [p1, p2], out_path):
        print(f"Phase-test merged: {out_path}")
    else:
        sys.exit(1)


def mode_section_test(project_root: str, section: str) -> None:
    section_dir = os.path.join(project_root, section)
    if not os.path.isdir(section_dir):
        print(f"Error: section directory not found: {section_dir}", file=sys.stderr)
        sys.exit(1)
    phases_dir = os.path.join(section_dir, "phases")
    if not os.path.isdir(phases_dir):
        print(f"Error: phases directory not found: {phases_dir}", file=sys.stderr)
        sys.exit(1)

    video_paths = []
    for n in range(1, 20):
        path = phase_video_path(project_root, section, n)
        if os.path.isfile(path):
            video_paths.append(path)
        elif n > 1:
            break
    if not video_paths:
        print("Error: no phase videos found (phase01/phase01.mp4, ...)", file=sys.stderr)
        sys.exit(1)

    out_name = f"{section}_merged.mp4"
    out_path = os.path.join(section_dir, out_name)
    if run_ffmpeg_concat(project_root, video_paths, out_path):
        print(f"Section-test merged ({len(video_paths)} phases): {out_path}")
    else:
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge phase videos (phase-test or section-test).")
    ap.add_argument("--mode", choices=["phase-test", "section-test"], required=True, help="phase-test: two adjacent phases; section-test: all phases in section")
    ap.add_argument("--section", type=str, required=True, help="Section name, e.g. section02")
    ap.add_argument("--from", dest="from_num", type=int, default=None, help="First phase number for phase-test (e.g. 11)")
    ap.add_argument("--to", dest="to_num", type=int, default=None, help="Second phase number (must be --from + 1) for phase-test (e.g. 12)")
    ap.add_argument("--project-root", type=str, default=None, help="Project root (default: cwd)")
    args = ap.parse_args()

    project_root = get_project_root(args)

    if args.mode == "phase-test":
        if args.from_num is None or args.to_num is None:
            print("Error: phase-test requires --from and --to", file=sys.stderr)
            sys.exit(1)
        mode_phase_test(project_root, args.section, args.from_num, args.to_num)
    else:
        mode_section_test(project_root, args.section)


if __name__ == "__main__":
    main()
