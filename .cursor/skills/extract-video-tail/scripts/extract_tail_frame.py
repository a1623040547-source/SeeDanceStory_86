#!/usr/bin/env python3
"""
Extract the last frame of a video (tail frame) for V2V continuity.
Must be the very last frame to ensure seamless continuity with the next segment.
Saves to the same directory as the video, e.g. section02_tail_01.png.
Requires: opencv-python (pip install opencv-python) OR ffmpeg on PATH.
"""

import argparse
import os
import re
import subprocess
import sys


def segment_from_filename(path: str) -> int:
    """Infer segment number from path like phase01.mp4 or phases/phase03/phase03.mp4."""
    name = os.path.basename(path).lower()
    m = re.search(r"phase(\d+)", name)
    return int(m.group(1)) if m else 1


def extract_last_frame_ffmpeg(video_path: str, out_path: str) -> bool:
    """Extract the very last frame: seek to 0.04s before end of file."""
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


def extract_tail_frame(
    video_path: str,
    segment: int,
    section: str = "section02",
) -> str:
    if not os.path.isfile(video_path):
        print(f"Error: file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(os.path.abspath(video_path))
    out_name = f"{section}_tail_{segment:02d}.png"
    out_path = os.path.join(out_dir, out_name)

    try:
        import cv2
    except ImportError:
        cv2 = None

    if cv2 is not None:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: could not open video: {video_path}", file=sys.stderr)
            sys.exit(1)
        last_frame = None
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break
            last_frame = frame
        cap.release()
        if last_frame is None:
            print("Error: could not read any frame", file=sys.stderr)
            sys.exit(1)
        cv2.imwrite(out_path, last_frame)
    else:
        if not extract_last_frame_ffmpeg(video_path, out_path):
            print("Error: need opencv-python (pip install opencv-python) or ffmpeg on PATH", file=sys.stderr)
            sys.exit(1)

    print(f"Saved tail frame (last frame): {out_path}")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract tail frame from segment video for V2V.")
    ap.add_argument("video", help="Path to segment video (e.g. phase01/phase01.mp4)")
    ap.add_argument("--segment", type=int, default=None, help="Segment number 1-11 (default: from filename)")
    ap.add_argument("--section", type=str, default="section02", help="Output prefix, e.g. section02 -> section02_tail_01.png")
    args = ap.parse_args()

    segment = args.segment if args.segment is not None else segment_from_filename(args.video)
    if segment < 1 or segment > 11:
        print("Warning: segment should be 1-11 (tail frame is for next segment)", file=sys.stderr)

    extract_tail_frame(args.video, segment=segment, section=args.section)


if __name__ == "__main__":
    main()
