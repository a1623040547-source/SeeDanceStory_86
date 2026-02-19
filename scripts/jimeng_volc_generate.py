#!/usr/bin/env python3
"""
使用火山引擎即梦 API（CV 视觉服务）提交视频生成任务并轮询结果。
依赖：pip install volcengine；.env 中配置 VOLCENGINE_ACCESS_KEY_ID、VOLCENGINE_SECRET_ACCESS_KEY。
即梦 3.0 720P 图生视频首帧：req_key=jimeng_i2v_first_v30。支持首帧图传 URL 或 base64（无需上传到网络）。
文档：https://www.volcengine.com/docs/85621/1785204

用法：
  python scripts/jimeng_volc_generate.py --prompt-file section04/phases/phase01/phase01.txt --image-url "https://..." [--no-poll]
  python scripts/jimeng_volc_generate.py --prompt-file ... --image-base64 "$(cat base64.txt)"   # 首帧图 base64
  python scripts/jimeng_volc_generate.py --task-id <task_id> [--wait]   # 查进度
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from typing import Optional

try:
    from volcengine.visual.VisualService import VisualService
except ImportError:
    print("请安装 volcengine: pip install volcengine", file=sys.stderr)
    sys.exit(1)


def load_env(project_root: str) -> tuple:
    ak, sk = None, None
    env_path = os.path.join(project_root, ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("VOLCENGINE_ACCESS_KEY_ID="):
                    ak = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("VOLCENGINE_SECRET_ACCESS_KEY="):
                    sk = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not ak or not sk:
        print("错误: 请在 .env 中配置 VOLCENGINE_ACCESS_KEY_ID 和 VOLCENGINE_SECRET_ACCESS_KEY。", file=sys.stderr)
        sys.exit(1)
    return ak, sk


def load_imgbb_key(project_root: str) -> Optional[str]:
    env_path = os.path.join(project_root, ".env")
    if not os.path.isfile(env_path):
        return None
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("IMGBB_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def upload_image_to_imgbb(path: str, api_key: str) -> Optional[str]:
    path = os.path.abspath(path) if not os.path.isabs(path) else path
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    data = urllib.parse.urlencode({"key": api_key, "image": b64}).encode("utf-8")
    req = urllib.request.Request("https://api.imgbb.com/1/upload", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.loads(r.read().decode("utf-8"))
            data_obj = res.get("data") or {}
            return data_obj.get("url") or (data_obj.get("image") or {}).get("url")
    except Exception as e:
        print("ImgBB 上传失败 %s: %s" % (path, e), file=sys.stderr)
        return None


def extract_prompt_from_phase_file(path: str) -> str:
    """从 phase 文件中提取【项目·风格·规则】～【负面词】及后一行。"""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    start_marker = "【项目·风格·规则】"
    if start_marker not in content:
        print("错误: phase 文件中未找到【项目·风格·规则】。", file=sys.stderr)
        sys.exit(1)
    start = content.index(start_marker)
    neg_label = "【负面词】"
    if neg_label not in content[start:]:
        return content[start:].strip()
    neg_pos = content.index(neg_label, start)
    rest = content[neg_pos:]
    lines = rest.split("\n")
    end_off = 0
    for i, line in enumerate(lines):
        end_off += len(line) + 1
        if i > 0 and ("不要" in line or (line.strip() and i <= 2)):
            break
    return content[start : neg_pos + end_off].strip()


def _parse_resp(resp):
    if isinstance(resp, bytes):
        return json.loads(resp.decode("utf-8"))
    if isinstance(resp, str):
        return json.loads(resp)
    return resp


def submit_jimeng(service: VisualService, prompt: str, image_url: Optional[str] = None, image_base64: Optional[str] = None, frames: int = 121, aspect_ratio: str = "16:9") -> str:
    """即梦 3.0 720P 图生视频首帧，返回 task_id。比例默认 16:9（长:宽）。"""
    form = {
        "req_key": "jimeng_i2v_first_v30",
        "prompt": prompt[:800],
        "frames": frames,
        "seed": -1,
        "aspect_ratio": aspect_ratio,
    }
    if image_base64:
        form["image_urls"] = [{"binary_data_base64": image_base64}]
    elif image_url:
        form["image_urls"] = [image_url]
    else:
        raise ValueError("须提供 image_url 或 image_base64 之一")
    try:
        resp = service.cv_sync2async_submit_task(form)
    except Exception as e:
        err_str = str(e).strip()
        if "50400" in err_str or "Access Denied" in err_str:
            print("即梦 API 返回 50400：请在控制台为当前 AK 授予「视觉智能」或「即梦AI」相关 IAM 权限。", file=sys.stderr)
        raise
    resp = _parse_resp(resp) if not isinstance(resp, dict) else resp
    if resp.get("code") != 10000 and resp.get("code") != 0:
        print("提交失败:", resp, file=sys.stderr)
        sys.exit(1)
    data = resp.get("data", resp)
    task_id = data.get("task_id") if isinstance(data, dict) else None
    task_id = task_id or (isinstance(data, dict) and data.get("taskid")) or resp.get("task_id")
    if not task_id:
        print("响应中未找到 task_id:", resp, file=sys.stderr)
        sys.exit(1)
    return str(task_id)


def get_result(service: VisualService, task_id: str) -> dict:
    """查询一次任务结果。"""
    form = {"req_key": "jimeng_i2v_first_v30", "task_id": task_id}
    try:
        resp = service.cv_sync2async_get_result(form)
    except Exception:
        resp = service.cv_get_result(form)
    if isinstance(resp, bytes):
        resp = json.loads(resp.decode("utf-8"))
    elif isinstance(resp, str):
        resp = json.loads(resp)
    return resp


def poll_until_done(service: VisualService, task_id: str, interval: int = 10, max_wait_sec: int = 600) -> dict:
    """轮询直到成功或失败。status 为 done/success 或 task_status==2 视为成功。"""
    start = time.time()
    while True:
        if max_wait_sec and (time.time() - start) > max_wait_sec:
            print("超时（%ds），退出轮询。" % max_wait_sec, file=sys.stderr)
            sys.exit(1)
        try:
            resp = get_result(service, task_id)
        except Exception as e:
            print("查询结果失败（将重试）:", e, file=sys.stderr)
            time.sleep(interval)
            continue
        code = resp.get("code", -1)
        data = resp.get("data", resp)
        if not isinstance(data, dict):
            data = resp
        status = (data.get("status") or "").lower() if isinstance(data, dict) else None
        task_status = data.get("task_status") if isinstance(data, dict) else None
        if code == 10000 or code == 0:
            if status in ("success", "done") or task_status == 2:
                return data
            if status == "failed" or task_status == 3:
                print("任务失败:", resp, file=sys.stderr)
                sys.exit(1)
        print("状态:", status or task_status, "，%ds 后重试..." % interval)
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="火山引擎即梦 API 视频生成")
    parser.add_argument("--prompt", type=str, help="提示词")
    parser.add_argument("--prompt-file", type=str, help="phase 文件路径")
    parser.add_argument("--image-url", type=str, help="首帧图公网 URL（1 张）")
    parser.add_argument("--image-base64", type=str, help="首帧图 base64（与 --image-url/--image 二选一）")
    parser.add_argument("--image", type=str, help="首帧图本地路径，脚本内转为 base64（避免命令行过长）")
    parser.add_argument("--frames", type=int, default=121, help="总帧数 121=5s 241=10s")
    parser.add_argument("--aspect-ratio", type=str, default="16:9", help="视频比例 16:9（长:宽）")
    parser.add_argument("--project-root", type=str, default=os.getcwd())
    parser.add_argument("--no-poll", action="store_true", help="仅提交不轮询")
    parser.add_argument("--output", "-o", type=str, help="成功后将视频下载保存到该路径")
    parser.add_argument("--task-id", type=str, help="仅查询该任务")
    parser.add_argument("--wait", action="store_true", help="与 --task-id 同用：轮询直到完成")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    ak, sk = load_env(project_root)
    service = VisualService()
    service.set_ak(ak)
    service.set_sk(sk)

    if args.task_id:
        if args.wait:
            data = poll_until_done(service, args.task_id)
            video_url = None
            if isinstance(data, dict):
                video_url = data.get("video_url") or (data.get("result") or {}).get("video_url") or data.get("url")
                if isinstance(data.get("result"), dict):
                    video_url = video_url or data["result"].get("video_url")
            if video_url:
                print("视频 URL:", video_url)
                if args.output:
                    import urllib.request
                    out_path = os.path.join(project_root, args.output) if not os.path.isabs(args.output) else args.output
                    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
                    urllib.request.urlretrieve(video_url, out_path)
                    print("已保存:", out_path)
            else:
                print("响应:", data)
        else:
            resp = get_result(service, args.task_id)
            print(json.dumps(resp, ensure_ascii=False, indent=2))
        return

    if not args.prompt and not args.prompt_file:
        parser.error("请指定 --prompt 或 --prompt-file（或使用 --task-id 查询）")
    if args.prompt_file:
        path = os.path.join(project_root, args.prompt_file) if not os.path.isabs(args.prompt_file) else args.prompt_file
        prompt = extract_prompt_from_phase_file(path)
    else:
        prompt = args.prompt
    image_url = args.image_url
    image_base64 = args.image_base64
    if args.image:
        img_path = os.path.join(project_root, args.image) if not os.path.isabs(args.image) else args.image
        if not os.path.isfile(img_path):
            print("错误: 首帧图不存在:", img_path, file=sys.stderr)
            sys.exit(1)
        # 即梦视频 API 的 image_urls 只接受 URL，不接受 base64；先上传到 ImgBB 取 URL
        imgbb_key = load_imgbb_key(project_root)
        if not imgbb_key:
            print("错误: 使用 --image 须在 .env 中配置 IMGBB_API_KEY（上传首帧图取 URL）。", file=sys.stderr)
            sys.exit(1)
        image_url = upload_image_to_imgbb(img_path, imgbb_key)
        if not image_url:
            sys.exit(1)
        print("首帧图已上传，URL:", image_url)
        image_base64 = None
    if not image_url and not image_base64:
        parser.error("即梦图生视频首帧需要 --image-url、--image-base64 或 --image 之一")

    task_id = submit_jimeng(service, prompt, image_url=image_url, image_base64=image_base64, frames=args.frames, aspect_ratio=args.aspect_ratio)
    print("task_id:", task_id)

    if args.no_poll:
        print("已提交。查进度: python scripts/jimeng_volc_generate.py --task-id", task_id, "--project-root", project_root)
        return

    data = poll_until_done(service, task_id)
    video_url = data.get("video_url") or (data.get("result") or {}).get("video_url") if isinstance(data, dict) else None
    if isinstance(data.get("result"), dict):
        video_url = video_url or data["result"].get("video_url")
    if not video_url and isinstance(data, dict):
        for k in ("url", "video_url"):
            if data.get(k):
                video_url = data[k]
                break
    if video_url:
        print("视频 URL:", video_url)
        if args.output:
            import urllib.request
            out_path = os.path.join(project_root, args.output) if not os.path.isabs(args.output) else args.output
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            urllib.request.urlretrieve(video_url, out_path)
            print("已保存:", out_path)
    else:
        print("响应:", data)


if __name__ == "__main__":
    main()
