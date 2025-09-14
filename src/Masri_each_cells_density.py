import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict

# ------------------------------------------------------------
# 1. deg → mm 変換（1° = 0.29mm）
# ------------------------------------------------------------
ecc_deg = np.linspace(1, 50, 300)         # 視角度 1°〜50°
ecc_mm = ecc_deg / 0.29                   # 偏心度 [mm]

# ------------------------------------------------------------
# 2. Masri et al., 2021 の密度モデル
# ------------------------------------------------------------
def diff_exp(x, c1, k1, c2, k2, c3=0, k3=0):
    return c1*np.exp(k1*x) + c2*np.exp(k2*x) + c3*np.exp(k3*x)

PARAMS = OrderedDict([
    ("Cone",      (3.673e5, -7.828e0,   -2.000e5, -2.000e3,   2.034e4,  -2.164e-1)),
    ("S-Cone",    (5.048e3, -3.014e0,   -1.100e4, -7.869e0,   1.455e3,  -1.370e-1)),
    ("Rod",       (5.855e5, -1.388e-1,  -5.989e5, -2.998e-1)),
    ("Ganglion",  (5.717e5, -1.031e0,   -6.000e5, -1.261e0,   -5.527e1, -9.658e1)),
    ("OFFMBC",    (4.208e5, -1.225e0,   -4.551e5, -1.387e0,   1.230e4,  -6.986e-2)),
    ("ONBC",      (1.788e5, -4.755e-1,  -1.836e5, -5.618e-1,   8.894e3,  -1.832e-2)),
    ("DB3a",      (4.275e3, -1.949e-1,  -9.614e3, -5.831e0,   3.336e2,   5.811e-3)),
    ("DB3b",      (7.061e3, -1.511e-1,  -7.869e3, -3.120e0,  -3.653e3,  -3.347e-1)),
    ("Horizontal",(2.051e4, -3.850e-1,  -4.246e4, -4.196e0,  2.672e3,  -1.097e-2)),
    ("H1",        (1.659e4, -3.344e-1,  -4.227e6, -1.633e1,   1.280e3,   4.952e-2)),
    ("H2",        (5.131e3, -2.197e-1,  -5.440e3, -6.706e-1,  -8.006e-1, -5.171e1)),
    ("GlyAC",     (1.614e4, -1.260e-1,  -3.944e5, -5.923e0,  -6.498e2, -5.675e1)),
    ("GABAAC",    (1.214e5, -1.001e0,  -1.354e5, -1.113e0,    7.605e3,  -6.347e-2)),
    ("Müller",    (2.011e5, -1.845e0,  -2.369e5, -2.362e0,    1.379e4,  -2.815e-2)),
])

density_fn = {
    name: (lambda p: (lambda r: diff_exp(r, *p)))(params)
    for name, params in PARAMS.items()
}

# ------------------------------------------------------------
# 3. 3.45度以上だけに制限し、密度を0未満にしない
# ------------------------------------------------------------
threshold_deg = 3.45
mask = ecc_deg >= threshold_deg
ecc_deg_th = ecc_deg[mask]
ecc_mm_th = ecc_mm[mask]

# ------------------------------------------------------------
# 4. プロット
# ------------------------------------------------------------
fig, axes = plt.subplots(4, 4, figsize=(16, 12), sharex=True)
axes = axes.flatten()

for i, (name, fn) in enumerate(density_fn.items()):
    if i >= len(axes): break
    y = fn(ecc_mm_th)
    y = np.maximum(0, y)  # 負の値を0に
    axes[i].plot(ecc_deg_th, y, label=name)
    axes[i].axvline(x=threshold_deg, color="gray", linestyle="--", linewidth=1)
    ymin, ymax = axes[i].get_ylim()
    axes[i].text(threshold_deg, ymin - 0.05 * (ymax - ymin),
                 "3.45", ha="center", va="top", fontsize=8, color="black")
    axes[i].set_title(name)
    axes[i].grid(True)
    axes[i].set_ylabel("Density (cells/mm²)")
    axes[i].legend(fontsize="small")

for ax in axes[-4:]:
    ax.set_xlabel("Eccentricity (deg)")

plt.tight_layout()
plt.show()
