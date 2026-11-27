#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""把 pcb3d.obj 光栅化成高度图（顶面 / 底面），颜色=相对板顶面的高度。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

OBJ = ROOT + "//pcb3d.obj"
S = 0.254                      # mm / unit（由 LQFP-100 14 mm = 55.10 unit 标定）
X0, X1 = 4048.20, 4259.60
Y0, Y1 = -3185.76, -3047.20
ZT = 10.0                      # 板顶面
W, H = (X1 - X0) * S, (Y1 - Y0) * S


def load():
    V, F = [], []
    with open(OBJ) as f:
        for line in f:
            if line.startswith('v '):
                _, a, b, c = line.split()
                V.append((float(a), float(b), float(c)))
            elif line.startswith('f '):
                p = [int(t.split('/')[0]) - 1 for t in line.split()[1:]]
                for k in range(1, len(p) - 1):
                    F.append((p[0], p[k], p[k + 1]))
    return np.array(V), np.array(F, dtype=np.int64)


def raster(V, F, res=0.15):
    nx, ny = int(W / res) + 2, int(H / res) + 2
    top = np.full((ny, nx), -1e9, np.float32)
    bot = np.full((ny, nx), 1e9, np.float32)
    px = (V[:, 0] - X0) * S / res
    py = (V[:, 1] + 3185.76) * S / res       # 实物坐标：下边缘 = 0，y 向上
    pz = (V[:, 2] - ZT) * S
    for tri in F:
        xs, ys = px[tri], py[tri]
        x0, x1 = int(np.floor(xs.min())), int(np.ceil(xs.max()))
        y0, y1 = int(np.floor(ys.min())), int(np.ceil(ys.max()))
        if x1 < 0 or y1 < 0 or x0 >= nx or y0 >= ny:
            continue
        x0, x1 = max(x0, 0), min(x1, nx - 1)
        y0, y1 = max(y0, 0), min(y1, ny - 1)
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = ((ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2]))
        if abs(d) < 1e-12:
            continue
        l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
        l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
        l2 = 1 - l0 - l1
        m = (l0 >= -0.02) & (l1 >= -0.02) & (l2 >= -0.02)
        if not m.any():
            continue
        z = l0 * pz[tri[0]] + l1 * pz[tri[1]] + l2 * pz[tri[2]]
        sub_t = top[y0:y1 + 1, x0:x1 + 1]
        sub_b = bot[y0:y1 + 1, x0:x1 + 1]
        np.maximum(sub_t, np.where(m, z, -1e9), out=sub_t)
        np.minimum(sub_b, np.where(m, z, 1e9), out=sub_b)
    return top, bot, res


if __name__ == "__main__":
    V, F = load()
    print("verts %d tris %d  board %.2f x %.2f mm" % (len(V), len(F), W, H))
    top, bot, res = raster(V, F)
    zt = np.where(top > -1e8, top, np.nan)
    zb = np.where(bot < 1e8, bot, np.nan)
    print("top   z: %.2f .. %.2f mm" % (np.nanmin(zt), np.nanmax(zt)))
    print("bot   z: %.2f .. %.2f mm" % (np.nanmin(zb), np.nanmax(zb)))
    ext = (0, W, 0, H)
    fig, ax = plt.subplots(1, 2, figsize=(20, 8))
    im0 = ax[0].imshow(zt, cmap="turbo", extent=ext, origin="lower", vmin=-1, vmax=9)
    ax[0].set_title("TOP side  (x right / y up, mm; colour = height above board top)")
    fig.colorbar(im0, ax=ax[0], shrink=0.8)
    im1 = ax[1].imshow(zb, cmap="turbo", extent=ext, origin="lower", vmin=-3, vmax=1)
    ax[1].set_title("BOTTOM side  (colour = height below board top, negative)")
    fig.colorbar(im1, ax=ax[1], shrink=0.8)
    for a in ax:
        a.set_xticks(np.arange(0, W + 1, 5))
        a.set_yticks(np.arange(0, H + 1, 5))
        a.grid(color="k", alpha=0.25, lw=0.5)
        a.set_xlim(-2, W + 2)
        a.set_ylim(-2, H + 2)
        a.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(ROOT + "//out/obj_heightmap.png", dpi=110)
    np.save("/tmp/ztop.npy", zt)
    np.save("/tmp/zbot.npy", zb)
    print("wrote out/obj_heightmap.png")
