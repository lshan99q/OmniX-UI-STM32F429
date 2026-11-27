#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""装配体预览图：托盘 + 真实主板网格 + 4G 模块包络 + 盖板 + 摇杆帽。

输出
  out/preview_assy_iso.png     整装 3/4 视图
  out/preview_assy_cut.png     沿 y=15.19 剖开（看主板、4G 模块、台面）
  out/preview_assy_inside.png  去掉盖板从上往下看（主板落在托盘里）
  out/sch_stack.png            2D 堆叠剖面（底板→4G→板→台面→盖板，带尺寸）
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import render_zbuf as R
import build_assy as A
import build_case as B

OUT = ROOT + "//out"
STEP = dict(tray=OUT + "/stm32f429_tray.step",
            lid=OUT + "/stm32f429_lid.step",
            joystick=OUT + "/stm32f429_joystick.step",
            button=OUT + "/stm32f429_button.step")
C = A.COL
YCUT = 15.19                                  # 剖切面（板 y 中点）

d = np.load("/tmp/assy_parts.npz")
PCB_V, PCB_F = d["V"], d["F"]
M4_V, M4_F = d["m4V"], d["m4F"]


# ---------------------------------------------------------------- 网格半剖
def clip_mesh(V, F, axis, value):
    """保留 V[:,axis] >= value 的部分，跨面按 Sutherland–Hodgman 切分。"""
    Vs = [tuple(v) for v in V]
    out = []
    for tri in F:
        d3 = [V[i, axis] - value for i in tri]
        if min(d3) >= 0:
            out.append(tuple(int(i) for i in tri))
        elif max(d3) <= 0:
            continue
        else:
            poly = []
            for k in range(3):
                a, b = int(tri[k]), int(tri[(k + 1) % 3])
                da, db = d3[k], d3[(k + 1) % 3]
                if da >= 0:
                    poly.append(a)
                if (da > 0 > db) or (da < 0 < db):
                    t = da / (da - db)
                    Vs.append(tuple(V[a] + t * (V[b] - V[a])))
                    poly.append(len(Vs) - 1)
            for k in range(1, len(poly) - 1):
                out.append((poly[0], poly[k], poly[k + 1]))
    return np.array(Vs), np.array(out, dtype=np.int64)


def quad(x0, x1, z0, z1, y, axis):
    """剖切处的封口面（矩形 → 两个三角形）"""
    if axis == 1:
        V = np.array([[x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1]])
    else:
        V = np.array([[y, x0, z0], [y, x1, z0], [y, x1, z1], [y, x0, z1]])
    return V, np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int64)


def merge(*meshes):
    Vs, Fs, off = [], [], 0
    for V, F in meshes:
        if len(F) == 0:
            continue
        Vs.append(V)
        Fs.append(F + off)
        off += len(V)
    return np.concatenate(Vs), np.concatenate(Fs)


def pcb_meshes(clip):
    if clip is None:
        return [(PCB_V, PCB_F)]
    (x0, x1, y0, y1, z0, z1) = clip
    V, F = clip_mesh(PCB_V, PCB_F, 1, y0)
    cap = quad(0.0, B.BW, B.Z_BOARD_BOT, 0.0, y0, 1)
    return [merge((V, F), cap)]


def m4_meshes(clip):
    if clip is None:
        return [(M4_V, M4_F)]
    (x0, x1, y0, y1, z0, z1) = clip
    V, F = clip_mesh(M4_V, M4_F, 1, y0)
    cx, cy = A.MOD4G_C
    w, dd, h = B.MOD4G["w"], B.MOD4G["d"], B.MOD4G["h"]
    cap = quad(cx - w / 2, cx + w / 2, B.Z_BOARD_BOT - h, B.Z_BOARD_BOT, y0, 1)
    return [merge((V, F), cap)]


def parts(clip=None, no_lid=False):
    out = []
    for nm, key in (("tray", "tray"), ("lid", "lid"), ("joystick", "joystick")):
        if no_lid and nm == "lid":
            continue
        V, F = R.load(STEP[key], clip)
        out.append((nm, V, F, np.array(C[key])))
    Vb, Fb = R.load(STEP["button"], clip)
    if len(Vb):
        out.append(("button_R", Vb, Fb, np.array(C["button"])))
        out.append(("button_L", Vb + np.array([5.85, 0.0, 0.0]), Fb, np.array(C["button"])))
    for V, F in pcb_meshes(clip):
        out.append(("pcb", V, F, np.array(C["pcb"])))
    for V, F in m4_meshes(clip):
        out.append(("mod4g", V, F, np.array(C["mod4g"])))
    return [p for p in out if len(p[2]) > 0]


