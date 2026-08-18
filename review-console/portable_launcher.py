from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from tkinter import Tk, messagebox, simpledialog


def _save_user_environment(name: str, value: str) -> None:
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        "Environment",
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)


def _ensure_api_key() -> bool:
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return True
    if os.environ.get("REVIEW_PORTABLE_TEST_MODE") == "1":
        return True

    root = Tk()
    root.withdraw()
    key = simpledialog.askstring(
        "方案评审 Agent",
        "首次使用，请输入你自己的 DeepSeek API Key：",
        show="*",
        parent=root,
    )
    if not key or len(key.strip()) < 12:
        messagebox.showwarning("未配置 API Key", "未保存密钥，程序将退出。", parent=root)
        root.destroy()
        return False

    key = key.strip()
    _save_user_environment("DEEPSEEK_API_KEY", key)
    _save_user_environment("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    _save_user_environment("DEEPSEEK_MODEL", "deepseek-v4-flash")
    os.environ["DEEPSEEK_API_KEY"] = key
    os.environ["DEEPSEEK_BASE_URL"] = "https://api.deepseek.com"
    os.environ["DEEPSEEK_MODEL"] = "deepseek-v4-flash"
    root.destroy()
    return True


def _prepare_runtime() -> None:
    install_root = Path(
        os.environ.get(
            "REVIEW_PORTABLE_ROOT",
            Path(sys.executable).parent if getattr(sys, "frozen", False) else Path.cwd(),
        )
    ).resolve()
    runtime_root = install_root / "方案评审数据"
    os.environ.setdefault("REVIEW_CONSOLE_DATA_PATH", str(runtime_root / "工作台数据"))
    os.environ.setdefault("REVIEW_PROJECTS_PATH", str(runtime_root / "项目记录"))
    os.environ.setdefault("OBSIDIAN_VAULT_PATH", str(runtime_root / "Obsidian运行数据"))
    for name in ("工作台数据", "项目记录", "Obsidian运行数据"):
        (runtime_root / name).mkdir(parents=True, exist_ok=True)


def main() -> None:
    if not _ensure_api_key():
        return
    _prepare_runtime()

    import app

    port = int(os.environ.get("REVIEW_CONSOLE_PORT", "8765"))
    url = f"http://127.0.0.1:{port}"

    def open_when_ready() -> None:
        time.sleep(1.0)
        webbrowser.open(url)

    threading.Thread(target=open_when_ready, daemon=True).start()
    app.main()


if __name__ == "__main__":
    main()
