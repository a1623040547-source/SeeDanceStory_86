#!/usr/bin/env python3
"""
Compress images for refs/scenes/characters: resize by max dimension, optimize file size.
Requires: pip install Pillow
Usage:
  python compress_image.py <input_path> [output_path] [--max-size 1920] [--quality 88] [--format png|jpeg]
"""

import argparse
import os
import sys
from typing import Optional

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow required. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def get_file_size(path: str) -> int:
    return os.path.getsize(path) if os.path.isfile(path) else 0


def compress_image(
    input_path: str,
    output_path: Optional[str] = None,
    max_size: int = 2048,
    quality: int = 88,
    out_format: Optional[str] = None,
) -> None:
    if not os.path.isfile(input_path):
        print(f"Error: not a file: {input_path}", file=sys.stderr)
        sys.exit(1)

    out_path = output_path or input_path
    if out_format is None:
        ext = os.path.splitext(out_path)[1].lower()
        out_format = "jpeg" if ext in (".jpg", ".jpeg") else "png"

    size_before = get_file_size(input_path)
    img = Image.open(input_path)
    img = img.convert("RGB" if out_format == "jpeg" else "RGBA")

    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    save_kw = {}
    if out_format == "jpeg":
        save_kw["quality"] = quality
        save_kw["optimize"] = True
    else:
        save_kw["optimize"] = True

    img.save(out_path, format=out_format.upper(), **save_kw)
    size_after = get_file_size(out_path)
    print(f"Saved: {out_path}")
    print(f"Size: {size_before / 1024:.1f} KB -> {size_after / 1024:.1f} KB")


def main() -> None:
    ap = argparse.ArgumentParser(description="Compress images for refs/assets.")
    ap.add_argument("input", help="Input image path")
    ap.add_argument("output", nargs="?", default=None, help="Output path (default: overwrite input)")
    ap.add_argument("--max-size", type=int, default=2048, help="Max dimension (default: 2048)")
    ap.add_argument("--quality", type=int, default=88, help="JPEG quality 1-100 (default: 88)")
    ap.add_argument("--format", choices=("png", "jpeg"), default=None, help="Output format (default: from output extension)")
    args = ap.parse_args()

    compress_image(
        args.input,
        output_path=args.output,
        max_size=args.max_size,
        quality=args.quality,
        out_format=args.format,
    )


if __name__ == "__main__":
    main()
