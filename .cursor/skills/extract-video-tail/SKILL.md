---
name: extract-video-tail
description: Extracts the last frame of a segment video (tail frame) for V2V continuity and saves it to the segment folder. Use when the user has generated a phase video and needs to extract the very last frame (e.g. section02_tail_01.png) for the next segment, or when organizing Seedance segment outputs.
---

# 提取视频尾帧

从已生成的段视频中截取**最后一帧**（必须是视频的最后一帧，以保证与下一段生成的连贯性），保存为下一段 V2V 使用的参考图（如 `section02_tail_01.png`），并放入该段对应文件夹。

## 使用脚本

依赖：`pip install opencv-python`

```bash
# 从段 1 视频提取尾帧，输出到视频所在文件夹，命名为 section02_tail_01.png
python .cursor/skills/extract-video-tail/scripts/extract_tail_frame.py <视频路径> [--segment 1] [--section section02]

# 示例：对 phase01 文件夹内的 phase01.mp4 提取尾帧
python .cursor/skills/extract-video-tail/scripts/extract_tail_frame.py section02/phases/phase01/phase01.mp4 --segment 1 --section section02
```

| 参数 | 说明 | 默认 |
|------|------|------|
| `--segment N` | 段号 1～11（尾帧供下一段用，段 12 无需尾帧） | 从文件名推断（phase01.mp4→1） |
| `--section NAME` | 输出文件名前缀，如 section02 → section02_tail_01.png | section02 |

输出文件保存在**视频所在目录**，文件名：`{section}_tail_{segment:02d}.png`。

## 与 phase 文件夹的对应关系

- 每段一个文件夹：`phases/phase01/` 内含 `phase01.txt`、`phase01.mp4`。
- 段 1 生成后运行脚本，尾帧保存为 `phases/phase01/section02_tail_01.png`，供段 2 上传使用。
