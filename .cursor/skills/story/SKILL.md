---
name: story
description: 在 section 之上扩展的「故事」层级，用于组织总长接近或超过约 10 分钟的长篇内容；提供跨 section 的剧情弧、分镜切换选择与过渡方案。创作或扩展 story、撰写故事大纲、规划 section 划分与 section 间过渡时使用。
---

# Story 故事层级（在 Section 之上）

本 Skill 定义**故事（story）** 文件夹的用途与结构：在单个 section（约 2～3 分钟、若干 phase）之上，用 story 组织**更长的连贯剧情**（如总长接近 10 分钟），并为**分镜/场景切换**提供更多选择（section 间黑场、时间跳跃、景别与情绪切点等）。

---

## 一、何时使用

- 用户要求**创作比一个 section 更长的故事**（如总长接近 10 分钟）、且需**先出大纲再填 section** 时：按本 Skill 建立 story 文件夹并撰写 `00-故事总述与大纲.md`。
- 用户要求**扩展 story 框架**、**规划 section 划分**或**设计 section 之间的过渡方式**时：在 story 的 00 或 README 中维护「section 列表」与「section 间过渡方案」。
- 用户询问**story 与 section 的关系**、**如何从大纲落到具体 section/phase** 时：引用本 Skill 与《剧本与视频生成流程》《section-phase-script-retro》。

---

## 二、Story 与 Section 的关系

| 层级 | 时长（约） | 内容单位 | 主要用途 |
|------|------------|----------|----------|
| **Story** | 约 8～12 分钟（可更长） | 多个 **Section** | 整体剧情弧、时间/地点/情绪分段；section 间过渡方式（黑场/淡入淡出/时间跳跃/景别） |
| **Section** | 约 2～3 分钟 | 多个 **Phase**（每段 15s） | 单一场景/时段内的完整小剧情；phase 间首尾帧 V2V + 动作切点/景别等（见《section-phase-script-retro》） |
| **Phase** | 15s | 单段生成单元 | 图生/V2V、提示词、台词、尾帧衔接 |

- **Story 不替代 section**：每个 section 仍保留自己的 `00-项目总述与素材说明`、`README`、`refs/`、`phases/`，可按《剧本与视频生成流程》独立生成。
- **Story 提供**：总述与大纲、section 列表（顺序与标题）、section 间「可选分镜/过渡方案」、全篇节奏与氛围统筹（便于多 section 环境/穿着一致或有意变化）。
- **Story 下的 Phase**：当 section 属于某 story 时，其**每个 phase** 除 section 级信息（本段情节说明、本段素材、提示词等）外，还须**提及整个 story 的大纲**——即在 phase 内标明本段在全篇剧情弧中的位置、所属 section 及与前后 section 的关系，便于生成与改写时保持全篇一致。落实方式见下节。

---

## 三、Story 目录结构规范

建议每个 story 单独成夹，与现有 `section01/`、`section02/` 等并列或置于 `story/` 下统一管理：

```
story/
  01-海边度假/                    # 或 story01-海边度假/
  ├── 00-故事总述与大纲.md         # 必选：总述、剧情弧、section 列表、section 间过渡、节奏与复盘要点
  ├── README.md                   # 可选：story 概述、与各 section 的对应关系、生成顺序
  └── sections/                   # 可选：此处可放 section 的符号链接或占位说明；实际 section 可在根目录 sectionXX/
      └── README.md               # 说明本 story 下 section 编号与路径（如 section05～section09）
```

- **00-故事总述与大纲.md** 必须包含（见下节）。
- 具体 section 的 phase 文件仍位于各 `sectionXX/` 内；story 只做**规划与索引**，不重复存放 phase 内容。

---

## 四、00-故事总述与大纲.md 必须包含

1. **一、故事总述**  
   标题、主角（与 protagonist-identity 一致）、总时长（约）、风格与基调；一句话剧情梗概。

2. **二、剧情弧与 Section 划分**  
   - 按时间/地点/情绪将全篇拆成若干 **section**（每个 section 约 2～3 分钟，对应 8～12 个 phase）。  
   - 每个 section 一段话概括：场景、主要事件、情绪与节奏（快段/慢段、留白段）。  
   - 标注全篇**快段/慢段分布**（与《section-phase-script-retro》台词与节奏一致）。

3. **三、Section 间过渡与分镜选择**  
   - 为每对**相邻 section** 标注推荐的过渡方式（如黑场 0.5s、淡出淡入、时间跳跃「翌日」、景别从大景切到特写等）。  
   - **过渡责任的落点**：section 间过渡的**实际任务落在各 section 的第一个 phase（段首）与最后一个 phase（段尾）**。段尾 phase 须在情节说明与提示词中写清本段收束方式（动作/景别/情绪），为跨 section 过渡预留；段首 phase 须写清承接上一 section、本 section 开场。在 00 或 README 中说明此点，便于撰写各 section 时在首/末 phase 落实。  
   - 可选：表格列出「section A → section B」的过渡方案与剪辑备注，便于分镜切换有据可依。

