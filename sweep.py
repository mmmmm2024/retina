#!/usr/bin/env python3
from itertools import product
from pathlib import Path
import subprocess, sys, os, shutil, time
from datetime import datetime

# === 基本設定 ===
BASE = Path(__file__).resolve().parent       
PY   = sys.executable
INIT = str((BASE / "init.py").resolve())    

RESULTS = BASE / f"results_txt_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
RESULTS.mkdir(exist_ok=True)

Num_R_list    = [1, 40, 80, 120, 160, 200, 240, 280, 320, 360, 400]
Num_C_RP_list = list(range(20, -1, -2))      # 20, 18, ..., 0

# .mod の場所（必要ならビルドする）
MODDIR   = BASE / "mod"      # 例: ./mod に .mod がある前提。無ければ何もしない
BUILDDIR = BASE / "x86_64"   # nrnivmodl の出力（Linux/macOSの既定）

def need_rebuild(moddir: Path, builddir: Path) -> bool:
    if not moddir.exists():
        return False
    if not builddir.exists():
        return True
    try:
        build_mtime = max(p.stat().st_mtime for p in builddir.rglob("*"))
    except ValueError:
        return True
    for m in moddir.glob("*.mod"):
        if m.stat().st_mtime > build_mtime:
            return True
    return False

def build_mechs_once():
    """必要なら nrnivmodl を一回だけ実行。失敗しても実行自体は続ける。"""
    if not MODDIR.exists():
        return
    if not need_rebuild(MODDIR, BUILDDIR):
        return
    print("[INFO] Building MOD mechanisms ...")
    try:
        # CoreNEURON 対応があるならこちらが速い。無ければ通常ビルドにフォールバック。
        subprocess.run(["nrnivmodl", "-coreneuron", str(MODDIR)], cwd=BASE,
                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
    except Exception:
        try:
            subprocess.run(["nrnivmodl", str(MODDIR)], cwd=BASE,
                           stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
        except Exception as e:
            print(f"[WARN] nrnivmodl failed: {e}")
    # FS の時刻ずれ対策で少し待つ
    time.sleep(0.2)
    print("[INFO] Build step done.")

# 1) .mod を必要に応じてビルド（ディレクトリは増やさない）
build_mechs_once()

# 2) 各条件を実行
for R, C in product(Num_R_list, Num_C_RP_list):
    g = 0.0 if R == 1 else 1e-5  # 仕様どおり

    # init.py がデフォルトで吐くファイル名を推定（例: "AIIAC_400.txt"）
    # ※あなたの init.py の export_data_txt 呼び出しが
    #    f"{object_name}_{h.Num_R:.0f}.txt" ならこの推定でOK。
    default_name = f"AIIAC_{R}.txt"
    default_path = BASE / default_name

    # 実行前に既存の同名ファイルがあれば削除
    if default_path.exists():
        default_path.unlink()

    # HOC グローバルを環境変数で注入
    env = os.environ.copy()
    env["Num_R"]     = str(R)
    env["Num_C_RP"]  = str(C)
    env["Num_C"]     = str(C)   # 互換のため
    env["g_R2RB"]    = str(g)

    # 実行（cwd は BASE のまま。ログは捨てて“結果テキストのみ”増やす）
    res = subprocess.run([PY, INIT], cwd=BASE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         check=False, env=env)

    if res.returncode != 0:
        print(f"[WARN] FAILED R{R:03d}_C{C:02d} (code={res.returncode})")
        continue

    # 生成されたデフォルトファイルを、R と C を含む名前に即リネーム
    # （これで同じ R の別 C による上書きを防ぐ）
    if default_path.exists():
        final = BASE / f"AIIAC_R{R:03d}_C{C:02d}.txt"
        # 念のため既存なら削除
        if final.exists():
            final.unlink()
        shutil.move(str(default_path), str(final))
    else:
        # 念のためフォールバック探索（*_R.txt の最新）
        candidates = sorted(BASE.glob(f"*_{R}.txt"),
                            key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            final = BASE / f"AIIAC_R{R:03d}_C{C:02d}.txt"
            if final.exists():
                final.unlink()
            shutil.move(str(candidates[0]), str(final))
        else:
            print(f"[WARN] No output file for R{R} C{C}. Check init.py output name.")
