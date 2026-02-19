---
name: seedance-api
description: 【废案】使用 Seedance 2.0 API 生成视频的约束与流程。当前项目已不再采用 API 生成连贯视频，本 skill 仅作参考保留。
---

# Seedance 2.0 API 使用（废案）

**状态：废案**。使用 API 生成连贯视频在当前阶段不切实际，详见 `section04/废案说明.md`。以下内容仅作参考保留。

本 Skill 说明在本项目中通过 **Seedance 2.0 API** 生成视频时的约束、环境配置与推荐流程。

---

## 一、何时使用

- 用户要求**用 Seedance 2.0 API** 生成视频（如 section04）时：按本 Skill 与 [docs/api-constraints.md](docs/api-constraints.md) 执行。
- 用户询问 **API 与即梦平台差异**（提示词长度、图片数量、时长）时：引用「关键约束」作答。
- 用户需要**取得参考图公网 URL** 时：使用项目根目录 `./scripts/upload-image-url.sh <图片路径>`，依赖 .env 中的 `IMGBB_API_KEY`。
- 用户编写或修改 **phase 提示词** 且 section 使用 API 时：提醒提示词须 **≤2000 字**，必要时精简【项目·风格·规则】或负面词。

---

## 二、环境配置（.env）

在项目根目录的 `.env` 中配置（勿提交到 git）：

```bash
SEEDANCE_API_KEY=你的Seedance_API密钥
IMGBB_API_KEY=你的ImgBB密钥   # 用于 upload-image-url.sh 获取图片直链
```

- **SEEDANCE_API_KEY**：在 Seedance API 控制台获取，用于 `Authorization: Bearer <key>`。
- **IMGBB_API_KEY**：在 https://api.imgbb.com/ 免费申请，用于脚本上传本地图片并输出公网 URL。

---

## 三、关键约束（与即梦对比）

| 项目 | API | 即梦平台 |
|------|-----|----------|
| 提示词长度 | **最大 2000 字符** | 通常更长 |
| 参考图数量 | **仅 1 张** | 可多图 |
| 参考图形式 | **公网 URL**（须先上传） | 可本地上传 |
| 单段时长 | **4 / 8 / 12 秒** | 常见 15s |

因此：每段只能传「首图」或「上一段尾帧图」其一；参考图须先用 `./scripts/upload-image-url.sh` 上传得 URL；提示词超长时需精简。

**参考图不能直接当作首帧**：若使用多图合成（如 2×2 拼图）作为段 1 的参考图，该图仅用于模型理解画风/角色/场景，**不是**视频的第一帧；段 2 起必须用「段 1 生成视频的最后一帧」截取的尾帧图作 V2V 输入。

---

## 四、推荐流程（单段）

1. **准备参考图**：首图或上一段尾帧（最后一帧）。
2. **取得 URL**：`./scripts/upload-image-url.sh section04/refs/scenes/section04_scene_01.png`（示例，见 section04/refs 命名规范），复制输出 URL。
3. **准备提示词**：从对应 `phases/phaseXX/phaseXX.txt` 取「给 Seedance 的整份提示词」，确保 **≤2000 字**。
4. **调用 API**：`POST https://seedanceapi.org/v1/generate`，Body 含 `prompt`、`image_urls`（数组仅 1 个 URL）、`duration`（如 "12"）、`aspect_ratio`（如 "16:9"）、`resolution`（如 "720p"）；Header 含 `Authorization: Bearer $SEEDANCE_API_KEY`。
5. **轮询结果**：`GET /v1/status?task_id=xxx` 直至 status 为 SUCCESS，从 `data.response[0]` 取视频 URL 下载。
6. **下一段**：从本段视频截取最后一帧 → 保存为 tail_XX.png → 再次 `upload-image-url.sh` 得 URL，供下一段使用。

---

## 五、详细约束与参数

详见 [docs/api-constraints.md](docs/api-constraints.md)。脚本目录下若有 `scripts/generate.py`，可用来提交任务并轮询状态（需从 .env 读取 SEEDANCE_API_KEY）。
