---
name: merge-video
description: Merge phase videos for testing. Use when you need to concatenate Seedance phase outputs—either two adjacent phases (phase-test) or all phases in a section (section-test). Scripts live inside this skill.
---

# 合并 Phase 视频

将多个 phase 视频按顺序无损拼接，用于**阶段测试**或**整段预览**。

## 两种模式

| 模式 | 说明 | 输出示例 |
|------|------|----------|
| **phase-test** | 合并指定的两个相邻 phase 视频（如 phase01 + phase02） | `section02/phases/phase_test_01_02.mp4` |
| **section-test** | 合并该 section 下所有已存在的 phase 视频（phase01～phase12） | `section02/section02_merged.mp4` |

## 依赖

- **ffmpeg**（需在 PATH 中）：用于 concat 无损拼接。

## 使用脚本

脚本位置：`.cursor/skills/merge-video/scripts/merge_phase_videos.py`

### phase-test：合并相邻两段

```bash
# 合并 phase01 与 phase02（从项目根执行）
python .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode phase-test --section section02 --from 1 --to 2

# 合并 phase03 与 phase04
python .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode phase-test --section section02 --from 3 --to 4
```

- `--from N`、`--to N`：相邻段号，且必须满足 `to = from + 1`（只支持两段相邻）。
- 输出：`<section>/phases/phase_test_<from>_<to>.mp4`。

### section-test：合并整段所有 phase

```bash
# 合并 section02 下所有已有 phase 视频（phase01.mp4, phase02.mp4, ...）
python .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode section-test --section section02
```

- 会按 phase01～phase12 顺序扫描，只拼接存在的 `phaseXX/phaseXX.mp4`。
- 输出：`<section>/<section>_merged.mp4`（如 `section02/section02_merged.mp4`）。

### 可选参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `--project-root PATH` | 项目根目录（其下有 section02 等） | 当前工作目录 |
| `--section NAME` | section 目录名 | 必填 |
| `--from N` / `--to N` | phase-test 时起止段号（相邻） | phase-test 时必填 |

## 与 phase 目录的对应关系

- 每段视频路径：`<section>/phases/phaseNN/phaseNN.mp4`。
- phase-test 仅拼接两段，用于快速检查衔接；section-test 用于整段成片预览。

---

## 相关：比例补正（aspect-correct）

若某段与上一段尾帧衔接处有轻微拉伸，可先用 aspect-correct 以上一段尾帧为参考补正该段，再做合并测试。
