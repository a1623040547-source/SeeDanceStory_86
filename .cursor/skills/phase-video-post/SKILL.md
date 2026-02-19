---
name: phase-video-post
description: After generating a phase video in Seedance, run rename → tail frame extraction → merge with previous phase. Use when a new phase has a long-named output (e.g. jimeng-xxx.mp4) and you want to standardize the name, extract the last frame for the next segment, and merge with the previous phase for testing.
---

# Phase 视频后期：改名 → 尾帧 → 与上一段合并

某段（phase）在即梦生成视频后，一次性完成：

1. **改名**：将 phase 文件夹内唯一的 `.mp4`（即梦长文件名）重命名为 `phaseNN.mp4`
2. **尾帧提取**：从该视频截取最后一帧，保存为 `{section}_tail_{N:02d}.png`，供下一段 V2V 使用
3. **合并测试**：与该 section 的上一段（phase N-1）拼接为 `phase_test_(N-1)_N.mp4`

## 使用脚本

脚本位置：`.cursor/skills/phase-video-post/scripts/rename_tail_merge.py`

依赖：**ffmpeg**（尾帧与合并）；可选 **opencv-python**（尾帧备用）。

```bash
# 在项目根目录执行
# 对 section03 的 phase05：改名 → 尾帧 → 与 phase04 合并
python .cursor/skills/phase-video-post/scripts/rename_tail_merge.py --section section03 --phase 5

# 仅改名 + 尾帧，不合并（例如 phase01 没有“上一段”或暂不合并）
python .cursor/skills/phase-video-post/scripts/rename_tail_merge.py --section section03 --phase 1 --no-merge
```

| 参数 | 说明 | 默认 |
|------|------|------|
| `--section NAME` | section 目录名，如 section02、section03 | 必填 |
| `--phase N` | 段号 1～12（刚生成视频的那一段） | 必填 |
| `--project-root PATH` | 项目根目录（其下有 section02、section03 等） | 当前工作目录 |
| `--no-merge` | 只做改名和尾帧，不执行与上一段合并 | 默认会合并（phase≥2 时） |

- 改名：只处理 `phases/phaseNN/` 下**唯一**的 `.mp4`；若已是 `phaseNN.mp4` 则跳过。
- 尾帧：输出到同目录，`{section}_tail_{N:02d}.png`。
- 合并：需要上一段存在 `phases/phase(N-1)/phase(N-1).mp4`，输出 `phases/phase_test_(N-1)_N.mp4`。

## 相关

- **extract-video-tail**：仅提取尾帧。
- **merge-video**：仅合并（phase-test / section-test）。
- **phase-transition**：若与上一段衔接生硬，可先做过渡再合并。
