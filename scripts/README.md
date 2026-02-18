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
