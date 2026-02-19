# 脚本说明

## 获取图片公网链接（供 Seedance 等 API 使用）

Seedance API 需要传**图片链接**时，可用以下方式之一得到公网可访问的 URL。

### 方式一：ImgBB 图床（推荐，无需自建）

不依赖自己的服务器，上传到 ImgBB 后直接得到直链。

1. 到 [https://api.imgbb.com/](https://api.imgbb.com/) 免费申请 API Key。
2. 在项目根目录的 `.env` 中增加一行（勿提交）：
   ```bash
   IMGBB_API_KEY=你的key
   ```
3. 运行：
   ```bash
   ./scripts/upload-image-url.sh section02/refs/characters/section02_character_ref_03.jpeg
   ```
4. 终端会输出直链，复制到 Seedance 的图片 URL 参数即可。

### 方式二：自建服务器

若你有可公网访问的服务器，可使用 `upload-image.sh`，在 `scripts/upload-config.local` 中配置 `SSH_HOST`、`REMOTE_PATH`、`HTTP_BASE_URL` 后执行：

```bash
./scripts/upload-image.sh <图片路径>
```

输出即为对应文件的 HTTP(S) 链接。

---

## 火山引擎即梦 API 视频生成

使用火山引擎即梦 3.0（图生视频首帧）生成视频，需 AK/SK 认证。

1. 在项目根目录 `.env` 中配置（勿提交）：
   ```bash
   VOLCENGINE_ACCESS_KEY_ID=你的AccessKeyId
   VOLCENGINE_SECRET_ACCESS_KEY=你的SecretAccessKey
   ```
   密钥在 [火山引擎控制台 - 访问密钥](https://console.volcengine.com/iam/keymanage/) 创建。

2. 安装依赖：`pip install volcengine`

3. 首帧图须为公网 URL，可用 `upload-image-url.sh` 上传后得到。

4. 提交任务（不轮询）：
   ```bash
   python scripts/jimeng_volc_generate.py --prompt-file section04/phases/phase01/phase01.txt --image-url "https://..." --no-poll --project-root .
   ```
5. 查进度：`python scripts/jimeng_volc_generate.py --task-id <task_id> --project-root .`  
   轮询直到完成：加 `--wait`。

**首帧用 base64、无需上传图床**：可用 `--image-base64` 传入首帧图 base64（例如由生图 API 生成后管道传入）。

**第一段一键流程（生图→视频）**：即梦生图生成首帧（refs 目录下角色+环境多图参考），再以 base64 传入图生视频，全程无需上传图片到网络：
```bash
python scripts/jimeng_volc_phase01.py --project-root .
```
- 生图使用 **即梦AI-图片生成4.0** 接口，参考图仅支持 URL（脚本用 ImgBB 上传后传 URL）。**生图时只传人物图**（不传环境图），可传 `--scale` 降低文本权重。段 1 仅生首帧图，尾帧由本段视频截取，不单独生尾帧图。
- 生图脚本：`scripts/jimeng_volc_img.py`。.env 需：`VOLCENGINE_ACCESS_KEY_ID`、`VOLCENGINE_SECRET_ACCESS_KEY`、`IMGBB_API_KEY`。
