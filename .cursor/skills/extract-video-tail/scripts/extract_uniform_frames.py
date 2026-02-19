#!/usr/bin/env python3
"""
从视频中均匀截取 N 帧（不含尾帧），保存到指定文件夹。
用于 phase 截图归档、参考等。默认 6 帧，输出到视频所在目录下的 frames/ 子目录。
Requires: opencv-python (pip install opencv-python).
"""

import argparse
import os
import sys
from typing import List, Optional


def get_frame_count_and_extract(
    video_path: str,
    num_frames: int = 6,
    out_dir: Optional[str] = None,
) -> List[str]:
    """从 video_path 均匀截取 num_frames 帧（不含最后一帧），保存到 out_dir，返回保存路径列表。"""
    try:
        import cv2
    except ImportError:
        print("Error: need opencv-python (pip install opencv-python)", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(video_path):
        print(f"Error: file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(video_path)), "frames")
    os.makedirs(out_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: could not open video: {video_path}", file=sys.stderr)
        sys.exit(1)

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < 2:
        print("Error: video has too few frames to extract 6 (excluding tail)", file=sys.stderr)
        cap.release()
        sys.exit(1)

    # 6 帧均匀分布在 [0, total-2]（不含尾帧 total-1）
    # 索引: 0, (total-2)*1/5, (total-2)*2/5, (total-2)*3/5, (total-2)*4/5, (total-2)
    indices = []
    if num_frames == 1:
        indices = [0]
    else:
        step = (total - 2) / (num_frames - 1)
        indices = [int(round(step * k)) for k in range(num_frames)]
        indices[-1] = total - 2  # 确保最后一帧索引不包含尾帧

    saved = []
    for i, idx in enumerate(indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        out_name = f"frame_{i+1:02d}.png"
        out_path = os.path.join(out_dir, out_name)
        cv2.imwrite(out_path, frame)
        saved.append(out_path)
    cap.release()

    for p in saved:
        print(f"Saved: {p}")
    return saved


def main() -> None:
    ap = argparse.ArgumentParser(
        description="从视频均匀截取 N 帧（不含尾帧），保存到 phase 下的 frames/ 文件夹",
    )
    ap.add_argument("video", help="视频路径，如 phase01/phase01.mp4")
    ap.add_argument("-n", "--num-frames", type=int, default=6, help="截取帧数（默认 6）")
    ap.add_argument("-o", "--output-dir", type=str, default=None, help="输出目录（默认：视频所在目录/frames）")
    args = ap.parse_args()

    if args.num_frames < 1:
        print("Error: --num-frames 至少为 1", file=sys.stderr)
        sys.exit(1)

    get_frame_count_and_extract(
        args.video,
        num_frames=args.num_frames,
        out_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
