---
name: merge-video
description: Merge phase videos for testing. Use when you need to concatenate Seedance phase outputs—either two adjacent phases (phase-test), all phases in a section (section-test), or cross-section (last phase of section1 + first phase of section2, optionally with ≤1s fade transition). Scripts live inside this skill.
---

# 合并 Phase 视频

将多个 phase 视频按顺序无损拼接，用于**阶段测试**或**整段预览**。

## 模式概览

| 模式 | 说明 | 输出示例 |
|------|------|----------|
| **phase-test** | 合并指定的两个相邻 phase 视频（如 phase01 + phase02） | `section02/phases/phase_test_01_02.mp4` |
| **section-test** | 合并该 section 下所有已存在的 phase 视频（phase01～phase12） | `section02/section02_merged.mp4` |
| **cross-section** | 上一 section 最后一 phase + 下一 section 第一 phase，可选中间插入 ≤1s 渐隐/渐显过渡 | `story/01-海边度假/section01_08_to_section02_01.mp4` |

## 依赖

- **ffmpeg**（需在 PATH 中）：用于 concat 无损拼接。

## 使用脚本

脚本位置：`.cursor/skills/merge-video/scripts/merge_phase_videos.py`

### phase-test：合并相邻两段

```bash
# 合并 phase01 与 phase02（从项目根执行）
python .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode phase-test --section section02 --from 1 --to 2

# 合并 phase02 与 phase03，并在中间插入补差过渡视频（若存在 transition_02_03/transition_02_03.mp4）
python3 .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode phase-test --section section03 --from 2 --to 3 --with-transition
```

- `--from N`、`--to N`：相邻段号，且必须满足 `to = from + 1`（只支持两段相邻）。
- `--with-transition`：若存在过渡视频，则**把过渡直接拼到前段视频尾部**（覆盖该 phase 的 mp4），并在该 phase 目录下用 **README.md** 记录「尾部拼接过渡 Xs（至 phase0Y）」；再与前段+后段合并。section-test 若检测到 README 中已有「尾部拼接」记录则不再插入独立过渡段。详见 skill **phase-transition**。
- 输出：`<section>/phases/phase_test_<from>_<to>.mp4`。

### section-test：合并整段所有 phase

```bash
# 合并 section02 下所有已有 phase 视频（phase01.mp4, phase02.mp4, ...）
python .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode section-test --section section02
```

- 会按 phase01～phase12 顺序扫描，依次拼接 `phaseNN.mp4`；若某段 **README.md** 中已记录「尾部拼接」（过渡已直接拼在该段视频尾部），则不再插入独立 `transition_XX_YY.mp4`。
- 输出：`<section>/<section>_merged.mp4`（如 `section02/section02_merged.mp4`）。

### cross-section：跨 section 拼接（可选过渡）

```bash
# 从项目根执行，指定 story 目录为 project-root
python3 .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode cross-section --project-root "story/01-海边度假" --section1 section01 --phase1 8 --section2 section02 --phase2 1

# 带场景过渡：上一 section 尾帧渐隐 + 下一 section 首帧渐显（≤1s），过渡视频自动生成
python3 .cursor/skills/merge-video/scripts/merge_phase_videos.py --mode cross-section --project-root "story/01-海边度假" --section1 section01 --phase1 8 --section2 section02 --phase2 1 --with-transition
```

- `--section1` / `--phase1`：上一 section 的最后一 phase（如 section01 的 phase08）。
- `--section2` / `--phase2`：下一 section 的第一 phase（如 section02 的 phase01）。
- `--with-transition`：把约 1 秒过渡（尾帧渐隐→首帧渐显）**直接拼到上一 section 末段视频尾部**（覆盖该 phase 的 mp4），并在该 phase 目录下用 **README.md** 记录「尾部拼接过渡 1s（跨 section 至 section02 phase01）」；再与下一 section 首段合并。后续整合直接拼该 phase 的 mp4 + section02 phase01 即可。过渡视频若不存在会先自动生成。
- 输出：`<story_dir>/section01_08_to_section02_01.mp4`。

### 可选参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `--project-root PATH` | 项目根目录（其下有 section02 等） | 当前工作目录 |
| `--section NAME` | section 目录名 | 必填 |
| `--from N` / `--to N` | phase-test 时起止段号（相邻） | phase-test 时必填 |

## 与 phase 目录的对应关系

- 每段视频路径：`<section>/phases/phaseNN/phaseNN.mp4`。若某 phase 的 **README.md** 中记录了「尾部拼接过渡」，表示该段 mp4 末尾已直接拼了过渡，section-test 不会在该段后再插独立过渡。

---

## 相关

- **cross-section-transition**：跨 section 时用 `--with-transition` 将约 1s 渐隐/渐显过渡直接拼到第一段视频尾部（覆盖该 phase 的 mp4），并在该 phase 的 README 中记录时长。
- **phase-transition**：同一 section 内相邻两段衔接生硬时，可准备「尾帧+首帧」并在 Seedance 生成 1～3 秒过渡视频；phase-test `--with-transition` 会把过渡直接拼到前段视频尾部并在 README 中记录，section-test 根据 README 不再插独立过渡段。
- **比例补正（aspect-correct）**：若某段与上一段尾帧衔接处有轻微拉伸，可先用 aspect-correct 以上一段尾帧为参考补正该段，再做合并测试。