4. **四、环境·氛围·穿着统筹**  
   - 全篇统一或按 section 约定的：场景（如海边·日间/傍晚）、光线与氛围、角色穿着状态（如泳装/便服/浴衣）及变化节点，避免跨 section 漂移（见《section-phase-script-retro》环境氛围、穿着状态）。  
   - **各 Section 环境提示词**：每个 section 可能选取不同环境，后续为各 section 撰写 phase 与 refs 时需有统一的环境描写。在 00 中为**每个 section 给出环境提示词描写**（可直接或略改后用于该 section 的【场景与氛围】及 refs/scenes 说明），便于生成时氛围一致。
   - **各 Section 环境描述（用于生成环境图）**：除上述提示词外，为每个 section 给出**用于生成环境/场景图**的描写（构图、主体、光线、景深、氛围等，面向静帧/背景图生成），便于制作 refs/scenes 或独立环境图。
   - **各 Section 服饰描述（用于生成人物俯视图/角色参考图）**：为每个 section（或穿着变化节点）给出**服饰描述**（男女主分别或合并，含上衣/下装/鞋/配饰等），便于生成角色 ref 图（含俯视图、全身参考），与剧情穿着状态一致。

5. **Section 尾部收束**（构建剧本时）  
   - 每个 section 的**尾部**（尤其是最后一个 phase）应是**收束的**：该 section 内情节与情绪有明确收束点（如动作结束、视线落点、静帧感、或空镜），避免断在动作/台词半途。这样既便于本 section 独立观看，也便于与下一 section 的过渡；段尾 phase 的「收束」与上文「过渡责任落点」配合使用。

6. **五、复盘要点在本 story 的落实**  
   - 简要列出本故事中如何落实：寡言方微反应与触发-反应链、快段/慢段、phase 内环环相扣、镜头过渡、配乐 15s 内封闭等（可引用《section-phase-script-retro》条目）。

7. **六、与各 Section 的对应关系**  
   - 表：section 编号、标题、对应 phase 范围（或 phase 数量）、refs 与 00 文件路径（若已创建）。

---

## 五、Story 下 Phase 须提及整个 story 大纲（落实方式）

当某 section 从属于一个 story 时，该 section 内**每个 phase 文件**除《剧本与视频生成流程》规定的 section 级内容外，须增加对**整个 story 大纲**的提及：

1. **【本段情节说明】或 phase 文件开头**  
   - 用一两句点明：本 story 总纲（如「和平后海边度假：抵达→散步→玩水→傍晚→收尾」）、本段所属 section（如「本段属 S2 海边散步」）、本段在全篇中的位置（如「日间散步中段」）。  
   - 可与「承接上段…」「本段以…结束、下段将…」合并书写，避免重复。

2. **给 Seedance 的提示词（可选但推荐）**  
   - 在【项目·风格·规则】或整份提示词开头，用一行概括本 story 与本段位置（如「本片为海边度假故事，本段为日间沙滩散步中段，与前后 section 衔接」），便于模型理解全篇语境；若平台字数敏感，可仅在情节说明中写清。

3. **段首 / 段尾 phase**  
   - 段首 phase 须写清「承接上一 section（某某）的…」；段尾 phase 须写清「本段收束…，下一 section（某某）将…」。与「过渡责任落点」一致，且均建立在「已标明 story 总纲与本 section 位置」的前提下。

各 section 的 00 或 README 可注明「本 section 属于 story XX，各 phase 须见 @story/XX/00-故事总述与大纲.md 并提及 story 大纲」。

---

## 六、与现有 Skill 的衔接

- **角色**：故事中的主角设定须与 [protagonist-identity](.cursor/skills/protagonist-identity/docs/characters.md) 一致；新建 section 时在 00 中引用。
- **Section/Phase 剧本**：每个 section 的创建与 phase 撰写仍按《剧本与视频生成流程》执行；节奏、动作、寡言微反应、环环相扣、镜头过渡按《section-phase-script-retro》执行。**若 section 属于某 story**，phase 还须按上节**提及整个 story 大纲**。
- **分镜选择**：story 层提供「section 间」的过渡与分镜选择；section 层提供「phase 间」的过渡方案（见《section-phase-script-retro》第五节）。

---

## 七、执行清单（新建 story 时）

- [ ] 创建 story 文件夹及 `00-故事总述与大纲.md`。
- [ ] 在 00 中写清：总述、剧情弧、section 划分（标题与约时长）、section 间过渡方案（含**过渡责任落点**：段首/段尾 phase）、**section 尾部收束**要求、环境/穿着统筹、**各 section 环境提示词**、**各 section 环境描述（用于生成环境图）**、**各 section 服饰描述（用于生成人物俯视图/角色参考图）**、复盘要点落实。
- [ ] 确认与 protagonist-identity 一致；若为 86 辛恩×蕾娜，注明「详见 @.cursor/skills/protagonist-identity/docs/characters.md」。
- [ ] 用户确认大纲后再创建或填充具体 section（每个 section 按《剧本与视频生成流程》与《section-phase-script-retro》执行）。
- [ ] 填充各 section 的 phase 时：**每个 phase 须提及整个 story 大纲**（见第五节：情节说明或开头标明 story 总纲、本段所属 section 及在全篇位置；可选在提示词【项目·风格·规则】带一句 story 与本段位置）。
