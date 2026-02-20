---
name: cross-section-transition
description: Scene transition (≤1s ffmpeg fade) between two phases—same-section or cross-section. Tail frame fades out, next first frame fades in; transition is appended to the first segment's mp4 and recorded in README. Use with merge-video via --with-transition (phase-test or cross-section).
---

# 场景过渡（同 section / 跨 section）

在**任意两段相邻 phase**（同 section 内 phase N→N+1，或跨 section 末段→下一 section 首段）拼接时，若直接硬切观感生硬，可插入一段 **≤1 秒** 的纯画面过渡：

- **前段尾帧** 渐隐（fade out）
- **后段首帧** 渐显（fade in）

整段过渡由 **ffmpeg 本地生成**，无需 Seedance；分辨率与前后段一致。

## 用法概览

- **同 section 内 phase→phase**（如 phase03→phase04）：`phase-test --with-transition`，会自动生成过渡并拼到前段尾部。
- **跨 section**（如 section01 phase08→section02 phase01）：`cross-section --with-transition`，同上。

## 1. 同 section：phase03→phase04 带过渡

```bash
python3 .cursor/skills/merge-video/scripts/merge_phase_videos.py \
  --mode phase-test --project-root "story/01-海边度假" \
  --section section02 --from 3 --to 4 --with-transition
```

- 会从 phase03 尾帧、phase04 首帧生成约 1s 过渡（若尚未存在），输出到 `section02/phases/transition_03_04/transition_03_04.mp4`；
- 把过渡拼到 phase03 的 mp4 尾部（覆盖），并在 phase03 的 **README.md** 记录「尾部拼接过渡 1s（至 phase04）」；
- 最终得到 `phase_test_03_04.mp4`。

仅生成过渡视频（不合并）：

```bash
python3 .cursor/skills/cross-section-transition/scripts/make_cross_section_transition.py \
  --project-root "story/01-海边度假" \
  --section1 section02 --phase1 3 --section2 section02 --phase2 4
```

- 输出：`section02/phases/transition_03_04/transition_03_04.mp4`（约 1s）。

## 2. 跨 section：section01 末段→section02 首段

```bash
python3 .cursor/skills/merge-video/scripts/merge_phase_videos.py \
  --mode cross-section --project-root "story/01-海边度假" \
  --section1 section01 --phase1 8 --section2 section02 --phase2 1 \
  --with-transition
```

- 在 `transition_s01_s02/` 下生成约 1s 过渡（若尚未存在），拼到 section01 phase08 的 mp4 尾部并写 README；
- 输出：**section01_08_to_section02_01.mp4**。

仅生成过渡视频：

```bash
python3 .cursor/skills/cross-section-transition/scripts/make_cross_section_transition.py \
  --project-root "story/01-海边度假" \
  --section1 section01 --phase1 8 --section2 section02 --phase2 1
```

- 输出：`<story_dir>/transition_s01_s02/transition_s01_s02.mp4`（约 1s）。

## 文件夹约定

| 场景 | 路径 | 说明 |
|------|------|------|
| 同 section | `<section>/phases/transition_XX_YY/` | 如 transition_03_04 |
| 跨 section | `<story_dir>/transition_s01_s02/` | 固定名 transition_s01_s02 |
| 通用 | `tail.png` / `first.png` | 尾帧 / 首帧（脚本生成或复用已有） |
| 通用 | `transition_*.mp4` | 约 1s 渐隐→渐显 |

## 过渡参数

- **总时长**：1 秒（可 `--duration`，建议 ≤1s）。
- **前半**：尾帧静置后渐隐；**后半**：首帧渐显。

依赖：**ffmpeg**（需在 PATH 中）。

## 与 merge-video 的对应关系

- **phase-test + --with-transition**：自动用本技能生成/复用过渡，拼到前段 mp4 尾部并写 README，再合并两段。
- **cross-section + --with-transition**：同上（跨 section）。
- **section-test**：若某 phase 的 README 已记录「尾部拼接过渡」，不再插入独立过渡段。

## 相关

- **merge-video**：phase-test / section-test / cross-section 合并；`--with-transition` 统一走本技能（ffmpeg 过渡）。
