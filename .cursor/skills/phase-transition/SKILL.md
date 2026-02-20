---
name: phase-transition
description: 【已废弃】请改用 cross-section-transition：用 ffmpeg 生成 ≤1s 渐隐/渐显过渡，phase-test / cross-section 合并时加 --with-transition 即可，无需 Seedance。
---

# Phase 间补差过渡（已废弃）

**本 skill 已废弃。** 相邻 phase 的过渡请统一使用 **cross-section-transition**：本地 ffmpeg 生成约 1 秒渐隐→渐显，无需 Seedance。合并时使用 `--mode phase-test --from N --to N+1 --with-transition` 即可自动生成并插入过渡。参见 `.cursor/skills/cross-section-transition/SKILL.md`。