# ---------------------------------------------------------------- 2D 堆叠剖面
def sch_stack():
    fig, ax = plt.subplots(figsize=(12.6, 6.6))
    zc, zf, zfb = B.Z_BOARD_BOT, B.Z_BOT_IN, B.Z_FLOOR_BOT
    tray_fc, wall_ec = "#d9a878", "k"
    # 底板
    ax.add_patch(Rectangle((B.OX0, zfb), B.OX1 - B.OX0, zf - zfb, fc=tray_fc, ec=wall_ec, lw=1))
    ax.text(B.BW / 2, (zfb + zf) / 2, "托盘底板 1.6 mm", ha="center", va="center", fontsize=9)
    # 左右侧壁（含 1.0 mm 台面）
    for x0, x1 in ((B.OX0, B.LX0), (B.LX1, B.OX1)):
        ax.add_patch(Rectangle((x0, zf), x1 - x0, B.Z_WALL_TOP - zf, fc=tray_fc, ec=wall_ec, lw=1))
    # 台面高亮（z = -1.0 的那圈 1.0 mm 平面）
    for x0, x1 in ((B.IX0, B.LX0), (B.LX1, B.IX1)):
        ax.plot([x0, x1], [B.Z_LEDGE, B.Z_LEDGE], color="#7a3b0a", lw=3)
    ax.annotate("台面 1.0 mm 宽", xy=(0.15, B.Z_LEDGE), xytext=(6.0, B.Z_LEDGE - 2.4),
                fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.7))

    mw, md, mh = B.MOD4G["w"], B.MOD4G["d"], B.MOD4G["h"]
    cx = A.MOD4G_C[0]
    ax.add_patch(Rectangle((cx - mw / 2, zc - mh), mw, mh, fc="#e0897c", ec="k", lw=1))
    ax.text(cx, zc - mh / 2, "背面 4G 模块包络 %.0f×%.0f×%.1f" % (mw, md, mh),
            ha="center", va="center", fontsize=8.5)
    ax.add_patch(Rectangle((0, zc), B.BW, B.BT, fc="#2f6b3a", ec="k", lw=1))
    ax.text(B.BW * 0.28, zc + B.BT / 2, "主板 %.1f mm" % B.BT, color="w",
            ha="center", va="center", fontsize=8.5)
    ax.add_patch(Rectangle((B.OX0, B.Z_PLATE_TOP - 2.0), B.OX1 - B.OX0, 2.0,
                           fc="#ad6030", ec="k", lw=1))
    ax.text(B.BW / 2, B.Z_PLATE_TOP - 1.0, "盖板 2.0 mm", color="w",
            ha="center", va="center", fontsize=9)

    def dim(z, txt, x, color="k"):
        ax.annotate("", xy=(x, z), xytext=(x, 0),
                    arrowprops=dict(arrowstyle="<->", lw=0.8, color=color))
        ax.text(x + 0.8, z / 2, txt, fontsize=8.5, va="center", color=color)

    dim(zc, "板底 %.1f\n(=台面)" % zc, 58.5)
    dim(zc - mh, "4G 底面 %.2f" % (zc - mh), 64.5)
    dim(zf, "下腔底 %.2f" % zf, 71.0)
    dim(zc - mh - (zf - zc + mh), "", 77.0) if False else None
    # 4G 余量
    ax.annotate("", xy=(77.0, zf), xytext=(77.0, zc - mh),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="crimson"))
    ax.text(77.8, (zf + zc - mh) / 2, "余量\n%.1f" % (zc - mh - zf), fontsize=8.5,
            va="center", color="crimson")
    # 内腔净高
    ax.annotate("", xy=(50.5, B.Z_WALL_TOP - 0.0), xytext=(50.5, B.Z_LEDGE),
                arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(49.3, (B.Z_WALL_TOP + B.Z_LEDGE) / 2 + 1.0,
            "内腔净高 %.1f\n(最高件 8.70，余 3.80)" % (B.Z_WALL_TOP - B.Z_LEDGE),
            fontsize=8.5, ha="right", va="center")
    ax.set_xlim(-6, 84)

    ax.set_xlim(-6, 84)
    ax.set_ylim(zfb - 1.4, B.Z_PLATE_TOP + 1.6)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("z (mm)  板顶面 = 0")
    ax.set_title("板厚 1.0 mm 装配堆叠：底板 1.6 → 4G 模块 2.4 → 主板 1.0 → 台面 → 盖板 2.0")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    p = OUT + "/sch_stack.png"
    fig.savefig(p, dpi=160)
    print("wrote", p)


if __name__ == "__main__":
    R.render(parts(), (-125, 32), "assy_iso",
             "装配体：托盘 + 主板(1.0 mm) + 4G 包络 + 盖板 + 摇杆帽")

    clip = (-2.80, 56.50, YCUT, 38.00, -7.10, 18.00)
    R.render(parts(clip), (-125, 24), "assy_cut",
             "剖开 y<15.19：主板落 1.0 mm 台面，板下 4G 模块 2.4 高，尚余 2.0")

    R.render(parts(no_lid=True), (-118, 42), "assy_inside",
             "去掉盖板：主板在腔内（左侧 USB-A / 烧录口 / TYPE-C，右下 LED 与摇杆）")

    sch_stack()
