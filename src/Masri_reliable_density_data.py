import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. 変換 & 汎用指数関数
# --------------------------------------------------
def mm2deg(r_mm):            # Watson 2014 近似
    return r_mm / 0.29

def exp2(x, c1, k1, c2, k2):
    return c1*np.exp(k1*x) + c2*np.exp(k2*x)

def exp3(x, c1, k1, c2, k2, c3, k3):
    return c1*np.exp(k1*x) + c2*np.exp(k2*x) + c3*np.exp(k3*x)

# --------------------------------------------------
# 2. 偏心度軸
# --------------------------------------------------
ecc_mm  = np.linspace(1, 15, 300)
ecc_deg = mm2deg(ecc_mm)
target_deg = 3.4                 # 破線位置

# --------------------------------------------------
# 3. Masri 2021 の 13 細胞（GC 以外）
# --------------------------------------------------
masri = {
    "Cone"          : exp3(ecc_mm, 3.673e5, -7.828,   -2.000e5, -2000,   2.034e4,  -0.2164),
    "S-Cone"        : exp3(ecc_mm, 5.048e3, -3.014,   -1.100e4, -7.869,   1.455e3,  -0.1370),
    "OFF Midget BC" : exp3(ecc_mm, 4.208e5, -1.225,   -4.551e5, -1.387,  1.230e4,  -0.06986),
    "ONBC"          : exp3(ecc_mm, 1.788e5, -0.4755,  -1.836e5, -0.5618, 8.894e3,  -0.01832),
    "DB3a"          : exp3(ecc_mm, 4.275e3, -0.1949,  -9.614e3, -5.831,  3.336e2,   0.005811),
    "DB3b"          : exp3(ecc_mm, 7.061e3, -0.1511,  -7.869e3, -3.120, -3.653e3,  -0.3347),
    "Horizontal"    : exp3(ecc_mm, 2.051e4, -0.3850, -4.246e4, -4.196, 2.672e3,  -0.01097),
    "H1"            : exp3(ecc_mm, 1.659e4, -0.3344, -4.227e6, -16.33,  1.280e3,   0.04952),
    "H2"            : exp3(ecc_mm, 5.131e3, -0.2197,  -5.440e3, -0.6706, -0.8006, -51.71),
    "GlyAC"         : exp3(ecc_mm, 1.614e4, -0.1260,  -3.944e5, -5.923,  -6.498e2, -56.75),
    "GABAAC"        : exp3(ecc_mm, 1.214e5, -1.001,   -1.354e5, -1.113,  7.605e3,  -0.06347),
    "Müller"        : exp3(ecc_mm, 2.011e5, -1.845,   -2.369e5, -2.362,  1.379e4,  -0.02815),
}

# --------------------------------------------------
# 4. Ganglion Cell 曲線 (3 論文)
# --------------------------------------------------
gc_masri2021  = exp3(ecc_mm, 5.717e5, -1.031, -6.000e5, -1.261, -5.527e1, -9.658e1)
gc_tsai2019   = exp2(ecc_mm, 8.475e5, -1.358, -8.691e5, -1.556)
gc_drasdo2020 = gc_masri2021          # パラメータ同一（重なる）

# --------------------------------------------------
# 5. 描画 (5×3, 縮小版)
# --------------------------------------------------
fig, axes = plt.subplots(5, 3, figsize=(7.5, 9), sharex=True)
axes = axes.flatten()

# ------------ 0) GC 比較 ------------
ax = axes[0]
ax.plot(ecc_deg, gc_masri2021,  label="Masri 2021",  color="tab:blue",   lw=2)
ax.plot(ecc_deg, gc_tsai2019,   label="Sammy 2019",    color="tab:orange", lw=2, ls="--")
ax.plot(ecc_deg, gc_drasdo2020, label="Masri 2020", color="tab:green",  lw=0,
        marker="o", markersize=3, markevery=15)   # ◯マーカーで可視化
ax.axvline(target_deg, color="gray", ls="--", lw=1)
ymin = ax.get_ylim()[0]
ax.text( 3.4, ymin,   "3.4°", ha='center', va='top', fontsize=7)
ax.set_title("Ganglion Cells", fontsize=9)
ax.set_ylabel("Density (cells/mm²)")
ax.grid(True)
ax.legend(fontsize=7)

# ------------ 1) 以降 13 細胞 ------------
for ax, (name, y) in zip(axes[1:], masri.items()):
    ax.plot(ecc_deg, y, color="tab:blue", lw=1.5)
    ax.axvline(target_deg, color="gray", ls="--", lw=1)
    ymin = ax.get_ylim()[0]
    ax.text( 3.4, ymin,   "3.4°", ha='center', va='top', fontsize=7)
    ax.set_title(name, fontsize=9)
    ax.grid(True)

# 余った空白パネルを非表示
for empty_ax in axes[1+len(masri):]:
    empty_ax.axis("off")

# 軸ラベル
for ax in axes[-3:]:
    ax.set_xlabel("Eccentricity (degrees)")
for i in range(0, 15, 3):
    axes[i].set_ylabel("Density\n(cells/mm²)")

# fig.suptitle("Retinal Cell Densities (linear scale, dashed = 3.4°)", fontsize=12, y=0.95)
plt.tight_layout()
plt.savefig("retinal_cell_densities.pdf", format="pdf", bbox_inches="tight")  # ← PDF 出力
plt.show()
