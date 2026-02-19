# 角色形象参照

本文件夹用于存放 **角色形象图**（辛恩/蕾娜 定妆或海边度假造型）。

## 命名规范

| 文件名 | 说明 |
|--------|------|
| `section04_character_01.png` | 角色参考 1（如辛恩单人或双人） |
| `section04_character_02.png` | 角色参考 2（如蕾娜单人或双人） |
| `section04_character_couple.png` | 可选：两人同框海边度假造型 |

**规范格式**：`section04_character_NN.<png|jpg>` 或 `section04_character_couple.<png|jpg>`，避免即梦等平台的长文件名（如 `jimeng-日期-xxx-描述....png`），便于脚本与文档引用。

## 放置内容

- 辛恩/蕾娜 86 画风定妆或海边度假服（短袖、泳装/沙滩装等），与 section04 剧本一致。
- 可复用 section03/refs/characters 的图，复制到本目录后建议重命名为上述规范名。

## 使用方式

- 段 1 若用 **单张人物图** 作 API 参考：上传本目录中一张（如 `section04_character_couple.png`）取得 URL 后传入 `image_urls`。
- 若使用 `scripts/composite_refs.py` 合成多图：脚本会按文件名排序选取本目录与 refs/scenes 下的图，建议先统一为规范名。
