---
name: image-compression
description: Compress images (PNG/JPEG) for refs and assets—resize by max dimension, reduce file size. Use when the user asks to compress images, reduce image size, optimize ref/scene/character images, or prepare assets for upload.
---

# 图片压缩

用于压缩项目中的参照图、场景图、角色图等，在保证可用画质的前提下减小文件体积。

## 使用脚本

依赖：`pip install Pillow`

```bash
# 压缩单张图，输出到指定路径（不写则覆盖原图）
python .cursor/skills/image-compression/scripts/compress_image.py <输入路径> [输出路径]

# 常用参数
python .cursor/skills/image-compression/scripts/compress_image.py input.png output.png --max-size 1920 --quality 88
```

| 参数 | 说明 | 默认 |
|------|------|------|
| `--max-size N` | 长边最大像素（保持比例） | 2048 |
| `--quality N` | JPEG 质量 1–100（仅影响 JPEG 或 PNG→JPEG） | 88 |
| `--format png\|jpeg` | 输出格式；不指定则按输出扩展名 | 按输出文件扩展名 |

## 典型场景

- **场景图/环境图**：`--max-size 1920`，保留 PNG 或转 JPEG 均可。
- **角色参照图**：`--max-size 1920`，保持 PNG 以保留透明或细节。
- **仅缩小体积**：不改尺寸时设 `--max-size 4096`（或大于原图），仅做优化/重编码。

## 执行流程

1. 确认输入路径存在且为图片。
2. 若指定了输出路径，则输出到该路径；否则覆盖原图（建议先备份）。
3. 按 `--max-size` 等比例缩放，再按格式与 `--quality` 保存。
4. 脚本打印压缩前后文件大小。
