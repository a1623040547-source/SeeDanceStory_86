---
name: protagonist-identity
description: 固定、扩展与维护《86｜不存在的日常》男女主人公（辛恩、蕾娜）身份文档，记录角色信息并用于后续剧本创作与提示词一致性。在新建/改写 section 或 phase 剧本、撰写 Seedance 提示词、或需要确认主角性格/声线/微反应时使用。
---

# 主角身份文档（维护与使用）

本 Skill 用于**固定、扩展与维护**男女主人公的身份设定，并确保剧本与提示词与之一致。

---

## 一、何时使用

- 用户要求**新建 section** 或**写/改 phase 剧本**时：先查阅 [docs/characters.md](docs/characters.md)，在总述与各段中体现辛恩/蕾娜的性格、表达方式与微反应要求。
- 用户要求**撰写或修订 Seedance 提示词**时：确保【项目·风格·规则】与角色概述与 identity 文档一致；寡言方（辛恩）须有对蕾娜的微反应与触发–反应链。
- 用户要求**扩展主角信息**（如新角色、新字段、口癖、某 section 专用设定）时：在 [docs/characters.md](docs/characters.md) 中增补并保持表格/结构一致。
- 用户询问**辛恩/蕾娜人设、声线、相处方式**时：直接引用 docs/characters.md 内容作答。

---

## 二、身份文档位置与结构

- **主文档**：`.cursor/skills/protagonist-identity/docs/characters.md`
- **内容**：辛恩、蕾娜的固定设定表（身份/性格/表达方式/声线/外貌/与对方关系/禁忌）；共通设定（画风、关系、服装约定）；维护说明（扩展、新增字段、剧本引用）。

---

## 三、使用规范

1. **写剧本前**：读取 `docs/characters.md`，在 00、README、各 phase 的「本段情节说明」与「给 Seedance 的提示词」中体现：
   - 辛恩：沉稳少言 + **对蕾娜的微反应**（视线、喉结、眉、嘴角、手指等），触发–反应链明确。
   - 蕾娜：活泼、先开口、表情与台词有起伏；快段/慢段与留白搭配。
2. **扩展时**：在 characters.md 中新增角色或字段时，保持与现有表格格式一致，并在「维护说明」中注明可选字段用途。
3. **与 section 总述的关系**：各 section 的 `00-项目总述与素材说明.md` 中的【角色概述】应与本身份文档一致，可写「详见 @.cursor/skills/protagonist-identity/docs/characters.md」。

---

## 四、与 refs 的关系

- 角色形象图仍存放在各 section 的 `refs/characters/`（或复用如 `section03/refs/characters`）；本 Skill 只维护**文字设定**，不管理图片路径。
- 若某 section 复用其他 section 的角色 ref（如 section04 复用 section03/refs/characters），在 00 或 README 中注明「角色设定与形象见 protagonist-identity 与 section03/refs/characters」。
