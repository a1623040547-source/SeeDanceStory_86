# 场景图 / 段 1 首图

本文件夹用于存放 **段 1 图生视频所用的首图或纯场景参考图**。

## 命名规范

| 文件名 | 说明 |
|--------|------|
| `section04_scene_01.png` | 海边度假场景（可无人物，作环境参考） |
| `section04_ref_img.jpg` | 可选：段 1 用首图（场景+两人合成），上传 API 时用 |

**规范格式**：`section04_scene_NN.<png|jpg>` 或 `section04_ref_img.jpg`，避免即梦等平台的长文件名。

## 放置内容

- **夏日海边场景**：晴空、海浪、沙滩，86 动画风；可无人物。
- **首图**（若单独制作）：辛恩与蕾娜在沙滩/海边、度假夏装，与剧本一致。

## 使用方式

1. 将场景图/首图放入本文件夹，按上表命名。
2. 使用 **Seedance 2.0 API** 时，须先将该图上传至图床取得**公网 URL**：
   ```bash
   ./scripts/upload-image-url.sh section04/refs/scenes/section04_scene_01.png
   # 或首图：section04/refs/scenes/section04_ref_img.jpg
   ```
3. 段 1 请求中 `image_urls` 传该 URL，提示词从 `phases/phase01/phase01.txt` 取用（须 ≤2000 字）。

## 注意

- API 仅支持 **1 张** 参考图；若用纯场景图，可另用 refs/characters 中人物图作风格参考（或合成后再上传）。
