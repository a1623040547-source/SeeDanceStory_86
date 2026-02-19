#!/usr/bin/env python3
"""
使用 Seedance 2.0 API 提交视频生成任务并轮询结果。
依赖：项目根目录 .env 中的 SEEDANCE_API_KEY；可选 dotenv。
用法：
  python generate.py --prompt-file section04/phases/phase01/phase01.txt --image-url "https://..." [--duration 12]
  # 从 phase 文件中读取「给 Seedance 的整份提示词」块时，需手动复制或使用 --prompt 直接传入
  python generate.py --prompt "【项目·风格·规则】..." --image-url "https://..." --duration 12
"""

import argparse
import os
import sys
import time
from typing import Optional

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://seedanceapi.org/v1"


def load_env(project_root: str) -> str:
    api_key = None
    env_path = os.path.join(project_root, ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("SEEDANCE_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not api_key:
        print("错误: 未找到 SEEDANCE_API_KEY，请在项目根目录 .env 中配置。", file=sys.stderr)
        sys.exit(1)
    return api_key


def extract_prompt_from_phase_file(path: str) -> str:
    """从 phase 文件中提取【项目·风格·规则】～【负面词】及其后一行（不要…）的整份提示词。"""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    start_marker = "【项目·风格·规则】"
    if start_marker not in content:
        print("错误: phase 文件中未找到【项目·风格·规则】。", file=sys.stderr)
        sys.exit(1)
    start = content.index(start_marker)
    neg_label = "【负面词】"
    if neg_label not in content[start:]:
        prompt = content[start:].strip()
    else:
        neg_pos = content.index(neg_label, start)
        # 包含【负面词】及下一行（通常为「不要…」）
        rest = content[neg_pos:]
        lines = rest.split("\n")
        end_off = 0
        for i, line in enumerate(lines):
            end_off += len(line) + 1
            if i == 0:
                continue  # 【负面词】行
            if "不要" in line or (line.strip() and i <= 2):
                break
        prompt = content[start : neg_pos + end_off].strip()
    if len(prompt) > 2000:
        print(f"警告: 提示词长度 {len(prompt)} 超过 API 限制 2000，将截断。", file=sys.stderr)
        prompt = prompt[:2000]
    return prompt


def submit(api_key: str, prompt: str, image_url: Optional[str], duration: str = "12", aspect_ratio: str = "16:9", resolution: str = "720p", generate_audio: bool = False) -> str:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "generate_audio": generate_audio,
    }
    if image_url:
        body["image_urls"] = [image_url]
    r = requests.post(f"{BASE_URL}/generate", json=body, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 200:
        print("API 返回错误:", data, file=sys.stderr)
        sys.exit(1)
    return data["data"]["task_id"]


def poll(api_key: str, task_id: str, interval: int = 5) -> dict:
    headers = {"Authorization": f"Bearer {api_key}"}
    while True:
        r = requests.get(f"{BASE_URL}/status", params={"task_id": task_id}, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 200:
            print("status API 返回错误:", data, file=sys.stderr)
            sys.exit(1)
        d = data["data"]
        status = d.get("status")
        if status == "SUCCESS":
            return d
        if status == "FAILED":
            print("任务失败:", d.get("error_message"), file=sys.stderr)
            sys.exit(1)
        print(f"状态: {status}，{interval}s 后重试...")
        time.sleep(interval)


def status_once(api_key: str, task_id: str) -> dict:
    """查询一次任务状态并返回 data，不轮询。"""
    headers = {"Authorization": f"Bearer {api_key}"}
    r = requests.get(f"{BASE_URL}/status", params={"task_id": task_id}, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 200:
        print("API 返回错误:", data, file=sys.stderr)
        sys.exit(1)
    return data["data"]


def main():
    parser = argparse.ArgumentParser(description="Seedance 2.0 API 提交并轮询视频生成")
    parser.add_argument("--prompt", type=str, help="完整提示词（≤2000 字）")
    parser.add_argument("--prompt-file", type=str, help="phase 文件路径，将从中提取提示词块")
    parser.add_argument("--image-url", type=str, help="参考图公网 URL（仅 1 张）")
    parser.add_argument("--duration", type=str, default="12", choices=["4", "8", "12"])
    parser.add_argument("--aspect-ratio", type=str, default="16:9")
    parser.add_argument("--resolution", type=str, default="720p", choices=["480p", "720p"])
    parser.add_argument("--generate-audio", action="store_true", help="启用 AI 生成音频（默认关闭）")
    parser.add_argument("--project-root", type=str, default=os.getcwd())
    parser.add_argument("--no-poll", action="store_true", help="仅提交，不轮询结果（可后用 --task-id 查进度）")
    parser.add_argument("--task-id", type=str, help="仅查询该任务状态（可重复执行查进度）；若带上 --wait 则轮询直到完成")
    parser.add_argument("--wait", action="store_true", help="与 --task-id 同用：轮询直到 SUCCESS/FAILED 并打印视频 URL")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    api_key = load_env(project_root)

    if args.task_id:
        if args.wait:
            result = poll(api_key, args.task_id)
            urls = result.get("response") or []
            if urls:
                print("视频 URL:", urls[0])
            else:
                print("未返回视频 URL:", result)
        else:
            d = status_once(api_key, args.task_id)
            print("status:", d.get("status"))
            if d.get("response"):
                print("视频 URL:", d["response"][0])
            elif d.get("error_message"):
                print("error_message:", d["error_message"])
        return

    if not args.prompt and not args.prompt_file:
        parser.error("请指定 --prompt 或 --prompt-file（或使用 --task-id 查询进度）")
    if args.prompt_file:
        prompt = extract_prompt_from_phase_file(os.path.join(project_root, args.prompt_file) if not os.path.isabs(args.prompt_file) else args.prompt_file)
    else:
        prompt = args.prompt
        if len(prompt) > 2000:
            print("警告: 提示词超过 2000 字，将截断。", file=sys.stderr)
            prompt = prompt[:2000]

    task_id = submit(api_key, prompt, args.image_url, args.duration, args.aspect_ratio, args.resolution, args.generate_audio)
    print(f"task_id: {task_id}")

    if args.no_poll:
        print("已提交。查进度: python generate.py --task-id " + task_id + " --project-root " + project_root)
        print("完成后取视频: python generate.py --task-id " + task_id + " --wait --project-root " + project_root)
        return

    result = poll(api_key, task_id)
    urls = result.get("response") or []
    if urls:
        print("视频 URL:", urls[0])
    else:
        print("未返回视频 URL:", result)


if __name__ == "__main__":
    main()
