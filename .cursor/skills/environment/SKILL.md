---
name: environment
description: 环境档案：固定、扩展与维护项目中可复用的场景/环境设定（光线、氛围、空间锚点、用于生成环境图的描述）。写 section 或 story 剧本、Seedance 提示词【场景与氛围】、规划 refs/scenes 与 refs/env_atmosphere 时使用；搭建故事时与 @character-shin、@character-lena 并列查阅，便于人设与场景一并落地。
---

# 环境档案（Environment）

本 Skill 维护**可复用的场景/环境设定**，一个 skill 内可放多个不同环境，便于搭建 story、新建 section 时直接引用或略改，保证【场景与氛围】与 refs 一致。

---

## 一、何时使用

- **搭建或规划 story**时：与 @protagonist-identity（或 @character-shin / @character-lena）并列查阅；从 [docs/environments.md](docs/environments.md) 索引中选环境，进入对应 `envs/<环境文件夹>` 查阅或引用。
- **新建 section**时：在 00、refs/scenes/README、refs/env_atmosphere 中约定本 section 所用环境时，引用本 skill 中对应环境文件夹内的 README（场景、光线、氛围、空间锚点、环境描述）。
- **撰写或修订 Seedance 提示词【场景与氛围】**时：从该环境的 README 取「环境提示词」或「用于生成环境图的描述」，保证段与段、section 与 section 环境一致。
- **扩展新环境**时：在 `envs/` 下新建文件夹（建议英文 kebab-case），内放 README.md 与 refs/，并在 [docs/environments.md](docs/environments.md) 索引中追加一行。

---

## 二、档案结构

- **索引**：`.cursor/skills/environment/docs/environments.md` — 环境列表与到各文件夹的链接。
- **每种环境单独文件夹**：`.cursor/skills/environment/envs/<环境名>/`
  - **README.md**：该环境的完整设定（场景、光线、氛围、空间锚点、环境提示词、用于生成环境图、门/特殊约定、备注）；可在此文件内继续增补细节。
  - **refs/**：本环境的场景/氛围参考图，可放图片及简短说明，供 section 或 story 引用。
- 各 section 的 `refs/scenes/`、`refs/env_atmosphere/` 仍为生成时主要路径；本 skill 的 envs/refs 为环境档案自带的参考图与跨 section 复用。

---

## 三、与角色、section、story 的关系

- **与角色**：写剧本或提示词时，人设用 @character-shin、@character-lena；场景与氛围用本 skill 的 envs 下对应环境文件夹，二者结合即可快速写出「谁在什么环境里做什么」。
- **与 section**：各 section 的 00、refs/scenes/README 中【环境概述】可与本 skill 某环境文件夹内 README 一致，并注明「环境详见 @.cursor/skills/environment envs/xxx」或直接粘贴/改写对应描述。
- **与 story**：故事总述中的「各 Section 环境」「环境提示词」「用于生成环境图」可直接从对应环境 README 摘录或映射（如 S1→envs/seaside-motel-room、S2→envs/shallow-beach 等），后续新建 section 时按 story 映射到本 skill 该环境即可。

---

## 四、环境条目建议字段（扩展时在 envs/新文件夹/README.md 中遵循）

每个环境 README 建议包含（可酌情省略暂无用到的字段）：

| 字段 | 用途 |
|------|------|
| 名称/代号 | 便于在 story、00 中引用（如「民宿室内」「浅滩」「露台傍晚」） |
| 场景 | 地点、空间类型、主要物件（门/窗/沙发/沙滩/栏杆等） |
| 光线 | 主光源、冷暖、时间感（自然光/傍晚/夜灯等） |
| 氛围 | 情绪、质感（温馨/活泼/私密/开阔等） |
| 空间锚点 | 写 phase 提示词时的人物位置参考（如海水在脚下、背后为沙滩） |
| 环境提示词（【场景与氛围】） | 可直接写入 phase 的短段描述 |
| 用于生成环境图的描述 | 供 refs/scenes 或图生用的、侧重构图与氛围的一句/段 |
| 门/特殊约定 | 若涉及门则写「自动门（横向滑动）」等；其他 Seedance 适配约定 |
| 备注 | 已用于哪条 story/section、可复用场景等 |

细节与参考图可在该环境文件夹内继续增补（README 正文或 refs/ 下图片）。
