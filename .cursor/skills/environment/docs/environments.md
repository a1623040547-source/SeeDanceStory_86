# 环境档案一览

每种环境单独一个文件夹，便于后续填充更多细节与参考图。搭建 story、新建 section、写【场景与氛围】或 refs 时从下表选环境，进入对应文件夹查阅或引用。

---

## 环境列表

| 名称/代号 | 文件夹 | 已用于 |
|-----------|--------|--------|
| 海边民宿室内（玄关/带窗房间） | [envs/seaside-motel-room](../envs/seaside-motel-room/) | story 海边度假 S1 |
| 浅滩 / 水边 | [envs/shallow-beach](../envs/shallow-beach/) | story 海边度假 S2 |
| 日间沙滩 | [envs/daytime-beach](../envs/daytime-beach/) | story 海边度假 S3 |
| 傍晚沙滩 / 露台（日落） | [envs/evening-beach-terrace](../envs/evening-beach-terrace/) | story 海边度假 S4 |
| 民宿卧室·床 | [envs/motel-bedroom](../envs/motel-bedroom/) | story 海边度假 S5 |
| 室内客厅·雨窗（周末小剧场） | [envs/indoor-rain-window](../envs/indoor-rain-window/) | section02 |
| 露台·傍晚·城市夜景 | [envs/terrace-city-night](../envs/terrace-city-night/) | section03 |

---

## 单环境文件夹结构

每个环境目录下：

- **README.md**：该环境的完整设定（场景、光线、氛围、空间锚点、环境提示词、用于生成环境图、门/特殊约定、备注）；可在此文件内继续增补细节。
- **refs/**：本环境的场景/氛围参考图，供 section 或 story 引用；refs 内可放图片与简短说明。

---

## 扩展新环境

1. 在 `envs/` 下新建文件夹，建议用英文 kebab-case（如 `new-cafe-interior`）。
2. 在该文件夹内创建 `README.md`（按现有环境条目格式填写）与 `refs/README.md`（说明本目录可放参考图）。
3. 在本页「环境列表」中追加一行，链接到新文件夹。

门、窗、家具等**细致场景描述**见《section-phase-script-retro》[03-场景环境与空间](../../section-phase-script-retro/docs/03-场景环境与空间.md)；本档案侧重「环境类型与可复用描述」，与各 section 的 refs/scenes/README、00 互补。
