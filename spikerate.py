import pandas as pd
import numpy as np

# # ファイル名
# filenames = [
#     "OFF_GC_400.txt",
#     "OFF_GC_400_2.txt",
#     "OFF_GC_360.txt",
#     "OFF_GC_320.txt",
#     "OFF_GC_280.txt",
#     "OFF_GC_240.txt",
#     "OFF_GC_200.txt",
#     "OFF_GC_160.txt",
#     "OFF_GC_120.txt",
#     "OFF_GC_80.txt",
#     "OFF_GC_40.txt",
#     "OFF_GC_1.txt",
# ]

filenames = [
    "ON_GC_400.txt",
    "ON_GC_360.txt",
    "ON_GC_320.txt",
    "ON_GC_280.txt",
    "ON_GC_240.txt",
    "ON_GC_200.txt",
    "ON_GC_160.txt",
    "ON_GC_120.txt",
    "ON_GC_80.txt",
    "ON_GC_40.txt",
    "ON_GC_1.txt",
]

# ヒステリシスしきい値 (mV)
thr_hi = 0.0     # 上抜けでスパイク開始
thr_lo = -20.0   # ここまで下降したら次の検出を許可

# 時間範囲 (ms)
start_time = 1000.0
end_time   = 6000.0

# 2) ここから下は、あなたの既存コードを for ループの中にそのまま入れてください
for filename in filenames:
    # --- ここから既存コード（読み込み～検出～集計） ---
    data = pd.read_csv(filename, skiprows=1, header=None, names=["time", "voltage"])
    data["time"] = pd.to_numeric(data["time"], errors="coerce")
    data["voltage"] = pd.to_numeric(data["voltage"], errors="coerce")
    data = data.dropna(subset=["time", "voltage"])

    seg = data[(data["time"] >= start_time) & (data["time"] <= end_time)].reset_index(drop=True)

    t = seg["time"].to_numpy()
    v = seg["voltage"].to_numpy()

    spike_times = []
    armed = True
    for i in range(1, len(v)):
        if armed:
            if v[i-1] <= thr_hi and v[i] > thr_hi:
                spike_times.append(t[i])
                armed = False
        else:
            if v[i] < thr_lo:
                armed = True

    spike_times = pd.Series(spike_times)
    valid_spikes = spike_times

    spike_count = len(valid_spikes)
    duration_s  = (end_time - start_time) / 1000.0
    firing_rate = spike_count / duration_s if duration_s > 0 else float("nan")
    # --- 既存コードここまで ---

    # あなたの末尾の3行（ファイル名→スパイク数→発火率）
    print(filename)
    print(f"Spike count (1000ms-6000ms): {spike_count}")
    print(f"Firing rate (1000ms-6000ms): {firing_rate:.2f} Hz")
    print()  # 見やすさ用の空行
