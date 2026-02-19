# Seedance 2.0 API 约束与用法

基于 [Seedance 2.0 API 文档](https://seedanceapi.org/docs) 的要点整理，用于本项目中通过 API 生成视频（如 section04）时的约束与流程。

---

## 一、认证与 .env

- **Base URL**：`https://seedanceapi.org/v1`
- **认证**：所有请求需在 Header 中带 `Authorization: Bearer YOUR_API_KEY`
- **本项目**：API Key 存放在项目根目录 **`.env`** 中，变量名为 `SEEDANCE_API_KEY`。勿将 .env 提交到 git。

```bash
# .env 示例
SEEDANCE_API_KEY=sk-xxxxxxxx
```

---

## 二、关键约束（与即梦平台差异）

| 项目 | API 限制 | 说明 |
|------|----------|------|
| **提示词长度** | 最大 **2000 字符** | 即梦平台可能更长；写 phase 提示词时须控制在此内，可精简【项目·风格·规则】或合并句子。 |
| **参考图** | **仅 1 张** | 参数 `image_urls` 为字符串数组，**最多 1 个元素**；不能同时传角色图 + 尾帧图。 |
| **图片来源** | **必须为公网 URL** | API 无法上传本地文件，须先将图片上传到图床（如 ImgBB），取得 HTTPS 直链后传入 `image_urls[0]`。 |
| **单段时长** | **4 / 8 / 12 秒** | 与即梦 15s 不同；本项目中 section04 采用 **12s** 每段。 |

---

## 三、图片 URL 获取（本项目）

1. 将需要作为参考的图片（首图或尾帧）准备好，路径如 `section04/refs/scenes/section04_scene_01.png`、`section04/refs/characters/section04_character_couple.png` 或 `section04/phases/phase01/section04_tail_01.png`（见 section04/refs 命名规范）。
2. 在项目根目录执行：
   ```bash
   ./scripts/upload-image-url.sh <图片路径>
   ```
3. 脚本会使用 `.env` 中的 `IMGBB_API_KEY` 上传到 ImgBB，终端输出一行**公网 URL**，复制到 API 请求的 `image_urls` 即可。

### 参考图 vs 首帧（不能混用）

- **多图合成**（如 `scripts/composite_refs.py` 输出的 2×2 拼图）：仅作**参考图**，供模型理解画风、角色与场景；**不能直接用作视频首帧**，也不能作为段 2 的 V2V 输入。
- **V2V 衔接**：段 2 及以后必须使用「上一段生成视频的**最后一帧**」截取并上传得到的 URL，才能保证画面连贯。

---

## 四、请求参数摘要（POST /v1/generate）

| 参数 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| prompt | string | ✅ | 文本描述，**最多 2000 字符** |
| image_urls | string[] | 否 | **最多 1 个** URL，用于图生视频 / V2V 起点 |
| aspect_ratio | string | 否 | 默认 1:1；可选 16:9, 9:16, 4:3, 3:4, 21:9, 9:21 |
| resolution | string | 否 | "480p" 或 "720p"，默认 720p |
| duration | string | 否 | "4" / "8" / "12"，默认 8 |
| generate_audio | boolean | 否 | 默认 false |
| fixed_lens | boolean | 否 | 默认 false |
| callback_url | string | 否 | 异步回调 URL（须公网可访问） |

---

## 五、状态与结果（GET /v1/status）

- 创建任务后返回 `task_id`，轮询 `GET /v1/status?task_id=xxx` 直至 `data.status` 为 `SUCCESS` 或 `FAILED`。
- 成功时视频 URL 在 `data.response[0]`，可直接下载。

---

## 六、与 section phase 的配合

- **段 1**：首图上传得 URL → `image_urls` = [首图URL]，`prompt` = phase01 整份提示词（≤2000 字），`duration` = "12"。
- **段 2～N**：上一段尾帧截取后上传得 URL → `image_urls` = [尾帧URL]，`prompt` = 当前段提示词，`duration` = "12"。
- 若某段提示词超过 2000 字，需在 phase 文件中精简（如合并句子、缩短【项目·风格·规则】或负面词）。
