#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""
STM32F429 mini 4G 物联网开发板 —— 上层主板外壳 v3（封闭底 / 三件套）
=====================================================================
几何来源：用户提供的真实 3D 模型 OBJ_PCB-主板.obj
  · 单位标定：LQFP-100 本体 55.10 unit = 14.00 mm → S = 0.254 mm/unit（10 mil）
  · 板框：x 0 .. 53.70，y 0 .. 35.19（四角直角，无圆角）
  · z = 0 为板顶面；模型里板被画成 2.54 mm 厚，**真实板厚 1.0 mm**（用户实测）
    （底面器件高度 = 模型值 + 1.54 mm 修正）

零件：
  A 托盘 tray   —— 封闭底 + 四面侧壁；主板从上方落入内圈台面
  B 盖板 lid    —— 2 mm 顶板：OLED 屏窗（贴玻璃、直角）+ 3×LED 孔 + 五向摇杆座
  C 摇杆帽 joystick —— 卡进盖板的五向摇杆，顶针压下五向键

坐标（两套，务必分清）：
  · 参数区/建模用「版面坐标」：原点 = 主板外形左上角（俯视），X 右、Y 下、Z 上。
    这是 EasyEDA 版面/截图的方向，取点方便，但它**是左手系**。
  · 导出用「实物坐标」：X 右、Y 上、Z 上 —— 与 pcb3d.obj 一致（右手系），
    pcb3d.obj 里 +Z 朝板顶面、+Y 朝板的上边缘、+X 朝板的右边缘。
  pcb3d.obj 是右手系，按版面坐标取点等于整体镜像了一次，所以 main() 导出前
  统一做 y → BH − y 的反射（MIRROR_OUT），出来的才是真实零件。
  实物坐标下：板 y 0..35.19，RESET/POWER 在 y ≈ −0.86..2.69 一侧。

