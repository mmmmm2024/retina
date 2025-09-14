import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------
#  Cones  (Curcio 1990  vs  Masri 2021, same visual angle)
# ------------------------------------------------------------
curcio = pd.read_excel("4meridians.xlsx", sheet_name="Cones per sq mm")
for col in ["mm", "superior", "inferior", "temporal", "nasal"]:
    curcio[col] = pd.to_numeric(curcio[col], errors="coerce")

meridian_cols = ["superior", "inferior", "temporal", "nasal"]
curcio["Curcio_mean"] = curcio[meridian_cols].mean(axis=1, skipna=True)

def mm2deg(r):          # Watson 2014 (Drasdo–Fowler) inverse polynomial
    return 3.556*r + 0.05993*r**2 - 7.358e-3*r**3 + 3.027e-4*r**4

OFFSET_NASAL = -1.5
curcio["deg_curcio"] = (curcio["mm"] + OFFSET_NASAL).apply(mm2deg) - mm2deg(OFFSET_NASAL)

def masri_cone_density(r_mm):
    c1, l1 = 3.673e5, -7.828e0
    c2, l2 = -2.000e5, -2.000e3
    c3, l3 = 2.034e4, -2.164e-1
    return c1*np.exp(l1*r_mm) + c2*np.exp(l2*r_mm) + c3*np.exp(l3*r_mm)

RET_MAG_MASRI = 0.29      # mm / deg
curcio["Masri_equiv_mm"]  = curcio["deg_curcio"] * RET_MAG_MASRI
curcio["Masri2021_equiv"] = masri_cone_density(curcio["Masri_equiv_mm"])

# ------------------------------------------------------------
#  Ganglion Cells  (Curcio 1990  vs  Masri 2021, same visual angle)
# ------------------------------------------------------------
gc = pd.read_excel("Curcio_JCompNeurol1990_GCtopo_F6.xlsx", header=0)
gc_meridians = [
    "Temp.mean_GC/sq mm", "Sup.mean_GC/sq mm",
    "Nasal.mean_GC/sq mm", "Inf.mean_GC/sq mm"
]
for col in gc_meridians + ["Ecc_mm"]:
    gc[col] = pd.to_numeric(gc[col], errors="coerce")

gc["Curcio_mean"] = gc[gc_meridians].mean(axis=1, skipna=True)
gc["deg_curcio"]  = (gc["Ecc_mm"] + OFFSET_NASAL).apply(mm2deg) - mm2deg(OFFSET_NASAL)

def masri_rgc_density(r_mm):
    c1, l1 = 5.717e5, -1.031e0
    c2, l2 = -6.000e5, -1.261e0
    c3, l3 = -5.527e1, -9.658e1
    return c1*np.exp(l1*r_mm) + c2*np.exp(l2*r_mm) + c3*np.exp(l3*r_mm)

gc["Masri_equiv_mm"]  = gc["deg_curcio"] * RET_MAG_MASRI
gc["Masri2021_equiv"] = masri_rgc_density(gc["Masri_equiv_mm"])

# ------------------------------------------------------------
#  Plot: visual angle (deg)  vs  cell density (cells/mm²)
# ------------------------------------------------------------

# Masri 曲線（0.0345–100°）
deg_range = np.linspace(1.034, 100, 1200)
masri_mm  = deg_range * RET_MAG_MASRI
masri_cone_curve = masri_cone_density(masri_mm)


fig, ax = plt.subplots(2, 1, figsize=(7, 10), sharex=True)

# ------------------------------------------------------------
#  RGC : Curcio 実測 vs. Masri モデル
# ------------------------------------------------------------
gc = pd.read_excel("Curcio_JCompNeurol1990_GCtopo_F6.xlsx", header=0)
gc_cols = ["Temp.mean_GC/sq mm", "Sup.mean_GC/sq mm", "Nasal.mean_GC/sq mm", "Inf.mean_GC/sq mm"]
for col in gc_cols + ["Ecc_mm"]:
    gc[col] = pd.to_numeric(gc[col], errors="coerce")
gc["Curcio_mean"] = gc[gc_cols].mean(axis=1, skipna=True)
gc["deg_curcio"]  = (gc["Ecc_mm"] + OFFSET_NASAL).apply(mm2deg) - mm2deg(OFFSET_NASAL)

def masri_rgc_density(r_mm):
    c1, l1 = 5.717e5, -1.031e0
    c2, l2 = -6.000e5, -1.261e0
    c3, l3 = -5.527e1, -9.658e1
    return c1*np.exp(l1*r_mm) + c2*np.exp(l2*r_mm) + c3*np.exp(l3*r_mm)

gc["Masri_equiv_mm"]  = gc["deg_curcio"] * RET_MAG_MASRI
gc["Masri2021_equiv"] = masri_rgc_density(gc["Masri_equiv_mm"])

masri_rgc_curve = masri_rgc_density(masri_mm)

# ------------------------------------------------------------
#  Plot
# ------------------------------------------------------------
fig, ax = plt.subplots(2, 1, figsize=(8, 11), sharex=True)

# Cones
ax[0].plot(curcio["deg_curcio"], curcio["Curcio_mean"], "o",
           label="Curcio 1990 (mean of 4 meridians)")
ax[0].plot(curcio["deg_curcio"], curcio["Masri2021_equiv"], "x",
           label="Masri 2021 model (at Curcio points)")
ax[0].plot(deg_range, masri_cone_curve, "-", lw=1.2,
           label="Masri 2021 model curve (1.034–100°)")
ax[0].set_ylabel("Cone density (cells / mm$^{2}$)")
ax[0].set_title("Cone Photoreceptor Density vs. Visual Angle")
ax[0].legend()

# RGC
ax[1].plot(gc["deg_curcio"], gc["Curcio_mean"], "o",
           label="Curcio 1990 (mean of 4 meridians)")
ax[1].plot(gc["deg_curcio"], gc["Masri2021_equiv"], "x",
           label="Masri 2021 model (at Curcio points)")
ax[1].plot(deg_range, masri_rgc_curve, "-", lw=1.2,
           label="Masri 2021 model curve (1.034–100°)")
ax[1].set_xlabel("Retinal eccentricity (deg, nasal meridian)")
ax[1].set_ylabel("RGC density (cells / mm$^{2}$)")
ax[1].set_title("Retinal Ganglion Cell Density vs. Visual Angle")
ax[1].legend()

plt.tight_layout()
plt.savefig("cone_and_gc_density_vs_deg_fullrange.png", dpi=300)
plt.show()