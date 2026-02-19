#!/usr/bin/env python3
"""
即梦 生图 API：按【即梦AI-图片生成4.0】接口生成首帧/尾帧图。参考图仅支持 URL，脚本将本地参考图上传至 ImgBB 后传 URL。
通过 scale 参数降低文本权重、让参考图更主导（scale 越小文本影响越小、参考图影响越大）。
文档：https://www.volcengine.com/docs/85621/1817045
.env：VOLCENGINE_ACCESS_KEY_ID、VOLCENGINE_SECRET_ACCESS_KEY、IMGBB_API_KEY
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional

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
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode("utf-8"))
            return (res.get("data") or {}).get("url")
    except Exception as e:
        print("ImgBB 上传失败 %s: %s" % (path, e), file=sys.stderr)
        return None


def _parse_resp(resp) -> dict:
    if isinstance(resp, bytes):
        return json.loads(resp.decode("utf-8"))
    if isinstance(resp, str):
        return json.loads(resp)
    return resp


def collect_refs_from_dir(refs_dir: str, project_root: str = "") -> tuple:
    root = os.path.abspath(project_root) if project_root else os.getcwd()
    refs_dir = os.path.join(root, refs_dir) if not os.path.isabs(refs_dir) else refs_dir
    exts = (".png", ".jpg", ".jpeg")
    char_paths, scene_paths = [], []
    for sub in ("characters", "scenes"):
        d = os.path.join(refs_dir, sub)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.lower().endswith(exts):
                    (char_paths if sub == "characters" else scene_paths).append(os.path.join(d, f))
    return char_paths, scene_paths


def build_ref_hint(first_frame: bool, n_char: int, characters_only: bool = True) -> str:
    if characters_only or n_char:
        if first_frame:
            return "【参考图说明】第1张为本段首帧（参考权重最高），其余均为人物/角色形象参考。人物在生图中具有绝对地位，必须严格按人物参考图还原脸型与身材，不得变形。"
        return "【参考图说明】以上参考图均为人物/角色形象参考。人物在生图中具有绝对地位，必须严格按人物参考图还原脸型与身材，场景由提示词描述、不得压过人物。"
    return ""


JIMENG_T2I_V40 = "jimeng_t2i_v40"
MAX_REF_IMAGES = 10
ASPECT_16_9_WIDTH = 1664
ASPECT_16_9_HEIGHT = 936


def submit_img_task_v40(
    service: VisualService,
    prompt: str,
    ref_url_list: List[str],
    width: int = ASPECT_16_9_WIDTH,
    height: int = ASPECT_16_9_HEIGHT,
    scale: float = 0.35,
) -> tuple:
    """提交即梦图片生成4.0。scale 越小文本权重越低、参考图权重越高（建议 0.3～0.4 以保人物一致）。"""
    form = {
        "req_key": JIMENG_T2I_V40,
        "prompt": prompt[:800],
        "seed": -1,
        "width": width,
        "height": height,
        "scale": scale,
    }
    if ref_url_list:
        form["image_urls"] = ref_url_list[:MAX_REF_IMAGES]
    resp = service.cv_sync2async_submit_task(form)
    resp = _parse_resp(resp) if not isinstance(resp, dict) else resp
    if resp.get("code") not in (10000, 0):
        print("生图提交失败:", resp, file=sys.stderr)
        sys.exit(1)
    data = resp.get("data", resp)
    task_id = data.get("task_id") or data.get("taskid") if isinstance(data, dict) else None
    if not task_id:
        sys.exit(1)
    return str(task_id), JIMENG_T2I_V40


def get_img_result(service: VisualService, task_id: str, req_key: str = JIMENG_T2I_V40) -> dict:
    form = {"req_key": req_key, "task_id": task_id}
    for attempt in range(3):
        try:
            resp = service.cv_sync2async_get_result(form)
            if resp is None or (isinstance(resp, bytes) and len(resp) == 0):
                raise ValueError("empty response")
            return _parse_resp(resp) if not isinstance(resp, dict) else resp
        except (Exception, json.JSONDecodeError):
            if attempt < 2:
                time.sleep(3)
                continue
            try:
                resp = service.cv_get_result(form)
                if resp is None or (isinstance(resp, bytes) and len(resp) == 0):
                    return {}
                return _parse_resp(resp) if not isinstance(resp, dict) else resp
            except Exception:
                return {}
    return {}


def poll_img_until_done(service: VisualService, task_id: str, req_key: str, interval: int = 5) -> dict:
    while True:
        resp = get_img_result(service, task_id, req_key)
        if not resp:
            print("生图状态: 查询无响应，%ds 后重试..." % interval, file=sys.stderr)
            time.sleep(interval)
            continue
        code = resp.get("code", -1)
        data = resp.get("data", resp) or {}
        status = data.get("status") if isinstance(data, dict) else None
        if code in (10000, 0) and status == "done":
            return data
        if isinstance(data, dict) and data.get("status") == "failed":
            print("生图失败:", resp, file=sys.stderr)
            sys.exit(1)
        print("生图状态:", status or "等待中", "，%ds 后重试..." % interval, file=sys.stderr)
        time.sleep(interval)


def read_prompt_from_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
    return " ".join(lines) if lines else ""


def main():
    parser = argparse.ArgumentParser(description="即梦 生图 4.0：仅人物图+首帧，scale 降低文本权重")
    parser.add_argument("--prompt", type=str, help="生图提示词（与 --prompt-file 二选一）")
    parser.add_argument("--prompt-file", type=str, help="生图提示词文件")
    parser.add_argument("--ref-images", nargs="+", default=[], help="参考图路径")
    parser.add_argument("--refs-dir", type=str, default=None, help="refs 目录，仅收集 characters/ 人物图")
    parser.add_argument("--first-frame", type=str, default=None, help="本段首帧图路径（尾帧生图时）")
    parser.add_argument("--output", type=str, default=None, help="生成图保存路径")
    parser.add_argument("--scale", type=float, default=0.35, help="文本相对参考图的权重，越小参考图越主导（默认0.35）")
    parser.add_argument("--aspect-ratio", type=str, default="16:9")
    parser.add_argument("--project-root", type=str, default=os.getcwd())
    parser.add_argument("--no-print-base64", action="store_true")
    args = parser.parse_args()

    if args.prompt_file:
        path = os.path.join(args.project_root, args.prompt_file) if not os.path.isabs(args.prompt_file) else args.prompt_file
        prompt = read_prompt_from_file(path)
        if not prompt:
            print("错误: 提示词文件为空或仅有注释:", args.prompt_file, file=sys.stderr)
            sys.exit(1)
    elif args.prompt:
        prompt = args.prompt
    else:
        parser.error("须指定 --prompt 或 --prompt-file")

    project_root = os.path.abspath(args.project_root)
    ak, sk = load_env(project_root)
    service = VisualService()
    service.set_ak(ak)
    service.set_sk(sk)

    ref_paths = []
    n_first = 0
    if args.first_frame:
        fp = args.first_frame if os.path.isabs(args.first_frame) else os.path.join(project_root, args.first_frame)
        if os.path.isfile(fp):
            ref_paths.append(fp)
            n_first = 1
    ref_paths.extend(args.ref_images or [])
    n_extra = len(ref_paths) - n_first
    char_paths, _ = [], []
    if args.refs_dir:
        char_paths, _ = collect_refs_from_dir(args.refs_dir, project_root)
        ref_paths.extend(char_paths)
    n_char = n_extra + len(char_paths)
    ref_hint = build_ref_hint(bool(n_first), n_char, characters_only=True)
    if ref_hint:
        prompt = (prompt + " " + ref_hint)[:800]

    ref_urls = []
    if ref_paths:
        imgbb_key = load_imgbb_key(project_root)
        if not imgbb_key:
            print("错误: 请在 .env 中配置 IMGBB_API_KEY。", file=sys.stderr)
            sys.exit(1)
        for i, p in enumerate(ref_paths[:MAX_REF_IMAGES]):
            abs_p = p if os.path.isabs(p) else os.path.join(project_root, p)
            if not os.path.isfile(abs_p):
                abs_p = os.path.abspath(p)
            url = upload_image_to_imgbb(abs_p, imgbb_key)
            if url:
                ref_urls.append(url)
                print("参考图 %d URL: %s" % (i + 1, url[:60] + "…"), file=sys.stderr)
        if ref_paths and not ref_urls:
            print("错误: 无参考图上传成功。", file=sys.stderr)
            sys.exit(1)

    w, h = ASPECT_16_9_WIDTH, ASPECT_16_9_HEIGHT
    if args.aspect_ratio == "16:9":
        w, h = ASPECT_16_9_WIDTH, ASPECT_16_9_HEIGHT
    task_id, req_key_used = submit_img_task_v40(service, prompt, ref_urls, width=w, height=h, scale=args.scale)
    print("生图 task_id:", task_id, "scale:", args.scale, file=sys.stderr)
    data = poll_img_until_done(service, task_id, req_key_used)

    image_b64 = None
    if isinstance(data, dict):
        image_b64 = data.get("binary_data_base64") or data.get("image_base64")
        if not image_b64 and isinstance(data.get("result"), dict):
            image_b64 = data["result"].get("binary_data_base64") or data["result"].get("image_base64")
        if not image_b64 and data.get("image_url"):
            import urllib.request
            with urllib.request.urlopen(data["image_url"]) as r:
                image_b64 = base64.b64encode(r.read()).decode("utf-8")
    if not image_b64:
        print("生图结果中未找到图片:", data, file=sys.stderr)
        sys.exit(1)
    if isinstance(image_b64, list) and image_b64:
        image_b64 = image_b64[0]

    if args.output:
        with open(args.output, "wb") as f:
            f.write(base64.b64decode(image_b64))
        print("已保存:", args.output, file=sys.stderr)
    if not args.no_print_base64:
        print(image_b64)


if __name__ == "__main__":
    main()
