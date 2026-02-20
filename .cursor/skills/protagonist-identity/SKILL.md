---
name: protagonist-identity
description: 辛恩与蕾娜身份文档的入口索引。具体设定与人物/服装参考图已拆分为两个独立 skill：character-shin（辛恩）、character-lena（蕾娜）。需查人设、写剧本或提示词时请使用 @character-shin 与 @character-lena。
---

# 主角身份文档（索引）

本 Skill 为**男女主人公身份文档的入口**。辛恩与蕾娜已分别拆成独立档案，便于维护与扩展。

---

## 一、请使用独立角色 Skill

| 角色 | Skill | 文字档案 | 人物图 / 服装图 |
|------|--------|-----------|------------------|
| **辛恩** | **@.cursor/skills/character-shin** | docs/shin.md | refs/、refs/clothes/ |
| **蕾娜** | **@.cursor/skills/character-lena** | docs/lena.md | refs/、refs/clothes/ |

- 写/改 **section 或 phase 剧本**、**Seedance 提示词**，或需确认**辛恩**人设/微反应时：使用 **character-shin**，查阅 docs/shin.md。
- 需确认**蕾娜**人设/声线/台词节奏时：使用 **character-lena**，查阅 docs/lena.md。
- 双人戏份、共通设定（画风、关系、服装约定）在两个角色的 docs 中均有「共通设定」小节；也可查阅下方合并版。

---

## 二、合并查阅（可选）

若需**一次查看两人**的固定设定表，可读 [docs/characters.md](docs/characters.md)。该文件为历史合并版，扩展与更新请以 character-shin / character-lena 各自 docs 为准。

---

## 三、与 section、环境的关系

- **角色**：各 section 的 `00-项目总述与素材说明.md` 中【角色概述】可与身份文档一致，并注明「辛恩详见 @character-shin，蕾娜详见 @character-lena」。各 section 的 `refs/characters/`、`refs/clothes/` 仍为生成时主要路径；角色 skill 内 refs 为档案备份与跨 section 参照。
- **环境**：搭建 story 或写 section 的【环境概述】/【场景与氛围】时，可并列查阅 **@.cursor/skills/environment**，从环境档案中选用或改写场景、光线、氛围与用于生成环境图的描述。