运行：  /home/lshan/.venv-cad/bin/python build_case.py
"""
import math
import os
import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")

# 背面 4G 模块（EC600S，LCC 26.0×26.0×2.4）：OBJ 里没有 3D 模型，只按包络校核
MOD4G = dict(w=26.0, d=26.0, h=2.4)

# ---------------------------------------------------------------- 主板（来自 OBJ）
BW, BH = 53.70, 35.19          # 板框实测（OBJ）
BT = 1.0                       # 板厚（用户实测 1.0，模型里画的是 2.54）
Z_BOARD_BOT = -BT

CL_L, CL_R, CL_T, CL_B = 0.35, 0.35, 0.35, 1.20   # 板边→内壁间隙；B 大是给背面侧键（外伸 0.86）
WALL = 2.4
CORNER_R = 3.0

Z_LEDGE = Z_BOARD_BOT              # -1.6 内圈台面（承板面）
Z_WALL_TOP = 12.5                  # 侧壁顶 = 盖板内表面
Z_PLATE_TOP = Z_WALL_TOP + 2.0     # 14.5 盖板外表面
Z_BOT_IN = -5.4                    # 托盘内底：板下 4.4 mm（背面：4G 模块 2.4 / 侧键 1.80 都够）
Z_FLOOR_BOT = Z_BOT_IN - 1.6       # -7.0 底板厚 1.6
LEDGE_W = 1.0

IX0, IX1 = -CL_L, BW + CL_R
IY0, IY1 = -CL_T, BH + CL_B
OX0, OX1 = IX0 - WALL, IX1 + WALL
OY0, OY1 = IY0 - WALL, IY1 + WALL
LX0, LX1 = IX0 + LEDGE_W, IX1 - LEDGE_W
LY0, LY1 = IY0 + LEDGE_W, IY1 - LEDGE_W

# ---------------------------------------------------------------- 左壁开孔（OBJ 实测）
# USB-A  ：丝印实测 y 2.5..15.5（12.8×10 footprint，H5.7）
# CN1    ：2×4P 2.0 mm 弯针（烧录/串口），本体 y 16.40..24.40 z 0..3.80，引脚外伸 4.33
# USB-C  ：y 25.32..34.26 z -1.00..3.10
LEFT_WINDOWS = [
    # (y0,   y1,    z0,    z1)
    (2.40, 15.70, -1.60, 6.50),    # USB-A
    (15.70, 24.90, -1.60, 4.60),   # CN1（要能穿过外伸的弯针）
    (24.90, 34.70, -1.60, 3.80),   # USB-C
]

# 盖板开孔（板坐标 mm，来自 OBJ）
OLED_W, OLED_H, OLED_CX, OLED_CY = 33.6, 24.6, 19.44, 18.69   # 屏玻璃实测
LED_R = 0.75                                                    # 可见孔径 φ1.50（原 φ3.20）
LED_FLARE_R = 2.00                                               # 内面喇叭口 φ4.00
LEDS = [(39.59, 24.47), (39.59, 28.66), (39.59, 33.02)]        # OBJ 实测 3× φ3 直插
JOY_C, JOY_HOLE_R = (46.60, 29.30), 4.80                        # 五向键中心（丝印中心焊盘）
JOY_RECESS_Z0, JOY_RECESS_Z1 = 12.50, 13.40                     # 盖板内面沉台（卡爪卡在这里）
JOY_BARB_R = 5.30                                               # 卡爪 φ10.6（> 孔 φ9.6 才能卡住）
JOY_CAP_R = 5.50                                                # 帽 φ11（避让 39.59 那列 LED 孔）
PLUNGER_Z = 6.20                                                # （旧）顶针下端；已由套筒方案替代
# ---- 五向键 K1-5203UA-01（厂商图纸 2021-06-22 版，单位 mm，基准 = PCB 顶面）----
SW_BODY_H = 5.00        # 本体高（8.60 flange / 7.50 方形本体）
SW_STEM_R = 1.50        # 摇杆 ø3.00
SW_STEM_TOP = 8.00      # 摇杆顶面（本体 5.00 + 露出 3.00）
SW_PUSH = 0.20          # 中心按压行程 0.20±0.10，力 250/350/450 gf
SW_LEVER = 5.0          # 四向杠杆 5°±2°，力 170±35 gf
# 摇杆帽的“套筒”端：内孔套住 ø3.00 摇杆，靠套壁把倾斜传给摇杆
JOY_SOCK_R = 1.68                       # 套内孔半径 → φ3.36（对 ø3.00 留 0.18/侧）
JOY_SOCK_WALL = 1.20                    # 套壁厚 → 套外径 φ5.76
JOY_SOCK_RIM = 6.30                     # 套口（本体顶面 5.00 上方 1.30，倾斜时不碰本体）
JOY_SOCK_CEIL = SW_STEM_TOP + 0.15      # 套内顶面 8.15：中心按压先吃掉 0.15 空程
JOY_SOCK_TOP = JOY_SOCK_CEIL + 1.20     # 套筒外顶面 9.35
SHAFT_R = 2.25                          # 套顶到帽底的杆 φ4.50

# ---- 背面侧键 RESET / POWER（OBJ 实测 x 42.73..47.33 / 48.58..53.18，本体 4.6×3.5×1.80）----
BTN_CX = (45.03, 50.88)
BTN_H = 1.80                          # 侧键本体在板底以下的高度
BTN_Z0, BTN_Z1 = Z_BOARD_BOT - BTN_H, Z_BOARD_BOT      # -2.80 .. -1.00
BTN_ZC = (BTN_Z0 + BTN_Z1) / 2.0      # -1.90 侧键推动中心（本体高度中间）
SW_FACE = BH + 0.86                   # 36.05 侧键外表面（伸出板边 0.86，即按动弹片顶端）
# 侧键要伸进墙里 0.66，所以在墙内侧挖避让槽（只挖台面以下，台面照旧承板）
BTN_NOTCH_X = 2.40                    # 槽半宽（侧键半宽 2.30 + 0.10）
BTN_NOTCH_Y1 = SW_FACE + 0.10         # 36.15 槽底（离开关外表面 0.10）
BTN_NOTCH_Y0 = 34.60                  # 槽起点（在下腔里，无副作用）
BTN_NOTCH_Z0 = BTN_Z0 - 0.50          # -3.30
# 按钮孔 + 独立按钮件：靠侧键弹片把按钮顶在外墙面上定位，不需要卡扣、不需要胶
BTN_HOLE_R = 2.20                     # φ4.40 通孔
BTN_ROD_R = 2.00                      # φ4.00 杆（孔内 0.20 单边间隙）
BTN_CAP_R = 2.50                      # φ5.00 帽（> 孔，掉不进壳里）
BTN_CAP_H = 0.70                      # 帽厚（露出墙面 0.70）
BTN_END = SW_FACE + 0.09              # 36.14 杆内端面，离弹片 0.09 空程


def box3(x0, x1, y0, y1, z0, z1):
    lo = [min(x0, x1), min(y0, y1), min(z0, z1)]
    hi = [max(x0, x1), max(y0, y1), max(z0, z1)]
    return (cq.Workplane("XY").box(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
            .translate(tuple((lo[i] + hi[i]) / 2 for i in range(3))))


def cyl_z(cx, cy, r, z0, z1):
    return (cq.Workplane("XY").workplane(offset=z0).center(cx, cy)
            .circle(r).extrude(z1 - z0, clean=False))


def cyl_y(cx, cz, r, y0, y1):
    return (cq.Workplane("XY").circle(r).extrude(abs(y1 - y0), clean=False)
            .rotate((0, 0, 0), (1, 0, 0), 90).translate((cx, max(y0, y1), cz)))


# ---------------------------------------------------------------- A 托盘
def make_tray():
    t = box3(OX0, OX1, OY0, OY1, Z_FLOOR_BOT, Z_WALL_TOP).edges("|Z").fillet(CORNER_R)
    t = t.cut(box3(IX0, IX1, IY0, IY1, Z_LEDGE, Z_WALL_TOP + 1))        # 上腔
    t = t.cut(box3(LX0, LX1, LY0, LY1, Z_BOT_IN, Z_LEDGE))              # 下腔（留 1 mm 台面）
    # 盖板靠摩擦配合：上口不再开卡扣槽，保持完整内壁
    # 左壁：USB-A / CN1 / USB-C 阶梯窗
    for y0, y1, z0, z1 in LEFT_WINDOWS:
        t = t.cut(box3(OX0 - 2, IX0, y0, y1, z0, z1))
    # 背面侧键避让槽：只挖台面以下，让侧键伸进墙里的 0.66 有地方去
    for bx in BTN_CX:
        t = t.cut(box3(bx - BTN_NOTCH_X, bx + BTN_NOTCH_X,
                       BTN_NOTCH_Y0, BTN_NOTCH_Y1, BTN_NOTCH_Z0, Z_LEDGE))
    # 两个按钮孔：φ4.40 通孔，独立按钮件从外面插入
    for bx in BTN_CX:
        t = t.cut(cyl_y(bx, BTN_ZC, BTN_HOLE_R, BTN_NOTCH_Y0, OY1))
    return t


# ---------------------------------------------------------------- B 盖板
def make_lid():
    lid = box3(OX0, OX1, OY0, OY1, Z_WALL_TOP, Z_PLATE_TOP).edges("|Z").fillet(CORNER_R)
    # 定位唇：塞进托盘上口做摩擦配合（四周留 0.10 间隙），底端 0.8 导角
    lipx, lipy = 0.15, 0.15
    lip = box3(IX0 + lipx, IX1 - lipx, IY0 + lipy, IY1 - lipy, 11.20, Z_WALL_TOP)
    lip = lip.cut(box3(IX0 + lipx + 1.2, IX1 - lipx - 1.2,
                       IY0 + lipy + 1.2, IY1 - lipy - 1.2, 10.0, Z_WALL_TOP + 1))
    lead = box3(IX0 + lipx + 0.8, IX1 - lipx - 0.8,
                IY0 + lipy + 0.8, IY1 - lipy - 0.8, 10.0, Z_WALL_TOP + 1)
    lip = lip.cut((cq.Workplane("XY").workplane(offset=11.20)
                   .rect((IX1 - IX0) - 2 * lipx, (IY1 - IY0) - 2 * lipy)
                   .workplane(offset=0.9).rect((IX1 - IX0) - 2 * lipx - 1.8,
                                               (IY1 - IY0) - 2 * lipy - 1.8)
                   .loft()))
    lid = lid.union(lip)
    # 四条边各两条摩擦筋（与内壁齐平 → 名义零过盈，靠打印公差产生摩擦）
    ycs = (IY0 + lipy + (IY1 - IY0 - 2 * lipy) / 3,
           IY0 + lipy + 2 * (IY1 - IY0 - 2 * lipy) / 3)
    xcs = (IX0 + lipx + (IX1 - IX0 - 2 * lipx) / 3,
           IX0 + lipx + 2 * (IX1 - IX0 - 2 * lipx) / 3)
    for yc in ycs:
        lid = lid.union(box3(IX0 + lipx - 0.15, IX0 + lipx + 0.9, yc - 3, yc + 3, 11.90, 12.45))
        lid = lid.union(box3(IX1 - lipx - 0.9, IX1 - lipx + 0.15, yc - 3, yc + 3, 11.90, 12.45))
    for xc in xcs:
        lid = lid.union(box3(xc - 3, xc + 3, IY0 + lipy - 0.15, IY0 + lipy + 0.9, 11.90, 12.45))
        lid = lid.union(box3(xc - 3, xc + 3, IY1 - lipy - 0.9, IY1 - lipy + 0.15, 11.90, 12.45))
    # OLED 屏窗（直角、贴合玻璃）
    lid = lid.cut(box3(OLED_CX - OLED_W / 2, OLED_CX + OLED_W / 2,
                       OLED_CY - OLED_H / 2, OLED_CY + OLED_H / 2,
                       Z_WALL_TOP - 1, Z_PLATE_TOP + 1))
    # 3× LED 孔：外表面 φ1.5 小孔 + 内面喇叭口到 φ4.0（只露灯珠中间一点，灯不被切光）
    for cx, cy in LEDS:
        lid = lid.cut(cyl_z(cx, cy, LED_R, Z_PLATE_TOP - 0.02, Z_PLATE_TOP + 0.5))
        lid = lid.cut((cq.Workplane("XY").workplane(offset=Z_PLATE_TOP)
                       .center(cx, cy).circle(LED_R)
                       .workplane(offset=-(Z_PLATE_TOP - Z_WALL_TOP)).circle(LED_FLARE_R)
                       .loft()))
    # 摇杆座：φ9.6 通孔 + 孔口 0.6 倒角 + 内面 φ11.2 沉台（卡爪藏身处）
    lid = lid.cut(cyl_z(JOY_C[0], JOY_C[1], JOY_HOLE_R, Z_WALL_TOP - 1, Z_PLATE_TOP + 1))
    lid = lid.cut(cyl_z(JOY_C[0], JOY_C[1], 5.60, JOY_RECESS_Z0, JOY_RECESS_Z1))
    lid = lid.cut((cq.Workplane("XY").workplane(offset=Z_PLATE_TOP)
                   .center(*JOY_C).circle(JOY_HOLE_R + 0.7)
                   .workplane(offset=-0.6).circle(JOY_HOLE_R).loft()))
    return lid


# ---------------------------------------------------------------- C 摇杆帽
def make_joy():
    """一体五向摇杆帽（套筒式驱动）。

    驱动原理：下端不是顶针，而是一个 **内孔 φ3.36 的套筒**，套住开关的 ø3.00 摇杆
    （摇杆顶面 z=8.00，套内顶面 8.15，套口 6.30）。
      · 倾斜：帽绕 φ9.6 孔摆，套壁横向推摇杆 → 四向（图纸：杠杆 5°±2°，170±35 gf）
      · 按压：套内顶面下压 0.15 后顶到摇杆顶 → 中心（图纸：0.20±0.1 mm，250~450 gf）
    卡爪挤过 φ9.6 孔后在 φ11.2 沉台里张开，上提掉不出来；帽底 14.90，压到顶板面 14.50 为止。
    """
    cx, cy = JOY_C
    zt = 14.90                                    # 帽底（顶板面上 0.4，即按压行程）
    # 套筒：外 φ5.76，从套口 6.30 到外顶面 9.35；内孔 φ3.36 只挖到 8.15（留 1.2 顶壁）
    j = cyl_z(cx, cy, JOY_SOCK_R + JOY_SOCK_WALL, JOY_SOCK_RIM, JOY_SOCK_TOP)
    j = j.cut(cyl_z(cx, cy, JOY_SOCK_R, JOY_SOCK_RIM - 0.5, JOY_SOCK_CEIL))
    # 杆 φ4.50：套顶 → 帽底，穿过盖板 φ9.6 孔内的颈
    j = j.union(cyl_z(cx, cy, SHAFT_R, JOY_SOCK_TOP - 0.4, zt))
    j = j.union(cyl_z(cx, cy, 4.4, JOY_RECESS_Z1, zt))          # 颈 φ8.8（孔里，0.4 间隙可晃）
    j = j.union(cyl_z(cx, cy, JOY_BARB_R, 12.80, JOY_RECESS_Z1))  # 卡爪 φ10.6
    for k in range(3):                                          # 三条竖槽让卡爪能压缩
        a = math.radians(90 + 120 * k)
        gx, gy = cx + 6.0 * math.cos(a), cy + 6.0 * math.sin(a)
        j = j.cut(box3(gx - 0.45, gx + 0.45, gy - 4.2, gy + 4.2, 12.4, 13.45)
                  .intersect(cyl_z(cx, cy, 6.2, 12.4, 13.45)))
    j = j.union(cyl_z(cx, cy, JOY_CAP_R, zt, 17.70))            # 帽 φ11
    j = j.cut((cq.Workplane("XY").workplane(offset=17.70).center(cx, cy).circle(JOY_CAP_R)
               .workplane(offset=-1.0).circle(4.1).loft()))      # 顶面收口
    j = j.cut((cq.Workplane("XY").workplane(offset=16.90).center(cx, cy).circle(3.2)
               .workplane(offset=1.0).circle(4.4).loft()))       # 指窝
    return j


# ---------------------------------------------------------------- D 侧键按钮（独立件 ×2）
def make_button(bx):
    """RESET / POWER 按钮（独立件，打印 2 个，通用不镜像）。

    结构：φ4.00 杆穿 φ4.40 孔 + 外面 φ5.00×0.70 帽。
      · 帽比孔大 → 掉不进壳里；
      · 侧键弹片把杆顶住 → 也不会掉出来；
      · 按下时杆内端（36.14，离弹片 0.09）压侧键，行程 = 0.09 空程 + 0.20 开关行程。
    装法：从外面插进孔，杆先入，帽落在墙面上即可，不需要胶也不需要卡扣。
    """
    b = cyl_y(bx, BTN_ZC, BTN_ROD_R, BTN_END, OY1)                      # 杆 φ4.00
    b = b.union(cyl_y(bx, BTN_ZC, BTN_CAP_R, OY1, OY1 + BTN_CAP_H))     # 帽 φ5.00×0.70
    b = b.cut(cyl_y(bx, BTN_ZC, 1.20, BTN_END - 0.01, BTN_END + 0.20))  # 内端 φ2.40 定心窝
    b = b.cut((cq.Workplane("XY").workplane(offset=OY1 + BTN_CAP_H)
               .center(bx, BTN_ZC).circle(BTN_CAP_R)
               .workplane(offset=-0.30).circle(1.70).loft()))           # 帽面浅凹（指感）
    return b


MIRROR_OUT = True          # 版面坐标(y 下) → 实物坐标(y 上)；见文件头说明


def _out(s):
    """把版面坐标的实体反射成实物坐标：y → BH − y（X/Z 不变）。
    反射是等距变换，托盘/盖板/摇杆的相对配合完全不变。"""
    if not MIRROR_OUT:
        return s
    return cq.Workplane("XY").add(s.val().mirror("XZ").translate(cq.Vector(0, BH, 0)))


def main():
    tray, lid, joy = make_tray(), make_lid(), make_joy()
    btns = [make_button(bx) for bx in BTN_CX]
    tray, lid, joy = _out(tray), _out(lid), _out(joy)
    btns = [_out(b) for b in btns]
    for name, s0 in (("tray", tray), ("lid", lid), ("joystick", joy), ("button", btns[0])):
        bb = s0.val().BoundingBox()
        print("%-9s %.2f x %.2f x %.2f mm  vol %.0f mm3"
              % (name, bb.xlen, bb.ylen, bb.zlen, s0.val().Volume()))
        cq.exporters.export(s0, os.path.join(OUT, "stm32f429_%s.step" % name))
        cq.exporters.export(s0, os.path.join(OUT, "stm32f429_%s.stl" % name),
                            tolerance=0.02, angularTolerance=0.2)
    assy = cq.Assembly()
    assy.add(tray, name="tray", color=cq.Color(0.25, 0.45, 0.75))
    assy.add(lid, name="lid", color=cq.Color(0.30, 0.55, 0.85))
    assy.add(joy, name="joystick", color=cq.Color(0.95, 0.65, 0.25))
    assy.add(btns[0], name="button_R", color=cq.Color(0.90, 0.30, 0.30))
    assy.add(btns[1], name="button_L", color=cq.Color(0.90, 0.30, 0.30))
    assy.save(os.path.join(OUT, "stm32f429_assy.step"))
    cq.exporters.export(tray.union(lid).union(joy).union(btns[0]).union(btns[1]),
                        os.path.join(OUT, "_preview_assy.step"))
    print("exported ->", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
