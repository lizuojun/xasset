#!/usr/bin/env python
"""本地环境探测 —— 一次运行，输出能力清单。

**为什么有这个脚本**：
    以前每次要判断"本地能不能跑 X"，都要临时查硬件、试端点、看依赖。
    现在跑一次就有完整答案，且可与其他时间点的结果对比。

用法：
    python scripts/probe_env.py              # 打印报告
    python scripts/probe_env.py --json       # 输出 JSON（可与 docs/env-capabilities.json 对比）

与 docs/env-capabilities.json 的关系：
    - 该 JSON 是**某一次探测的快照**（人工整理的结论）
    - 本脚本是**可重复的探测器**（环境变了就重跑，看差异）
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path


def probe_cpu_memory() -> dict:
    """CPU 核心与内存（不依赖 WMI）。"""
    info = {
        "logical_cores": os.cpu_count(),
        "architecture": platform.machine(),
        "os": platform.system() + " " + platform.release(),
    }
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            info["memory_total_gb"] = round(stat.ullTotalPhys / 1024**3, 1)
            info["memory_available_gb"] = round(stat.ullAvailPhys / 1024**3, 1)
    except Exception as e:
        info["memory_error"] = str(e)
    return info


def probe_gpu() -> dict:
    """NVIDIA GPU（通过 nvidia-smi）。"""
    smi = shutil.which("nvidia-smi") or "C:\\Windows\\System32\\nvidia-smi.exe"
    if not Path(smi).exists() and not shutil.which("nvidia-smi"):
        return {"available": False, "reason": "nvidia-smi 不存在"}
    try:
        out = subprocess.run(
            [smi, "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        line = out.stdout.strip().splitlines()[0] if out.stdout.strip() else ""
        if not line:
            return {"available": False, "reason": "nvidia-smi 无输出"}
        name, mem = [x.strip() for x in line.split(",")]
        vram_mb = int(mem.replace("MiB", "").strip())
        return {
            "available": True,
            "name": name,
            "vram_gb": round(vram_mb / 1024, 1),
        }
    except Exception as e:
        return {"available": False, "reason": str(e)}


def probe_llm_endpoints() -> dict:
    """LLM 端点：Anthropic 代理 + Ollama。"""
    result: dict = {}

    base = os.environ.get("ANTHROPIC_BASE_URL")
    result["anthropic_proxy"] = {
        "configured": bool(base),
        "base_url": base,
        "auth_token_set": bool(
            os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
        ),
    }
    if base:
        result["anthropic_proxy"]["reachable"] = _http_head_ok(base)

    # Ollama
    ollama_cli = shutil.which("ollama")
    result["ollama"] = {
        "installed": bool(ollama_cli),
        "cli": ollama_cli,
        "models_dir": os.environ.get("OLLAMA_MODELS"),
        "service_running": _ollama_running(),
        "models": _ollama_models() if _ollama_running() else [],
    }
    return result


def _http_head_ok(url: str, timeout: float = 5.0) -> bool:
    """端点是否可达（任何 HTTP 响应都算可达）。"""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if not host:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _ollama_running() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 11434), timeout=3):
            return True
    except OSError:
        return False


def _ollama_models() -> list[str]:
    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5) as r:
            data = json.loads(r.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def probe_python_env() -> dict:
    """Python 依赖情况。"""
    deps = {}
    for mod in ("torch", "transformers", "cv2", "onnxruntime",
                "anthropic", "openai", "numpy", "PIL", "pydantic"):
        try:
            m = __import__(mod)
            deps[mod] = getattr(m, "__version__", "installed")
        except ImportError:
            deps[mod] = None
    return {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "deps": deps,
    }


def probe_disk() -> dict:
    """各盘剩余空间。"""
    out = {}
    for drive in "CDEFGK":
        p = Path(f"{drive}:\\")
        if p.exists():
            try:
                usage = shutil.disk_usage(p)
                out[drive] = round(usage.free / 1024**3, 1)
            except OSError:
                pass
    return out


def collect() -> dict:
    return {
        "hardware": {
            "cpu": probe_cpu_memory(),
            "gpu": probe_gpu(),
            "disk_free_gb": probe_disk(),
        },
        "llm": probe_llm_endpoints(),
        "python": probe_python_env(),
    }


def print_report(d: dict) -> None:
    def line(k, v):
        print(f"  {k:<28} {v}")

    print("=" * 70)
    print("本地环境探测报告")
    print("=" * 70)

    hw = d["hardware"]
    print("\n[硬件]")
    line("CPU 逻辑核心", hw["cpu"].get("logical_cores"))
    line("架构 / OS", f"{hw['cpu'].get('architecture')} / {hw['cpu'].get('os')}")
    line("内存 总/可用 (GB)",
         f"{hw['cpu'].get('memory_total_gb')} / {hw['cpu'].get('memory_available_gb')}")
    g = hw["gpu"]
    line("GPU", f"{g.get('name')} ({g.get('vram_gb')} GB)" if g.get("available")
         else f"不可用 - {g.get('reason')}")
    line("磁盘剩余 (GB)", hw["disk_free_gb"])

    print("\n[LLM 资源]")
    a = d["llm"]["anthropic_proxy"]
    if a["configured"]:
        line("Anthropic 代理", a["base_url"])
        line("  可达", a.get("reachable"))
        line("  auth token 已配", a["auth_token_set"])
    else:
        line("Anthropic 代理", "未配置")
    o = d["llm"]["ollama"]
    line("Ollama 已装", o["installed"])
    line("  CLI", o["cli"])
    line("  服务运行中", o["service_running"])
    if o["models"]:
        line("  可用模型", ", ".join(o["models"]))
    elif o["installed"]:
        line("  可用模型", "(服务未运行，无法列出)")

    print("\n[Python 依赖]")
    py = d["python"]
    line("Python", py["python"])
    for k, v in py["deps"].items():
        if v:
            line(f"  {k}", v)
    missing = [k for k, v in py["deps"].items() if not v]
    if missing:
        line("  未安装", ", ".join(missing))

    print("\n" + "=" * 70)


def main() -> int:
    d = collect()
    if "--json" in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=2, default=str))
    else:
        print_report(d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
