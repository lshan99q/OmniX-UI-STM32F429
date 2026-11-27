#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""v3 探针自检：固体判定（0.24 mm 立方探针与实体求交）+ 三件干涉体积。

下方 CASE 表里的坐标是「版面坐标」（x 右 / y 下 / z 板顶面向上，方便对着 EasyEDA 版面数），
STEP 里是「实物坐标」（y 上）。运行时用 y → BH − y 反射一次，两者对齐。"""
import os
import cadquery as cq

OUT = ROOT + "//out"
P = 0.12          # 探针半边长 → 0.24 mm 立方
BH = 35.19        # 板宽（y 方向）


def mirror_y(y):
    """版面坐标 y（向下）→ 实物坐标 y（向上）"""
    return BH - y


def load(n):
    return cq.importers.importStep(os.path.join(OUT, "stm32f429_%s.step" % n)).val()


tray, lid, joy = load("tray"), load("lid"), load("joystick")
btn = load("button")
allp = tray.fuse(lid).fuse(joy)
SHAPES = {"tray": tray, "lid": lid, "joystick": joy, "button": btn}


def solid(shape, x, y, z):
    probe = cq.Workplane("XY").box(2 * P, 2 * P, 2 * P).translate((x, y, z)).val()
    try:
        v = shape.intersect(probe).Volume()
    except Exception:
        return False
    return v > 0.35 * (2 * P) ** 3


CASES = [
    # ---- 托盘：左壁三个阶梯窗必须通
    ("USB-A 窗口透空", tray, (-1.6, 9.0, 2.0), False),
    ("USB-A 窗口上部(y=9,z=6)", tray, (-1.6, 9.0, 6.0), False),
    ("USB-A 窗口上方有墙", tray, (-1.6, 9.0, 7.5), True),
    ("CN1 窗口透空", tray, (-1.6, 20.0, 2.0), False),
    ("CN1 窗口上方有墙", tray, (-1.6, 20.0, 6.0), True),
    ("USB-C 窗口透空", tray, (-1.6, 30.0, 1.0), False),
    ("USB-C 窗口上方有墙", tray, (-1.6, 30.0, 5.0), True),
    ("窗口下方窗台(x=-1.6,y=9,z=-2.0)", tray, (-1.6, 9.0, -2.0), True),
    ("左壁 y=1 段完整", tray, (-1.6, 1.0, 2.0), True),
    ("左壁 y=35 端头完整", tray, (-1.6, 35.0, 2.0), True),
    # ---- 右壁：整面封闭
    ("右壁 y=8 封闭", tray, (55.5, 8.0, 2.0), True),
    ("右壁 y=20 封闭", tray, (55.5, 20.0, 2.0), True),
    ("右壁 y=30 封闭", tray, (55.5, 30.0, -1.0), True),
    # ---- 底板
    ("底板中心实心", tray, (27.0, 17.0, -6.2), True),
    ("底板四角实心", tray, (1.0, 1.0, -6.2), True),
    ("板下空间空", tray, (27.0, 17.0, -3.0), False),
    ("台面承板处实心", tray, (0.2, 17.0, -1.15), True),
    ("台面承板右", tray, (53.8, 17.0, -1.15), True),
    ("台面上方空(板位)", tray, (0.2, 17.0, -0.85), False),
    ("板下 4G 位空", tray, (27.0, 17.0, -2.00), False),
    ("上腔空（板位）", tray, (27.0, 17.0, 0.0), False),
    ("侧壁实心(右上)", tray, (27.0, -1.5, 5.0), True),
    # ---- 背面侧键：避让槽 + 独立按钮孔
    ("侧键避让槽空(1)", tray, (43.00, 35.80, -2.25), False),
    ("侧键避让槽空(2)", tray, (50.00, 35.80, -2.25), False),
    ("避让槽外仍是墙", tray, (48.60, 37.50, -2.25), True),
    ("两避让槽之间留墙", tray, (47.95, 35.80, -2.25), True),
    ("避让槽外端留墙", tray, (53.45, 35.80, -2.25), True),
    ("按钮孔空(1)", tray, (45.03, 37.50, -1.90), False),
    ("按钮孔空(2)", tray, (50.88, 37.50, -1.90), False),
    ("按钮孔上壁实心", tray, (45.03, 37.50, 0.90), True),
    ("两按钮孔之间留墙", tray, (47.95, 37.50, -1.90), True),
    ("按钮件：杆实心", "button", (45.03, 37.50, -1.90), True),
    ("按钮件：帽实心", "button", (45.03, 39.10, -1.90), True),
    ("按钮件：杆旁空", "button", (45.03, 37.50, 1.10), False),
    ("两侧键区之间壁料(x=41)", tray, (41.0, 38.55, -2.25), True),
    # ---- 盖板
    ("OLED 屏窗透空", lid, (19.44, 18.69, 13.5), False),
    ("OLED 窗角(2.8,6.5)", lid, (2.8, 6.5, 13.5), False),
    ("OLED 窗右侧有料(x=37)", lid, (37.0, 18.69, 13.5), True),
    ("LED 孔1 透空", lid, (39.59, 24.47, 13.5), False),
    ("LED 孔2 透空", lid, (39.59, 28.66, 13.5), False),
    ("LED 孔3 透空", lid, (39.59, 33.02, 13.5), False),
    ("RGB 位置不开孔(应实心)", lid, (34.06, 2.97, 13.5), True),
    ("摇杆座孔透空", lid, (46.60, 29.30, 13.5), False),
    ("摇杆座沉台(内面)", lid, (51.0, 29.30, 12.95), False),
    ("摇杆座外圈有料", lid, (52.5, 29.30, 13.5), True),
    ("盖板左边缘有料", lid, (0.0, 20.0, 13.5), True),
    ("盖板前边缘有料", lid, (20.0, 36.0, 13.5), True),
    ("定位唇实心", lid, (0.0, 20.0, 11.8), True),
    ("定位唇内侧空", lid, (3.0, 20.0, 11.8), False),
    # ---- 摇杆帽
    # 套筒式：内孔 φ3.36 套住开关 ø3.00 摇杆（摇杆顶 8.00，套内顶 8.15，套口 6.30）
    ("套筒内孔空(让位摇杆)", joy, (46.60, 29.30, 7.20), False),
    ("套筒内孔空(近套口)", joy, (46.60, 29.30, 6.60), False),
    ("套筒内顶面之上实心", joy, (46.60, 29.30, 8.45), True),
    ("套筒壁实心(+x)", joy, (46.60 + 2.40, 29.30, 7.60), True),
    ("套筒壁实心(-x)", joy, (46.60 - 2.40, 29.30, 7.60), True),
    ("套筒壁实心(+y)", joy, (46.60, 29.30 + 2.40, 7.60), True),
    ("套筒外空(不碰开关本体)", joy, (46.60, 29.30 + 3.40, 6.90), False),
    ("杆 φ4.5 存在", joy, (46.60 + 1.60, 29.30, 11.50), True),
    ("杆外空(φ4.5→φ8.8 间)", joy, (46.60, 29.30 + 3.00, 11.50), False),
    ("颈在孔内", joy, (46.60, 29.30, 14.2), True),
    ("卡爪在沉台高度", joy, (49.6, 26.30, 13.1), True),
    ("帽本体", joy, (49.0, 29.30, 16.0), True),
    ("帽外无料", joy, (52.5, 29.30, 16.0), False),
    # ---- 背面侧键：随板厚 1.0 上移后的位置（键体 -2.80..-1.00）
    ("台面以上墙料(45)", tray, (45.03, 38.55, 1.50), True),
    ("台面以上墙料(43)", tray, (43.00, 37.00, -0.80), True),
    ("避让槽下方实心", tray, (43.00, 37.00, -3.60), True),
    # ---- 组合
    ("盖上后：盖板实心处", allp, (50.0, 20.0, 13.5), True),
]


def main():
    bad = 0
    n_total = 0
    for name, shape, (x, y, z), want in CASES:
        sh = SHAPES[shape] if isinstance(shape, str) else shape
        got = solid(sh, x, mirror_y(y), z)
        ok = got == want
        bad += not ok
        n_total += 1
        print("%s %-34s (%5.1f,%5.1f,%5.1f) 期望 %s 实测 %s"
              % ("  OK " if ok else " FAIL", name, x, y, z, want, got))
    for a, b, n in ((tray, lid, "tray∩lid"), (tray, joy, "tray∩joy"),
                    (lid, joy, "lid∩joy"), (tray, btn, "tray∩button"),
                    (lid, btn, "lid∩button"), (joy, btn, "joy∩button")):
        v = a.intersect(b).Volume()
        ok = v < 0.05
        print("%s %-12s = %.4f mm3" % ("  OK " if ok else " FAIL", n, v))
        bad += not ok
        n_total += 1
    # ---- 五向键 K1-5203UA-01 包络（图纸：本体 7.50×7.50×5.00，摇杆 ø3.00 顶面 8.00）
    cx, cy = 46.60, 29.30
    body = cq.Workplane("XY").box(7.50, 7.50, 5.00).translate((cx, cy, 2.50)).val()
    stem = cq.Workplane("XY").circle(1.50).extrude(3.00).translate((cx, cy, 5.00)).val()
    sw = body.fuse(stem)
    for a, n in ((tray, "tray∩开关包络"), (lid, "lid∩开关包络"), (joy, "摇杆∩开关包络")):
        v = a.intersect(sw).Volume()
        ok = v < 0.05
        print("%s %-14s = %.4f mm3" % ("  OK " if ok else " FAIL", n, v))
        bad += not ok
        n_total += 1
    # ---- 背面侧键包络（OBJ：4.60 × 3.55 × 1.80，外表面伸出板边 0.86）
    import build_case as B
    # 包络按实物坐标摆（托盘是反射后的）：y 中心 = BH − 版面 y 中心
    swb = (cq.Workplane("XY").box(4.60, 3.55, 1.80)
           .translate((45.03, BH - (B.SW_FACE - 3.55 / 2), (B.BTN_Z0 + B.BTN_Z1) / 2)).val())
    for a, n in ((tray, "tray∩侧键包络"), (btn, "button∩侧键包络")):
        v = a.intersect(swb).Volume()
        ok = v < 0.05
        print("%s %-14s = %.4f mm3" % ("  OK " if ok else " FAIL", n, v))
        bad += not ok
        n_total += 1
    # ---- 背面 4G 模块（EC600S 26×26×2.4）扫掠包络
    mw, md, mh = 26.0, 26.0, 2.4
    LX0, LX1, LY0, LY1 = 0.65, 53.05, 0.65, 35.39
    zb = -1.00
    sx = cq.Workplane("XY").box((LX1 - LX0) - mw, (LY1 - LY0) - md, mh) \
         .translate(((LX0 + LX1) / 2, (LY0 + LY1) / 2, zb - mh / 2)).val()
    for a, nm in ((tray, "tray∩4G 包络"), (lid, "lid∩4G 包络")):
        v = a.intersect(sx).Volume()
        ok = v < 0.05
        print("%s %-16s = %.4f mm3" % ("  OK " if ok else " FAIL", nm, v))
        bad += not ok
        n_total += 1
    # ---- 关键间隙报数
    print("\n--- 关键间隙 ---")
    print("     五向键：摇杆顶 8.00 → 套内顶 8.15（空程 0.15）；套口 6.30 vs 本体顶 5.00（净空 1.30）")
    print("     按钮：杆内端 %.2f → 侧键外表面 %.2f（空程 %.2f）；按压总行程 %.2f mm"
          % (B.BTN_END, B.SW_FACE, B.BTN_END - B.SW_FACE, (B.BTN_END - B.SW_FACE) + B.SW_PUSH))
    print("     侧键避让槽：槽底 %.2f → 侧键外表面 %.2f（间隙 %.2f）"
          % (B.BTN_NOTCH_Y1, B.SW_FACE, B.BTN_NOTCH_Y1 - B.SW_FACE))
    print("     4G 模块 %.0f×%.0f×%.1f：贴板底 %.2f → 底面 %.2f，下腔底 -5.40，余量 %.2f"
          % (mw, md, mh, zb, zb - mh, zb - mh + 5.40))
    print("\n%d / %d 通过" % (n_total - bad, n_total))


if __name__ == "__main__":
    main()
