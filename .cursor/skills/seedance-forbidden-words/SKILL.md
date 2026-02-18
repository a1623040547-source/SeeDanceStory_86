---
name: seedance-forbidden-words
description: Manages and checks Seedance 2.0 (即梦) prompt forbidden words. Use when writing or revising Seedance prompts, when prompts are rejected, or when maintaining the forbidden-words list for this project.
---

# Seedance 2.0 提示词违禁词管理

本 Skill 维护「复制到即梦 Seedance 2.0 提示词框」时需避免或替换的用词，减少因违禁词导致的生成失败。

## 何时使用

- 撰写或修改 `phases/phaseXX.txt` 中「整段复制到 Seedance 2.0 提示词框」的英文提示词与负面词时，先对照违禁词表做替换。
- 用户反馈「不符合规则」「违禁」或生成被拒时，用违禁词表排查并改写。
- 发现新的疑似违禁词时，将「原词 + 替换建议」追加到 `forbidden-words.md`。

## 使用方式

1. **写提示词前**：打开 [forbidden-words.md](forbidden-words.md)，避免在提示词/负面词中直接使用「禁用」列词汇；优先使用「替换建议」列写法。
2. **排查被拒**：若整段复制后仍报错，在 `forbidden-words.md` 中搜索提示词里出现的词条，逐项替换后再试。
3. **更新列表**：确认新违禁词后，在 `forbidden-words.md` 对应分类下新增一行，格式与现有一致。

## 原则（不改剧本块）

- 仅对**会复制到 Seedance 提示词框 / 负面词框**的英文内容做违禁词替换。
- 本段情节说明、本段素材、剧本台词（含日文配音词）等**不复制进 Seedance**，可保留角色名、作品名等，无需为违禁词改剧本本身。

## 词表位置

完整分类与替换建议见：[forbidden-words.md](forbidden-words.md)
