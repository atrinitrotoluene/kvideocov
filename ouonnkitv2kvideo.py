#!/usr/bin/env python3
"""
ouonnkitv2kvideo — 将 OuonnkiTV 视频源格式转为 KVideo 视频源 JSON 格式

OuonnkiTV 格式 (输入):
  [
    { "id": "source1", "name": "示例视频源", "url": "https://...",
      "detailUrl": "https://...", "isEnabled": true }
  ]

KVideo 视频源格式 (输出):
  [
    { "id": "feifan", "name": "非凡资源", "baseUrl": "https://...",
      "group": "normal", "enabled": true, "priority": 1 }
  ]

默认 OuonnkiTV 源 URL:
  https://raw.githubusercontent.com/Yesbaiwan/OuonnkiTV-Source/main/tv_source/OuonnkiTV/full.json

用法:
  # 从默认源抓取并转换
  python ouonnkitv2kvideo.py --fetch -o kvideo_sources.json

  # 从自定义 URL 抓取并转换
  python ouonnkitv2kvideo.py --fetch https://example.com/sources.json -o output.json

  # 转换本地文件
  python ouonnkitv2kvideo.py input.json -o output.json

  # 输出到终端
  python ouonnkitv2kvideo.py input.json --stdout

  # 自定义分组
  python ouonnkitv2kvideo.py --fetch --group premium -o output.json
"""

import json
import sys
import re
import argparse
import os
import urllib.request
import urllib.error

DEFAULT_SOURCE_URL = (
    "https://raw.githubusercontent.com/Yesbaiwan/"
    "OuonnkiTV-Source/main/tv_source/OuonnkiTV/full.json"
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "kvideo_sources.json")


def slugify(text: str) -> str:
    """将文本转为 kebab-case 的 id"""
    s = text.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = s.strip("-")
    return s if s else f"source-{abs(hash(text)) % 10000}"


def convert_source(entry: dict, index: int, group: str = "normal",
                   start_priority: int = 1) -> dict:
    """将单个 OuonnkiTV 源条目转为 KVideo 格式"""
    if "name" not in entry or "url" not in entry:
        raise ValueError(f"条目缺少 'name' 或 'url' 字段: "
                         f"{json.dumps(entry, ensure_ascii=False)}")

    source_id = entry.get("id") or slugify(entry["name"])
    priority = entry.get("priority", start_priority + index)

    return {
        "id": source_id,
        "name": entry["name"],
        "baseUrl": entry["url"],
        "group": group,
        "enabled": entry.get("isEnabled", True),
        "priority": priority,
    }


def fetch_json(url: str) -> list:
    """从 URL 抓取 JSON 并解析"""
    req = urllib.request.Request(url, headers={
        "User-Agent": "ouonnkitv2kvideo/1.0",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"错误: HTTP {e.code} — {url}", file=sys.stderr)
        sys.exit(1)
    except (urllib.error.URLError, OSError) as e:
        print(f"错误: 无法连接 — {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: 返回的不是有效 JSON — {e}", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        print("错误: JSON 应为对象或对象数组", file=sys.stderr)
        sys.exit(1)
    return data


def read_file(path: str) -> list:
    """从本地文件读取 JSON"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件不存在 — {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: 文件不是有效 JSON — {e}", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        print("错误: JSON 应为对象或对象数组", file=sys.stderr)
        sys.exit(1)
    return data


def convert_all(entries: list, group: str, start_priority: int) -> list:
    """批量转换，跳过无效条目"""
    converted = []
    for i, entry in enumerate(entries):
        try:
            src = convert_source(entry, i, group, start_priority)
            converted.append(src)
        except ValueError as e:
            print(f"警告: 跳过第 {i+1} 项 — {e}", file=sys.stderr)
            continue
    return converted


def write_output(data: list, output_path: str | None):
    """输出 JSON 到文件或终端"""
    json_str = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)
    if not output_path or output_path == "-":
        print(json_str, end="")


def main():
    parser = argparse.ArgumentParser(
        description="将 OuonnkiTV 视频源 JSON 格式转为 KVideo 视频源 JSON 格式"
    )
    parser.add_argument(
        "input", nargs="?",
        help="输入 JSON 文件路径或 URL（缺省时与 --fetch 配合使用默认源）"
    )
    parser.add_argument("-o", "--output",
                        help="输出文件路径（默认: kvideo_sources.json）")
    parser.add_argument("--stdout", action="store_true",
                        help="输出到 stdout")
    parser.add_argument("--fetch", action="store_true",
                        help="从远程 URL 抓取（缺省 input 时用默认源 URL）")
    parser.add_argument("--group", default="normal",
                        help="KVideo 分组名称（默认: normal）")
    parser.add_argument("--start-priority", type=int, default=1,
                        help="起始优先级序号（默认: 1）")

    args = parser.parse_args()

    # 确定输入来源
    if args.fetch:
        source_url = args.input or DEFAULT_SOURCE_URL
        print(f"🌐 正在抓取: {source_url}", file=sys.stderr)
        raw = fetch_json(source_url)
        print(f"   抓取到 {len(raw)} 个条目", file=sys.stderr)
    elif args.input:
        if args.input.startswith(("http://", "https://")):
            raw = fetch_json(args.input)
        else:
            raw = read_file(args.input)
    else:
        parser.print_help()
        print("\n错误: 请指定输入文件，或使用 --fetch 从远程抓取", file=sys.stderr)
        sys.exit(1)

    # 转换
    converted = convert_all(raw, args.group, args.start_priority)

    if not converted:
        print("错误: 没有成功转换任何条目", file=sys.stderr)
        sys.exit(1)

    print(f"✓ 成功转换 {len(converted)}/{len(raw)} 个条目", file=sys.stderr)

    # 输出
    output_path = None if args.stdout else (args.output or DEFAULT_OUTPUT)
    write_output(converted, output_path)

    if output_path:
        print(f"📄 输出文件: {output_path}", file=sys.stderr)
        print(f"\n💡 KVideo 订阅链接:\n"
              f"   https://raw.githubusercontent.com/<你的用户名>/<仓库名>/main/"
              f"{os.path.basename(output_path)}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
