#!/usr/bin/env python3
"""
Generate a ≤1s cross-section transition: last frame of section1 last phase
fades out, then first frame of section2 first phase fades in (light reveal).
Uses only ffmpeg; no Seedance. Output: transition_s01_s02/transition_s01_s02.mp4.
Requires: ffmpeg on PATH.
"""

import argparse
import os
import shutil
import subprocess
import sys
from typing import Optional, Tuple


def get_project_root(args) -> str:
    root = os.path.abspath(args.project_root or os.getcwd())
    if not os.path.isdir(root):
        print(f"Error: project root not found: {root}", file=sys.stderr)
        sys.exit(1)
    return root


def phase_video_path(project_root: str, section: str, phase_num: int) -> str:
    name = f"phase{phase_num:02d}"
    return os.path.join(project_root, section, "phases", name, f"{name}.mp4")


def tail_frame_candidate(project_root: str, section: str, phase_num: int) -> str:
    """Existing tail frame e.g. section01_tail_08.png in phase folder."""
    name = f"phase{phase_num:02d}"
    return os.path.join(
        project_root, section, "phases", name,
        f"{section}_tail_{phase_num:02d}.png",
    )


def extract_last_frame_ffmpeg(video_path: str, out_path: str) -> bool:
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-sseof", "-0.04", "-i", video_path,
                "-vframes", "1", "-q:v", "2", out_path,
            ],
            check=True,
            capture_output=True,
        )
        return os.path.isfile(out_path)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def extract_first_frame_ffmpeg(video_path: str, out_path: str) -> bool:
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


def get_video_size(path: str) -> Optional[Tuple[int, int]]:
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height", "-of", "csv=p=0:nokey=1",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode != 0 or not r.stdout:
            return None
        w, h = r.stdout.strip().split(",")
        return int(w), int(h)
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        return None


def make_transition(
    project_root: str,
    section1: str,
    phase1: int,
    section2: str,
    phase2: int,
    duration: float = 1.0,
) -> Optional[str]:
    """
    Generate transition video: tail fade out + first frame fade in.
    - Cross-section (section1 != section2): story_dir/transition_s01_s02/transition_s01_s02.mp4
    - Same-section phase-to-phase (section1 == section2): section/phases/transition_XX_YY/transition_XX_YY.mp4
    Returns path to the generated mp4, or None on failure.
    """
    same_section = section1 == section2
    if same_section:
        trans_name = f"transition_{phase1:02d}_{phase2:02d}"
        trans_dir = os.path.join(project_root, section1, "phases", trans_name)
    else:
        story_dir = os.path.dirname(os.path.join(project_root, section1))
        trans_name = "transition_s01_s02"
        trans_dir = os.path.join(story_dir, trans_name)
    os.makedirs(trans_dir, exist_ok=True)

    video1 = phase_video_path(project_root, section1, phase1)
    video2 = phase_video_path(project_root, section2, phase2)
    if not os.path.isfile(video1):
        print(f"Error: video not found: {video1}", file=sys.stderr)
        return None
    if not os.path.isfile(video2):
        print(f"Error: video not found: {video2}", file=sys.stderr)
        return None

    target_size = get_video_size(video1)
    if not target_size:
        print("Error: could not get video size", file=sys.stderr)
        return None
    w, h = target_size

    tail_png = os.path.join(trans_dir, "tail.png")
    first_png = os.path.join(trans_dir, "first.png")
    # Prefer existing tail frame (e.g. section01_tail_08.png)
    existing_tail = tail_frame_candidate(project_root, section1, phase1)
    if os.path.isfile(existing_tail):
        shutil.copy2(existing_tail, tail_png)
    else:
        if not extract_last_frame_ffmpeg(video1, tail_png):
            print("Error: failed to extract last frame from section1 phase", file=sys.stderr)
            return None
    if not extract_first_frame_ffmpeg(video2, first_png):
        print("Error: failed to extract first frame from section2 phase", file=sys.stderr)
        return None

    # Transition: first half tail fades out, second half first fades in (light reveal). Total duration.
    half = duration / 2.0
    # Fade out last 40% of first half; fade in first 40% of second half
    fade_out_duration = half * 0.4
    fade_out_start = half - fade_out_duration
    fade_in_duration = half * 0.4

    out_mp4 = os.path.join(trans_dir, f"{trans_name}.mp4")
    # [0:v] tail: loop for half sec, scale, fade out at end
    # [1:v] first: loop for half sec, scale, fade in at start
    # [2:a] anullsrc: silent audio for same duration so merge keeps audio from adjacent clips
    filter_parts = [
        f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
        f"fade=out:st={fade_out_start:.3f}:d={fade_out_duration:.3f}[v0]",
        f"[1:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
        f"fade=in:st=0:d={fade_in_duration:.3f}[v1]",
        "[v0][v1]concat=n=2:v=1:a=0[outv]",
    ]
    filter_complex = ";".join(filter_parts)
    # anullsrc -t duration: silent audio so merged output keeps audio from adjacent clips
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(half), "-i", tail_png,
        "-loop", "1", "-t", str(half), "-i", first_png,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-t", str(duration),
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "2:a",
        "-r", "25", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        out_mp4,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return out_mp4 if os.path.isfile(out_mp4) else None
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(e.stderr.decode(), file=sys.stderr)
        return None
    except FileNotFoundError:
        print("Error: ffmpeg not found", file=sys.stderr)
        return None


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate ≤1s cross-section transition (tail fade out + first frame fade in).",
    )
    ap.add_argument("--project-root", type=str, default=None, help="Story dir parent (e.g. story/01-海边度假)")
    ap.add_argument("--section1", type=str, required=True, help="e.g. section01")
    ap.add_argument("--phase1", type=int, required=True, help="Last phase of section1 (e.g. 8)")
    ap.add_argument("--section2", type=str, required=True, help="e.g. section02")
    ap.add_argument("--phase2", type=int, required=True, help="First phase of section2 (e.g. 1)")
    ap.add_argument("--duration", type=float, default=1.0, help="Transition duration in seconds (default 1, keep ≤1)")
    args = ap.parse_args()

    project_root = get_project_root(args)
    out = make_transition(
        project_root,
        args.section1,
        args.phase1,
        args.section2,
        args.phase2,
        duration=args.duration,
    )
    if out:
        print(f"Cross-section transition: {out}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
