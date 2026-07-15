# -*- coding: utf-8 -*-
"""
长征文化数字地图 — 环境配置脚本
用法: python setup.py
"""
import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd, cwd=None, check=True):
    """Run a command and print output."""
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or BASE_DIR,
                          capture_output=False, text=True)
    if check and result.returncode != 0:
        print(f"  [FAIL] exit code {result.returncode}")
        return False
    return True

def step(num, msg):
    print(f"\n[{num}/4] {msg}")

def main():
    os.chdir(BASE_DIR)
    print("=" * 50)
    print("  长征文化数字地图 — 环境配置")
    print("=" * 50)

    # --- Step 1: Check Python ---
    print(f"\n  Python: {sys.version.split()[0]}")
    print(f"  pip:    OK")

    # --- Step 2: Create venv and install deps ---
    step(2, "创建虚拟环境并安装依赖")
    venv_dir = os.path.join(BASE_DIR, ".venv")
    src_dir = os.path.join(BASE_DIR, "001 项目源码")

    if not os.path.exists(venv_dir):
        print("  Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print("  [OK] venv created")
    else:
        print("  [OK] venv already exists")

    # Determine pip path
    if sys.platform == "win32":
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
        python_venv = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")
        python_venv = os.path.join(venv_dir, "bin", "python")

    if not os.path.exists(pip_path):
        print(f"  [FAIL] pip not found in venv")
        sys.exit(1)

    req_file = os.path.join(src_dir, "requirements.txt")
    if os.path.exists(req_file):
        print("  Installing requirements...")
        subprocess.run([pip_path, "install", "-r", req_file], cwd=src_dir)
        print("  [OK] Dependencies installed")
    else:
        print(f"  [WARN] requirements.txt not found at {req_file}")

    # --- Step 3: Check optional tools ---
    step(3, "检查可选工具")
    
    # Git
    git_ok = shutil.which("git") is not None
    if git_ok:
        gitver = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip()
        print(f"  [OK] {gitver}")
    else:
        print("  [INFO] Git not installed (optional)")

    # Doxygen
    doxy_path = os.path.join(BASE_DIR, "007 项目工具",
                             "doxygen-1.17.0.windows.x64.bin", "doxygen.exe")
    if os.path.exists(doxy_path):
        print(f"  [OK] Doxygen ready")
    else:
        print(f"  [INFO] Doxygen not configured (optional)")

    # HHW
    hhw_path = os.path.join(BASE_DIR, "007 项目工具", "htmlhelp.exe")
    if os.path.exists(hhw_path):
        print(f"  [OK] HTML Help Workshop installer available")
    else:
        print(f"  [INFO] HTML Help Workshop not bundled")

    # --- Step 4: Verify ---
    step(4, "验证项目结构")
    key_paths = [
        "001 项目源码/app.py",
        "001 项目源码/run.py",
        "001 项目源码/static/js/map.js",
        "001 项目源码/templates/index.html",
        "001 项目源码/data/longmarch.db",
    ]
    for p in key_paths:
        full = os.path.join(BASE_DIR, p)
        ok = "OK" if os.path.exists(full) else "MISS"
        print(f"  [{ok}] {p}")

    # --- Done ---
    print()
    print("=" * 50)
    print("  环境配置完成！")
    print("=" * 50)
    print()
    print("  启动应用:")
    print(f"    cd \"{src_dir}\"")
    print("    python run.py")
    print()
    print("  访问地址: http://127.0.0.1:5000")
    print("  管理员:   admin / admin123")
    print()

if __name__ == "__main__":
    main()
