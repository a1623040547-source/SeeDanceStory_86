#!/usr/bin/env python3
"""
将 section04/refs 下的多张参考图（3 张人物 + 1 张环境）合成为一张 2x2 图，
供 Seedance API 仅传 1 张图时使用。

⚠️ 重要：合成图的组成与用途
- 组成：2x2 拼图，[人物1, 人物2] / [人物3, 环境]，为多张参考的拼接，并非单一场景画面。
- 用途：仅作「参考图」——供 Seedance 理解画风、角色形象与场景氛围；模型据此生成与提示词相符的**新画面**作为视频内容。
- 不能直接用作首帧：此图不是视频的第一帧，也不能当作段 2 的 V2V 输入。段 2 及之后必须使用「段 1 生成视频的最后一帧」截取的尾帧图作衔接。

用法（在项目根目录）:
  python scripts/composite_refs.py
  python scripts/composite_refs.py --section section04 --output section04/refs/section04_ref_composite.jpg
"""

import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    print("请安装 Pillow: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def find_images(refs_dir: str, characters_dir: str, scenes_dir: str):
    """返回 (characters 下最多 3 张的路径列表, scenes 下 1 张路径)。"""
    char_dir = os.path.join(refs_dir, characters_dir)
    scene_dir = os.path.join(refs_dir, scenes_dir)
    exts = (".png", ".jpg", ".jpeg")
    char_paths = []
    if os.path.isdir(char_dir):
        for f in sorted(os.listdir(char_dir)):
            if f.lower().endswith(exts):
                char_paths.append(os.path.join(char_dir, f))
                if len(char_paths) >= 3:
                    break
    scene_path = None
    if os.path.isdir(scene_dir):
        for f in sorted(os.listdir(scene_dir)):
            if f.lower().endswith(exts):
                scene_path = os.path.join(scene_dir, f)
                break
    return char_paths, scene_path


def composite_2x2(image_paths: list, cell_size: int = 512, output_path: str = "composite.png"):
    """将 4 张图排成 2x2，每格 cell_size x cell_size，总图 2*cell_size。"""
    if len(image_paths) != 4:
        raise ValueError(f"需要恰好 4 张图，当前 {len(image_paths)} 张")
    total = 2 * cell_size
    out = Image.new("RGB", (total, total), (255, 255, 255))
    for i, path in enumerate(image_paths):
        row, col = i // 2, i % 2
        with Image.open(path) as im:
            im = im.convert("RGB")
            im = im.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
            out.paste(im, (col * cell_size, row * cell_size))
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    out.save(output_path, "JPEG", quality=90)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="将 refs 下 4 张图合成为 1 张 2x2")
    parser.add_argument("--section", type=str, default="section04")
    parser.add_argument("--refs", type=str, default=None, help="refs 目录，默认 <section>/refs")
    parser.add_argument("--output", type=str, default=None, help="输出路径，默认 <section>/refs/<section>_ref_composite.jpg")
    parser.add_argument("--cell-size", type=int, default=512)
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    refs_dir = args.refs or os.path.join(project_root, args.section, "refs")
    output_path = args.output or os.path.join(refs_dir, f"{args.section}_ref_composite.jpg")

    char_paths, scene_path = find_images(refs_dir, "characters", "scenes")
    if not scene_path:
        print("错误: refs/scenes 下未找到任意一张图片。", file=sys.stderr)
        sys.exit(1)
    # 顺序: 3 张人物 + 1 张环境 → 2x2 为 [char0, char1] [char2, scene]
    image_paths = char_paths + [scene_path]
    if len(image_paths) < 4:
        # 若人物不足 3 张，用场景图补足（重复场景）
        while len(image_paths) < 4:
            image_paths.append(scene_path)
        image_paths = image_paths[:4]

    composite_2x2(image_paths, cell_size=args.cell_size, output_path=output_path)
    print("已合成:", output_path)
    return output_path


if __name__ == "__main__":
    main()
