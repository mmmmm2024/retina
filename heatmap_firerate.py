# OFF mGC: ロバストな“勾配基準”の閾値境界検出
# 手順: 移動平均 → 単調(減少)回帰 → 最大勾配位置をRodごとに抽出
# 表示: 白→青の2色ヒートマップ（0〜17固定）＋ 閾値境界線のオーバーレイ

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize

# ========= 設定 =========
MOVING_AVG_WIN = 3      # 移動平均の窓幅（奇数）。3か5が無難
FIGSIZE = (8.0, 5.8)
DPI = 300

# ========= データ（発火率[Hz]）=========
DATA_HZ = {
    4.0: {200:7.60, 175:7.40, 150:7.40, 125:7.40, 100:7.40,  75:7.40,  50:7.40,  25:7.00,  0:6.80},
    3.5: {200:7.40, 175:7.40, 150:7.40, 125:7.40, 100:7.40,  75:7.40,  50:7.20,  25:6.40,  0:6.40},
    3.0: {200:7.20, 175:7.40, 150:7.00, 125:7.00, 100:7.00,  75:7.00,  50:6.60,  25:5.80,  0:5.40},
    2.5: {200:6.60, 175:6.80, 150:6.80, 125:6.80, 100:6.80,  75:6.60,  50:5.80,  25:5.00,  0:4.60},
    2.0: {200:6.20, 175:6.20, 150:6.20, 125:6.40, 100:6.20,  75:6.00,  50:5.00,  25:4.20,  0:4.20},
    1.5: {200:5.60, 175:5.60, 150:5.80, 125:5.80, 100:5.40,  75:5.00,  50:4.20,  25:3.80,  0:3.00},
    1.0: {200:4.20, 175:4.20, 150:4.40, 125:4.40, 100:4.40,  75:4.20,  50:3.60,  25:2.00,  0:1.80},
    0.5: {200:3.00, 175:3.20, 150:3.20, 125:3.20, 100:3.00,  75:3.00,  50:1.80,  25:1.60,  0:1.60},
    0.0: {200:2.60, 175:2.60, 150:2.60, 125:2.60, 100:2.20,  75:1.80,  50:1.60,  25:1.60,  0:1.60},
}


# ---- 軸（gは降順、Rodは昇順）----
g_vals = sorted(DATA_HZ.keys(), reverse=True)        # [4.0, 3.5, ..., 0.0]
rod_vals = sorted({r for d in DATA_HZ.values() for r in d.keys()})  # [0,25,...,200]

# ---- 行列Z（行=Rod, 列=g）----
Z = np.array([[DATA_HZ[g][r] for g in g_vals] for r in rod_vals], dtype=float)

# ========= 補助関数 =========
def moving_average(y, win=3):
    """端をコピーしてパディングし、窓幅winの単純移動平均を返す"""
    if win <= 1:
        return np.asarray(y, dtype=float)
    pad = win // 2
    y = np.asarray(y, dtype=float)
    ypad = np.pad(y, (pad, pad), mode='edge')
    kernel = np.ones(win) / win
    return np.convolve(ypad, kernel, mode='valid')

def pava_increasing(y, w=None):
    """単調増加の等方回帰（PAVA）。戻り値は元の長さの配列。"""
    y = list(map(float, y))
    n = len(y)
    if w is None:
        w = [1.0] * n
    else:
        w = list(map(float, w))
    blocks = [{'sum_w': w[i], 'sum_y': w[i]*y[i], 'len': 1} for i in range(n)]
    i = 0
    while i < len(blocks) - 1:
        avg_i   = blocks[i]['sum_y'] / blocks[i]['sum_w']
        avg_nxt = blocks[i+1]['sum_y'] / blocks[i+1]['sum_w']
        if avg_i > avg_nxt:
            # マージ
            blocks[i]['sum_w'] += blocks[i+1]['sum_w']
            blocks[i]['sum_y'] += blocks[i+1]['sum_y']
            blocks[i]['len']   += blocks[i+1]['len']
            del blocks[i+1]
            if i > 0:
                i -= 1
        else:
            i += 1
    z = []
    for b in blocks:
        avg = b['sum_y'] / b['sum_w']
        z.extend([avg] * b['len'])
    return np.array(z, dtype=float)

def pava_decreasing(y, w=None):
    """単調減少の等方回帰：符号反転で増加版に流用"""
    y = np.asarray(y, dtype=float)
    return -pava_increasing(-y, w=w)

def knee_by_max_gradient(y, g):
    """最大勾配（絶対値）が出る区間の中央を“膝”として返す"""
    y = np.asarray(y, dtype=float)
    g = np.asarray(g, dtype=float)
    dy = np.diff(y)
    dg = np.diff(g)
    slope = np.abs(dy / dg)  # dg<0だが絶対値でOK
    j = int(np.argmax(slope))  # 区間 [j, j+1]
    g_star = 0.5 * (g[j] + g[j+1])
    return g_star, j + 0.5  # 列インデックス（imshow座標）も返す

# ========= Rodごとに“ロバスト膝”を抽出 =========
g_stars = []      # 閾値のg*
x_line  = []      # imshow上のx位置（列インデックス小数）
for i in range(Z.shape[0]):
    row = Z[i, :]
    row_ma  = moving_average(row, win=MOVING_AVG_WIN)  # 移動平均
    row_iso = pava_decreasing(row_ma)                  # 単調減少に補正
    g_star, x_idx = knee_by_max_gradient(row_iso, np.array(g_vals))
    g_stars.append(g_star)
    x_line.append(x_idx)

# ========= 図：ヒートマップ + 閾値境界線 =========
cmap = LinearSegmentedColormap.from_list("white_to_blue", ["#FFFFFF", "#1f4e97"])
norm = Normalize(vmin=0, vmax=7)

fig, ax = plt.subplots(figsize=FIGSIZE)  # ★ fig, ax を定義

im = ax.imshow(Z, origin="lower", aspect="auto", cmap=cmap, norm=norm)

# 軸ラベル
ax.set_xticks(np.arange(len(g_vals)))
ax.set_xticklabels(g_vals)
ax.set_yticks(np.arange(len(rod_vals)))
ax.set_yticklabels(rod_vals)
ax.set_xlabel("Synaptic conductance from cones to midget bipolar cells[nS]")
ax.set_ylabel("Number of Rod")

# カラーバーを作成
cbar = fig.colorbar(im, ax=ax, label="Firing rate [Hz]")
cbar.set_ticks(np.arange(0, 8, 1))

# 閾値線
y_idx = np.arange(len(rod_vals))
ax.plot(x_line, y_idx, linewidth=2.5, label="robust knee", color="red")

# --- カラーバーの下に凡例を追加 ---
cbar.ax.legend(
    [plt.Line2D([0], [0], color="red", linewidth=2.5)],
    ["robust knee"],
    loc="upper center",
    bbox_to_anchor=(0.5, -0.05),
    frameon=True
)

# タイトルを下側中央に
fig.suptitle("Figure 2: Firing rate in ONmGC", y=0.04)

plt.tight_layout()
plt.show()

fig.savefig("ONmGC.pdf")
