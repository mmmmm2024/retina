import pandas as pd

# データの読み込み
# df = pd.read_csv("OFF_GC_52.0.txt")
df = pd.read_csv("OFF_GC_10.0.txt")
# スパイク検出：0mVを超えた瞬間（crossing）
# ひとつ前の値が0以下で、次が0より大きい → スパイクとみなす
spike_indices = df[(df["membrane potential(mV)"].shift(1) <= 0) & (df["membrane potential(mV)"] > 0)].index

# スパイク回数
num_spikes = len(spike_indices)

# 測定時間 [秒]
duration_sec = (df["time(ms)"].iloc[-1] - df["time(ms)"].iloc[0]) / 1000

# 発火率 [Hz]
firing_rate = num_spikes / duration_sec

print(f"スパイク回数：{num_spikes}回")
print(f"発火率：{firing_rate:.2f} Hz")

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ── 1. データ ─────────────────────────────────────────────
data = {
    "ID":   ["R4", "R7", "R10", "R13", "R26", "R39", "R52",
             "C1", "C2", "C3", "C4", "C8", "C12", "C16"],
    "Type": ["R",  "R",  "R",   "R",   "R",   "R",   "R",
             "C",  "C",  "C",   "C",   "C",   "C",   "C"],
    "ONGC": [4.80, 4.80, 4.80, 4.80, 4.00, 4.40, 4.80,
             4.20, 4.40, 4.40, 4.40, 4.80, 4.80, 4.80],
    "OFFGC":[15.60,15.60,15.60,15.80,15.60,15.60,15.60,
             5.40, 7.20, 8.80, 9.20,14.20,15.00,15.60]
}
df   = pd.DataFrame(data)
df_R = df[df["Type"] == "R"]
df_C = df[df["Type"] == "C"]

# ── 2. 減少率 (数値) ＆ ラベル（表示用） ──────────────────
#   1.0 = 減少 0%         ←→   0%  (ラベル)
#   0.0 = 完全消失 100%?  ←→ 100% (ラベル)  … ここでは使用しない
reduction_numeric = np.array([1.00, 0.75, 0.50, 0.25, 0.19, 0.12, 0.06])
reduction_labels  = ["0%", "25%", "50%", "75%", "81%", "88%", "94%"]

# データ順を numeric(降順) に合わせる（[::-1] で反転）
R_ONGC  = df_R["ONGC"].values[::-1]
R_OFFGC = df_R["OFFGC"].values[::-1]
C_ONGC  = df_C["ONGC"].values[::-1]
C_OFFGC = df_C["OFFGC"].values[::-1]

# ── 3. プロット ───────────────────────────────────────────
fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=True)

# Rod – ONGC
axs[0, 0].plot(reduction_numeric, R_ONGC,  'o-', color='tab:blue')
axs[0, 0].set_title("Rod - ONGC")
axs[0, 0].set_ylabel("Firing Rate [Hz]")
axs[0, 0].set_ylim(0, 16)
axs[0, 0].grid(True)

# Rod – OFFGC
axs[1, 0].plot(reduction_numeric, R_OFFGC, 's-', color='tab:blue')
axs[1, 0].set_title("Rod - OFFGC")
axs[1, 0].set_ylabel("Firing Rate [Hz]")
axs[1, 0].set_xlabel("Photoreceptor Reduction")
axs[1, 0].set_ylim(0, 16)
axs[1, 0].grid(True)

# Cone – ONGC
axs[0, 1].plot(reduction_numeric, C_ONGC,  'o-', color='tab:red')
axs[0, 1].set_title("Cone - ONGC")
axs[0, 1].set_ylim(0, 16)
axs[0, 1].tick_params(labelleft=False)
axs[0, 1].grid(True)

# Cone – OFFGC
axs[1, 1].plot(reduction_numeric, C_OFFGC, 's-', color='tab:red')
axs[1, 1].set_title("Cone - OFFGC")
axs[1, 1].set_xlabel("Photoreceptor Reduction")
axs[1, 1].set_ylim(0, 16)
axs[1, 1].tick_params(labelleft=False)
axs[1, 1].grid(True)

# ── 4. x軸目盛を統一して設定 ──────────────────────────────
for row in axs:
    for ax in row:
        ax.set_xticks(reduction_numeric)
        ax.set_xticklabels(reduction_labels, rotation=45)

plt.tight_layout()
plt.savefig("FR_in_GC_fovea.pdf", dpi=300, bbox_inches='tight')
plt.show()
