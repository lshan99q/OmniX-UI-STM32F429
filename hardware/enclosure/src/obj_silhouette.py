#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""把 pcb3d.obj 渲染成正交轮廓图（沿 ±X / ±Y / ±Z 看），用于确定外壳开孔轮廓。
   坐标已换算到 mm 板坐标系：x 0..53.70（右）、y 0..35.19（下）、z=0 板顶面（向上为正）。
"""
import numpy as np
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OBJ = ROOT + "//pcb3d.obj"
S = 0.254
X0, YMIN, ZT = 4048.20, -3185.76, 10.0


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
    V = np.array(V)
    P = np.empty_like(V)
    P[:, 0] = (V[:, 0] - X0) * S
    P[:, 1] = (V[:, 1] - YMIN) * S        # 实物坐标：y 向上
    P[:, 2] = (V[:, 2] - ZT) * S
    return P, np.array(F, dtype=np.int64)


def render(P, F, view, fname, res=0.06, title=""):
    """view: 'left' 从 x- 看(屏幕右=+y, 上=+z); 'right' 从 x+ 看(右=-y);
             'front' 从 y+ 看(右=-x, 上=+z); 'back' 从 y- 看(右=+x);
             'top' 从上(右=+x, 上=+y); 'bottom' 从下(右=+x, 下=+y)"""
    if view in ("left", "right"):
        sx = P[:, 1] * (1 if view == "left" else -1)
        sy = P[:, 2]
        dep = P[:, 0] * (-1 if view == "left" else 1)
    elif view in ("front", "back"):
        sx = P[:, 0] * (-1 if view == "front" else 1)
        sy = P[:, 2]
        dep = P[:, 1] * (1 if view == "front" else -1)
    else:
        sx = P[:, 0]
        sy = P[:, 1]
        dep = P[:, 2] * (1 if view == "top" else -1)

    x0, x1 = np.floor(sx.min() / res) * res, np.ceil(sx.max() / res) * res
    y0, y1 = np.floor(sy.min() / res) * res, np.ceil(sy.max() / res) * res
    nx, ny = int((x1 - x0) / res) + 1, int((y1 - y0) / res) + 1
    buf = np.full((ny, nx), -1e9, np.float32)
    for tri in F:
        xs, ys = sx[tri], sy[tri]
        i0 = int((xs.min() - x0) / res) - 1
        i1 = int((xs.max() - x0) / res) + 2
        j0 = int((ys.min() - y0) / res) - 1
        j1 = int((ys.max() - y0) / res) + 2
        i0, j0 = max(i0, 0), max(j0, 0)
        i1, j1 = min(i1, nx), min(j1, ny)
        if i1 <= i0 or j1 <= j0:
            continue
        gx, gy = np.meshgrid(x0 + (np.arange(i0, i1) + 0.5) * res,
                             y0 + (np.arange(j0, j1) + 0.5) * res)
        d = ((ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2]))
        if abs(d) < 1e-12:
            continue
        l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
        l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
        l2 = 1 - l0 - l1
        m = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
        if not m.any():
            continue
        zz = l0 * dep[tri[0]] + l1 * dep[tri[1]] + l2 * dep[tri[2]]
        sub = buf[j0:j1, i0:i1]
        np.maximum(sub, np.where(m, zz, -1e9), out=sub)
    img = np.where(buf > -1e8, buf, np.nan)
    fig, ax = plt.subplots(figsize=(16, 10))
    im = ax.imshow(img, cmap="viridis", extent=(x0, x1, y0, y1), origin="lower")
    fig.colorbar(im, ax=ax, shrink=0.8, label="depth")
    ax.set_xticks(np.arange(np.ceil(x0), x1 + 0.01, 2))
    ax.set_yticks(np.arange(np.ceil(y0), y1 + 0.01, 2))
    ax.grid(color="w", alpha=0.35, lw=0.6)
    ax.set_title(title)
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(fname, dpi=110)
    plt.close(fig)
    print("wrote", fname)


if __name__ == "__main__":
    P, F = load()
    out = ROOT + "//out/"
    render(P, F, "left", out + "obj_left.png",
           title="OBJ 左视（从 x- 看，屏幕右 = +y）：USB-A / 烧录口 / USB-C 轮廓，单位 mm")
    render(P, F, "front", out + "obj_front.png",
           title="OBJ 前视（从 y+ 看，屏幕右 = -x）：RESET/POWER 侧键轮廓")
    render(P, F, "top", out + "obj_top.png", title="OBJ 俯视（右=+x，下=+y）")
