#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""水平剖面图：把三件套切成 0.10 mm 薄片，光栅化成实心掩膜，按真实 mm 坐标出图，
并叠上主板轮廓（53.70×35.19）与关键器件位置，用于核对开孔 / 台面 / 腔体。
用法：python sections.py
输出：out/section_z<高度>.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import cadquery as cq

OUT = ROOT + "//out"
RES = 0.08                    # mm / pixel
PARTS = [("tray", "stm32f429_tray.step"), ("lid", "stm32f429_lid.step"),
         ("joystick", "stm32f429_joystick.step")]
BW, BH = 53.70, 35.19

# 板上关键器件（mm，来自 pcb3d.obj）
# (x0, y0, w, h)：左壁三个窗口在平面上的位置（画在侧壁上）
MARKS = [
    (0.0, 0.0, BW, BH, "--", "板框 53.70×35.19"),
    (-3.05, 19.49, 2.70, 13.30, "-", ""),     # 左窗 USB-A（y 19.49..32.79）
    (-3.05, 10.29, 2.70, 9.20, "-", ""),      # 左窗 CN1（y 10.29..19.49）
    (-3.05, 0.49, 2.70, 9.80, "-", ""),       # 左窗 USB-C（y 0.49..10.29）
]
TXT = [(-1.7, 26.19, "USB-A\n窗"), (-1.7, 14.89, "烧录口"), (-1.7, 5.39, "TYPE-C\n窗"),
       (19.44, 16.50, "OLED"), (45.03, 15.19, "RESET/POWER"),]


def box_solid(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(max(x1 - x0, 1e-3), max(y1 - y0, 1e-3), max(z1 - z0, 1e-3))
            .translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)).val())


def mask_at(z, x0=-4.0, x1=58.5, y0=-4.5, y1=41.5):
    nx, ny = int((x1 - x0) / RES) + 1, int((y1 - y0) / RES) + 1
    m = np.zeros((ny, nx), bool)
    for name, fn in PARTS:
        p = os.path.join(OUT, fn)
        if not os.path.exists(p):
            continue
        shp = cq.importers.importStep(p).val()
        bb = shp.BoundingBox()
        if z < bb.zmin or z > bb.zmax:
            continue
        slab = shp.intersect(box_solid(x0, x1, y0, y1, z - 0.05, z + 0.05))
        try:
            verts, tris = slab.tessellate(0.05)
        except Exception:
            continue
        if not verts or not tris:
            continue
        V = np.array([[v.x, v.y, v.z] for v in verts])
        T = np.array(tris, dtype=np.int64)
        px = (V[:, 0] - x0) / RES
        py = (V[:, 1] - y0) / RES
        for tri in T:
            tx, ty = px[tri], py[tri]
            i0, i1 = max(int(np.floor(tx.min())), 0), min(int(np.ceil(tx.max())), nx - 1)
            j0, j1 = max(int(np.floor(ty.min())), 0), min(int(np.ceil(ty.max())), ny - 1)
            if i1 < i0 or j1 < j0:
                continue
            gx, gy = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1))
            den = (ty[1] - ty[2]) * (tx[0] - tx[2]) + (tx[2] - tx[1]) * (ty[0] - ty[2])
            if abs(den) < 1e-12:
                continue
            l0 = ((ty[1] - ty[2]) * (gx - tx[2]) + (tx[2] - tx[1]) * (gy - ty[2])) / den
            l1 = ((ty[2] - ty[0]) * (gx - tx[2]) + (tx[0] - tx[2]) * (gy - ty[2])) / den
            sel = (l0 >= -0.02) & (l1 >= -0.02) & (1 - l0 - l1 >= -0.02)
            m[gy[sel], gx[sel]] = True
    return m, x0, y0


def draw(z, title):
    m, x0, y0 = mask_at(z)
    ny, nx = m.shape
    fig, ax = plt.subplots(figsize=(11.5, 8.0), dpi=150)
    ax.imshow(np.where(m, 1.0, np.nan), origin="lower", cmap="Blues", vmin=0, vmax=2.2,
              extent=[x0, x0 + nx * RES, y0, y0 + ny * RES], interpolation="nearest")
    for (a, b, w, h, ls, lab) in MARKS:
        ax.add_patch(Rectangle((a, b), w, h, fill=False, ec="#c0392b", ls=ls,
                               lw=1.0, label=lab or None))
    ax.plot([0, 0, BW, BW, 0], [0, BH, BH, 0, 0], color="#c0392b", lw=1.0, ls="--", alpha=0.85)
    for (x, y, t) in TXT:
        if t:
            ax.text(x, y, t, color="#c0392b", fontsize=7, ha="center", va="center")
    ax.set_xlim(-4.0, 58.5)
    ax.set_ylim(-4.5, 41.5)
    ax.set_aspect("equal")
    ax.set_xlabel("x / mm（板左边缘 = 0）")
    ax.set_ylabel("y / mm（板上边缘 = 0，向上为正）")
    ax.set_title(title, fontsize=10.5)
    ax.grid(alpha=0.25, lw=0.4)
    ft = os.path.join(OUT, "section_z%+.1f.png" % z) if z < 0 else os.path.join(OUT, "section_z%.1f.png" % z)
    fig.tight_layout()
    fig.savefig(ft)
    plt.close(fig)
    if m.any():
        j, i = np.where(m)
        print("wrote %s  实心 %.1f%%  bbox x %.2f..%.2f  y %.2f..%.2f"
              % (ft, 100.0 * m.mean(), x0 + i.min() * RES, x0 + i.max() * RES,
                 y0 + j.min() * RES, y0 + j.max() * RES))
    else:
        print("wrote %s  （空）" % ft)


def main():
    draw(5.0, "剖面 z=+5.0：上腔（左壁三窗在此高度全开，右壁封闭；内腔 54.40×36.74）")
    draw(-0.5, "剖面 z=−0.5：主板层（板厚 1.0，板边四周 0.35 间隙；上腔 54.40×36.74）")
    draw(-1.2, "剖面 z=−1.2：台面下方 0.2（1.0 mm 宽承台立柱一圈 + 下腔）")
    draw(-2.6, "剖面 z=−2.6：背面侧键层（0.6 mm 柔性膜 + 两个内侧凸台 + 断料缝）")
    draw(-4.5, "剖面 z=−4.5：板下 4G 空间层（净深 4.4，周壁 + 底板）")
    draw(12.0, "剖面 z=+12.0：盖板定位唇层（唇厚 1.2，四边各两条摩擦筋）")
    draw(13.2, "剖面 z=+13.2：摇杆卡爪层（φ9.6 孔 + φ11.2 沉台 + 三爪）")


if __name__ == "__main__":
    main()
