#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""装入自检：把真实 PCB（pcb3d.obj，含全部有 3D 模型的器件）光栅化成
顶/底高度图，逐格判定是否撞到外壳实体（底板、侧壁、台面、前壁按键膜、盖板、
摇杆），并核对接插件是否落在开孔窗内。

坐标系：x 右 / y 下 / z 板顶面向上，mm。
"""
import numpy as np

import build_case as B

OBJ = ROOT + "//pcb3d.obj"
S = 0.254
X0, Y0, ZT = 4048.20, -3047.20, 10.0
RES = 0.10                     # mm / cell

# ---- 外壳关键面：直接从 build_case 取，避免两边不同步 ----
IX0, IX1, IY0, IY1 = B.IX0, B.IX1, B.IY0, B.IY1
LX0, LX1, LY0, LY1 = B.LX0, B.LX1, B.LY0, B.LY1
OX0, OX1, OY0, OY1 = B.OX0, B.OX1, B.OY0, B.OY1
Z_LEDGE, Z_BOT_IN = B.Z_LEDGE, B.Z_BOT_IN
Z_WALL_TOP, Z_PLATE_TOP = B.Z_WALL_TOP, B.Z_PLATE_TOP
BT = B.BT
BH = B.BH                       # 板宽（y 方向）
MOD4G = B.MOD4G
Z_SHIFT_BOT = 2.54 - BT          # 模型板厚 2.54 → 真实板厚；底面器件整体上移量

# 本脚本内部用「版面坐标」（y 向下，和 EasyEDA 版面一致）判撞；报数时用 MY() 换成
# 「实物坐标」（y 向上，与导出的 STL/STEP 一致），方便和成品图对照。


def MY(y):
    """版面坐标 y → 实物坐标 y"""
    return BH - y


LEFT_WINDOWS = B.LEFT_WINDOWS                    # USB-A / CN1 / USB-C
# 前壁侧键避让槽（台面以下，每个侧键一块）
BTN_NOTCH = dict(hx=B.BTN_NOTCH_X, y0=B.BTN_NOTCH_Y0, y1=B.BTN_NOTCH_Y1,
                 z0=B.BTN_NOTCH_Z0, z1=B.Z_LEDGE)
BTN_CX = B.BTN_CX


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


def raster(V, F):
    """返回 (x, y, ztop, zbot) 四张同形格点图；空格 ztop=-1e9 / zbot=+1e9。"""
    xs = (V[:, 0] - X0) * S
    ys = (-3047.20 - V[:, 1]) * S
    # 保守起见不做板厚修正：模型板厚 2.54 → 底面器件比真实情况更深 (2.54 − BT) mm
    zs = (V[:, 2] - ZT) * S
    lo_x, hi_x = -8.0, 62.0
    lo_y, hi_y = -6.0, 44.0
    nx, ny = int((hi_x - lo_x) / RES) + 2, int((hi_y - lo_y) / RES) + 2
    top = np.full((ny, nx), -1e9, np.float32)
    bot = np.full((ny, nx), 1e9, np.float32)
    px = (xs - lo_x) / RES
    py = (ys - lo_y) / RES
    for tri in F:
        tx, ty, tz = px[tri], py[tri], zs[tri]
        i0, i1 = max(int(np.floor(tx.min())), 0), min(int(np.ceil(tx.max())), nx - 1)
        j0, j1 = max(int(np.floor(ty.min())), 0), min(int(np.ceil(ty.max())), ny - 1)
        if i1 < i0 or j1 < j0:
            continue
        gx, gy = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1))
        # 重心坐标判格心是否在三角形内
        det = (ty[1] - ty[2]) * (tx[0] - tx[2]) + (tx[2] - tx[1]) * (ty[0] - ty[2])
        if abs(det) < 1e-12:
            continue
        l0 = ((ty[1] - ty[2]) * (gx - tx[2]) + (tx[2] - tx[1]) * (gy - ty[2])) / det
        l1 = ((ty[2] - ty[0]) * (gx - tx[2]) + (tx[0] - tx[2]) * (gy - ty[2])) / det
        l2 = 1.0 - l0 - l1
        m = (l0 >= -0.02) & (l1 >= -0.02) & (l2 >= -0.02)
        if not m.any():
            continue
        z = l0 * tz[0] + l1 * tz[1] + l2 * tz[2]
        ii, jj = gx[m], gy[m]
        zz = z[m]
        np.maximum.at(top, (jj, ii), zz)
        np.minimum.at(bot, (jj, ii), zz)
    return lo_x, lo_y, top, bot


def main():
    V, F = load()
    lo_x, lo_y, top, bot = raster(V, F)
    ny, nx = top.shape
    gy, gx = np.meshgrid(np.arange(ny), np.arange(nx), indexing='ij')
    px = gx * RES + lo_x + RES / 2
    py = gy * RES + lo_y + RES / 2
    occ = top > -1e8
    print("光栅格 %d x %d，占用 %.0f 格（%.2f mm 分辨率网格）" % (nx, ny, occ.sum(), RES))

    problems = []

    # 1) 顶面是否顶到盖板内表面 / 侧壁
    over = occ & (top > Z_WALL_TOP + 1e-6)
    if over.any():
        for (y_, x_) in zip(*np.where(over)):
            problems.append("顶面撞盖板内表面 (%.2f,%.2f) 顶=%.2f > %.1f"
                            % (px[y_, x_], MY(py[y_, x_]), top[y_, x_], Z_WALL_TOP))

    # 2) 底面是否撞底板
    under = occ & (bot < Z_BOT_IN - 1e-6)
    if under.any():
        for (y_, x_) in zip(*np.where(under)):
            problems.append("底面穿出底板顶面 (%.2f,%.2f) 底=%.2f < %.1f"
                            % (px[y_, x_], MY(py[y_, x_]), bot[y_, x_], Z_BOT_IN))

    # 3) 侧壁 / 台面：落在上腔之外但在外壳之内
    out_cav = occ & ((px < IX0) | (px > IX1) | (py < IY0) | (py > IY1))
    for (y_, x_) in zip(*np.where(out_cav)):
        x, y = px[y_, x_], py[y_, x_]
        zt, zb = top[y_, x_], bot[y_, x_]
        in_env = (OX0 - 1e-6 <= x <= OX1 + 1e-6) and (OY0 - 1e-6 <= y <= OY1 + 1e-6)
        if not in_env:
            continue
        # 左壁窗口
        if x < IX0:
            hit = True
            for (y0, y1, z0, z1) in LEFT_WINDOWS:
                if y0 - 1e-6 <= y <= y1 + 1e-6 and z0 - 1e-6 <= zb and zt <= z1 + 1e-6:
                    hit = False
                    break
            if hit:
                problems.append("左壁干涉 (%.2f,%.2f) z=%.2f..%.2f" % (x, MY(y), zb, zt))
        # 前壁侧键避让槽（槽内合法：侧键伸进墙里的 0.66 住在这里）
        elif y > IY1:
            ok = False
            for bx in BTN_CX:
                if (abs(x - bx) <= BTN_NOTCH["hx"] + 1e-6
                        and BTN_NOTCH["z0"] - 1e-6 <= zb
                        and zt <= BTN_NOTCH["z1"] + 1e-6
                        and y <= BTN_NOTCH["y1"] + 1e-6):
                    ok = True
                    break
            if ok:
                continue
            problems.append("前壁干涉 (%.2f,%.2f) z=%.2f..%.2f" % (x, MY(y), zb, zt))
        else:
            problems.append("后壁/右壁干涉 (%.2f,%.2f) z=%.2f..%.2f" % (x, MY(y), zb, zt))

    # 4) 插接件是否伸到窗口外（应当看得见）
    print("\n--- 插接件穿窗核对 ---")
    carrier = [(x, y) for (y_, x_) in zip(*np.where(occ)) for x, y in [(px[y_, x_], py[y_, x_])]
               if x < IX0]
    if carrier:
        cx = np.array([c[0] for c in carrier])
        cy = np.array([c[1] for c in carrier])
        print("伸出左壁内面的格点数 %d，x 最外 %.2f mm（外壳外面 x=%.2f），y %.2f..%.2f"
              % (len(carrier), cx.min(), OX0, MY(cy.max()), MY(cy.min())))

    # 5) 关键器件高度余量
    print("\n--- 高度余量 ---")
    print("顶面最高 %.2f mm（盖板内表面 %.1f → 余量 %.2f）"
          % (top[occ].max(), Z_WALL_TOP, Z_WALL_TOP - top[occ].max()))
    print("底面最低 %.2f mm（底板顶面 %.1f → 余量 %.2f）"
          % (bot[occ].min(), Z_BOT_IN, bot[occ].min() - Z_BOT_IN))
    print("台面接触：板底 %.2f，台面 %.2f（板厚 %.1f）" % (-BT, Z_LEDGE, BT))
    print("底面器件按 %.2f 板厚修正后最深 = %.2f mm（模型值 +%.2f）"
          % (BT, bot[occ].min() + Z_SHIFT_BOT, Z_SHIFT_BOT))

    # 6) 背面 4G 模块（EC600S 26×26×2.4）可用空间：在下腔平面内滑动，取扫掠包络
    mw, md, mh = MOD4G["w"], MOD4G["d"], MOD4G["h"]
    zx0, zx1 = LX0 + mw / 2, LX1 - mw / 2        # 模块中心可落在的范围
    zy0, zy1 = LY0 + md / 2, LY1 - md / 2
    print("\n--- 背面 4G 模块 ---")
    print("模块 %.1f × %.1f × %.1f，模块顶面贴板底 %.2f → 底面 %.2f；下腔底 %.2f（余量 %.2f）"
          % (mw, md, mh, Z_LEDGE, Z_LEDGE - mh, Z_BOT_IN, Z_LEDGE - mh - Z_BOT_IN))
    print("模块中心可放置范围：x %.2f..%.2f，y %.2f..%.2f（版面坐标），整块板下方都是空的"
          % (zx0, zx1, zy0, zy1))
    import cadquery as cq
    swept = (cq.Workplane("XY").box(zx1 - zx0, zy1 - zy0, mh)
             .translate(((zx0 + zx1) / 2, (zy0 + zy1) / 2, Z_LEDGE - mh / 2)))
    tray = cq.importers.importStep(ROOT + "//out/stm32f429_tray.step").val()
    # 扫掠体是版面坐标，实物件已镜像 → 用 y 对称性：把扫掠体按 BH 反射后一起算
    swept_m = swept.val().mirror("XZ").translate(cq.Vector(0, BH, 0))
    v = tray.intersect(swept_m).Volume()
    print("扫掠包络 ∩ 托盘 = %.4f mm3 %s" % (v, "（任何位置都放得下）" if v < 0.05 else "**干涉**"))
    if v >= 0.05:
        problems.append("4G 模块扫掠包络与托盘干涉 %.2f mm3" % v)

    print("\n--- 结论 ---")
    if problems:
        print("%d 处干涉：" % len(problems))
        for p in problems[:40]:
            print("  " + p)
        if len(problems) > 40:
            print("  ... 共 %d 条" % len(problems))
    else:
        print("无干涉：整板（含全部有 3D 模型的器件）落在外壳空腔内。")
    return len(problems)


if __name__ == "__main__":
    raise SystemExit(0 if main() == 0 else 1)
