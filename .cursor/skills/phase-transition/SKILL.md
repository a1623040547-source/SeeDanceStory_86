---
name: phase-transition
description: Prepare and insert 1–3s transition clips between two phases for smoother cuts. Use when phase N and N+1 feel abrupt; create transition folder with tail/first frames, generate transition in Seedance, then merge with --with-transition.
---

# Phase 间补差过渡

当相邻两段（如 phase02 与 phase03）衔接生硬时，可在中间插入一段 **1～3 秒的过渡视频**：用前段尾帧 + 后段首帧在 Seedance 生成「补差」短片，合成时插入到两段之间。

## 流程概览

1. **准备过渡文件夹**：运行脚本，在 `phases/transition_02_03/` 中生成尾帧、首帧和提示词模板。
2. **在 Seedance 生成过渡视频**：以「尾帧 → 首帧」为起止，生成约 **2 秒** 过渡（可自定 1～3 秒），下载后放入该文件夹并命名为 `transition_02_03.mp4`。
3. **合并时插入补差**：使用 merge 脚本的 `--with-transition`，得到 phase02 + 过渡 + phase03 的成片。

## 文件夹约定

| 路径 | 说明 |
|------|------|
| `<section>/phases/transition_<from>_<to>/` | 过渡专用文件夹，如 `transition_02_03` |
| `tail.png` | 前段尾帧（复制自 phase02 的 section03_tail_02.png） |
| `first.png` | 后段首帧（从 phase03 视频第一帧提取） |
| `transition_02_03.txt` | Seedance 提示词模板（时长约 2 秒，可改） |
| `transition_02_03.mp4` | 你在 Seedance 生成的过渡视频，命名固定以便合并脚本识别 |

## 使用脚本

### 1. 准备过渡素材（尾帧 + 首帧 + 提示词模板）

脚本位置：`.cursor/skills/phase-transition/scripts/prepare_transition.py`

```bash
# 为 section03 的 phase02→phase03 准备过渡文件夹（从项目根执行）
python3 .cursor/skills/phase-transition/scripts/prepare_transition.py --section section03 --from 2 --to 3

# 可选：指定过渡时长（秒），默认 2
python3 .cursor/skills/phase-transition/scripts/prepare_transition.py --section section03 --from 2 --to 3 --duration 2
```

- 会创建 `section03/phases/transition_02_03/`，写入 `tail.png`、`first.png`、`transition_02_03.txt`。
- 若该文件夹已存在，会覆盖 `tail.png`、`first.png` 和同名的 `.txt`，不会删除已有 `transition_02_03.mp4`。

### 2. 在 Seedance 生成过渡视频

- **首图**：用 `transition_02_03/tail.png`（前段最后一帧）。
- **尾图/目标**：用 `transition_02_03/first.png`（后段第一帧）。
- 提示词：打开 `transition_02_03.txt` 参考或复制，描述「从当前画面自然过渡到下一镜」，时长设为约 **2 秒**（或 1～3 秒自定）。
- 生成后下载，将视频命名为 **`transition_02_03.mp4`** 并放入 `section03/phases/transition_02_03/`。

### 3. 合并时插入过渡视频

使用 merge 脚本的 **phase-test + --with-transition**：

```bash
# 合并 phase02 + 过渡 + phase03（若 transition_02_03.mp4 存在则自动插入）
python3 .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode phase-test --section section03 --from 2 --to 3 --with-transition
```

- 若 `transition_02_03/transition_02_03.mp4` 存在：输出为 phase02 + transition_02_03.mp4 + phase03 → `phase_test_02_03.mp4`。
- 若不存在：行为与不加 `--with-transition` 相同，仅 phase02 + phase03。

## 与 merge-video 的对应关系

- 普通 phase-test：`--from 2 --to 3` → 只拼 phase02 + phase03。
- 带补差：`--from 2 --to 3 --with-transition` → 拼 phase02 + transition_02_03.mp4 + phase03。
- 过渡视频建议时长：**2 秒**（可在 prepare 时用 `--duration` 写入提示词模板，实际以 Seedance 生成为准）。
