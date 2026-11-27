#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""五向摇杆驱动机构示意图（x–z 剖面，过开关中心 y=5.89）+ 俯视操作示意。
基准：z=0 为主板顶面；单位 mm；数值与 build_case.py 顶部参数一一对应。
输出 out/sch_joy_drive.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
matplotlib.rcParams["axes.unicode_minus"] = False

CX = 46.60
SW_BODY_H, SW_STEM_R, SW_STEM_TOP = 5.00, 1.50, 8.00
JOY_SOCK_R, JOY_SOCK_WALL = 1.68, 1.20
JOY_SOCK_RIM, JOY_SOCK_CEIL, JOY_SOCK_TOP = 6.30, 8.15, 9.35
SHAFT_R = 2.25
Z_PLATE_BOT, Z_PLATE_TOP = 12.50, 14.50
JOY_HOLE_R, JOY_RECESS_R, JOY_RECESS_Z1 = 4.80, 5.60, 13.40
JOY_BARB_R, JOY_CAP_R, ZT = 5.30, 5.50, 14.90

CASE, JOYK, SWC, PCBC = "#c8763a", "#e0912f", "#4a6fa5", "#2e8b57"

fig = plt.figure(figsize=(13.2, 9.8))
ax = fig.add_axes([0.055, 0.235, 0.62, 0.70])
ax.set_aspect("equal")


def rect(x0, x1, z0, z1, fc, ec="k", lw=1.0, z=2, alpha=1.0):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor=fc, edgecolor=ec,
                           lw=lw, zorder=z, alpha=alpha))


def sym(r, z0, z1, **kw):
    rect(CX - r, CX + r, z0, z1, **kw)


# 主板
sym(13.0, -1.60, 0.0, fc=PCBC, lw=0.8, z=1, alpha=0.9)
ax.text(CX - 12.5, -0.80, "主板（顶面 z=0，板厚 1.6）", fontsize=10, va="center",
        color="white", zorder=6)

# 五向键
sym(3.75, 0.0, SW_BODY_H, fc=SWC, ec="#152b47", lw=1.6, z=3, alpha=0.92)
ax.text(CX, 2.3, "K1-5203UA-01\n7.50×7.50×5.00", fontsize=9.5, ha="center", va="center",
        color="white", zorder=6)
sym(SW_STEM_R, SW_BODY_H, SW_STEM_TOP, fc=SWC, ec="#152b47", lw=1.6, z=4, alpha=0.92)

# 盖板
sym(13.0, Z_PLATE_BOT, Z_PLATE_TOP, fc=CASE, lw=1.1, z=1, alpha=0.72)
sym(JOY_HOLE_R, Z_PLATE_BOT, Z_PLATE_TOP, fc="white", lw=1.0, z=5)
sym(JOY_RECESS_R, Z_PLATE_BOT, Z_PLATE_BOT + 0.9, fc="white", lw=1.0, z=6)
ax.text(CX + 6.6, 13.45, "盖板 2 mm\nφ9.6 孔 + φ11.2×0.9 沉台", fontsize=9.5, ha="left",
        va="center", color="#7a3d12", zorder=7)

# 摇杆帽（套筒式）
sym(JOY_SOCK_R + JOY_SOCK_WALL, JOY_SOCK_RIM, JOY_SOCK_TOP, fc=JOYK, lw=1.2, z=8)
sym(JOY_SOCK_R, JOY_SOCK_RIM - 0.4, JOY_SOCK_CEIL, fc="white", lw=1.0, z=9)      # 内孔
sym(SW_STEM_R, JOY_SOCK_RIM, SW_STEM_TOP, fc=SWC, ec="#152b47", lw=1.4, z=10,
    alpha=0.92)                                                                  # 摇杆在孔里
sym(SHAFT_R, JOY_SOCK_TOP - 0.4, ZT, fc=JOYK, lw=1.2, z=7)
sym(4.40, JOY_RECESS_Z1, ZT, fc=JOYK, lw=1.2, z=8)
sym(JOY_BARB_R, 12.80, JOY_RECESS_Z1, fc=JOYK, lw=1.2, z=9)
sym(JOY_CAP_R, ZT, 17.70, fc=JOYK, lw=1.2, z=8)

# ---- 标注
ax.annotate("套筒内孔 φ3.36\n套 ø3.00 摇杆（0.18/侧）", xy=(CX + JOY_SOCK_R, 7.3),
            xytext=(CX + 7.4, 9.9), fontsize=9.5, ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", lw=1.1, color="#0b5"))
ax.annotate("摇杆顶面 8.00\n套内顶面 8.15\n→ 0.15 空程后压摇杆", xy=(CX + 0.2, JOY_SOCK_CEIL),
            xytext=(CX - 11.4, 10.9), fontsize=9.5, ha="right", va="center",
            arrowprops=dict(arrowstyle="-|>", lw=1.1, color="#b03030"))
ax.annotate("", xy=(CX - 2.78, SW_BODY_H), xytext=(CX - 2.78, JOY_SOCK_RIM),
            arrowprops=dict(arrowstyle="<|-|>", lw=1.0, color="#b03030"))
ax.text(CX - 2.98, (SW_BODY_H + JOY_SOCK_RIM) / 2, "1.30 净空\n倾斜时不碰本体",
        fontsize=8.5, ha="right", va="center", color="#b03030")
ax.annotate("", xy=(CX + JOY_CAP_R + 0.30, Z_PLATE_TOP), xytext=(CX + JOY_CAP_R + 0.30, ZT),
            arrowprops=dict(arrowstyle="<|-|>", lw=1.0, color="#b03030"))
ax.text(CX + JOY_CAP_R + 0.55, ZT + 0.15, "0.40 按压行程", fontsize=8.5, ha="left",
        va="bottom", color="#b03030")
# 标尺
for z in range(0, 18):
    ax.plot([CX - 20.4, CX - 19.9 if z % 5 else CX - 19.4], [z, z], color="#999", lw=0.8, zorder=1)
ax.text(CX - 20.7, 8.5, "z (mm)", fontsize=9, rotation=90, ha="center", va="center", color="#666")

ax.set_xlim(CX - 21.5, CX + 13.0)
ax.set_ylim(-2.8, 19.2)
ax.set_xlabel("x (mm)", fontsize=10)
ax.set_ylabel("z (mm) —— 主板顶面为 0", fontsize=10)
ax.set_title("v3.2 五向摇杆 ↔ K1-5203UA-01：x–z 剖面（过开关中心 y=5.89）", fontsize=12)
ax.grid(alpha=0.25, lw=0.6)

# ---- 说明框（放左下空处）
fig.text(0.058, 0.205,
        "驱动方式（套筒式）\n"
        "① 倾斜 → 四向：帽绕盖板 φ9.6 孔摆，套筒壁横推 ø3.00 摇杆\n"
        "    图纸：杠杆 5°±2°，170±35 gf\n"
        "② 按下 → 中心：套内顶面 8.15 走 0.15 空程后压摇杆顶 8.00\n"
        "    图纸：行程 0.20±0.10 mm，力 250 / 350 / 450 gf\n"
        "③ 限位：帽底 14.90 落到盖板面 14.50 → 总行程 0.40 = 0.15 + 0.20 + 余量",
        fontsize=10.0, va="top", ha="left", linespacing=1.7,
        bbox=dict(boxstyle="round,pad=0.55", facecolor="#fffbe8", edgecolor="#d9b45b"))

# ---- 右上角：俯视操作示意
ax2 = fig.add_axes([0.705, 0.60, 0.275, 0.32])
ax2.set_aspect("equal")
ax2.add_patch(Circle((0, 0), JOY_CAP_R, facecolor=JOYK, edgecolor="k", lw=1.2, zorder=2))
ax2.add_patch(Circle((0, 0), 1.70, facecolor="#fff6e0", edgecolor="k", lw=1.0, zorder=3))
for dx, dy, lab in ((1, 0, ""), (-1, 0, ""), (0, 1, ""), (0, -1, "")):
    ax2.add_patch(FancyArrowPatch((dx * 0.9, dy * 0.9), (dx * 3.9, dy * 3.9),
                                  arrowstyle="-|>", mutation_scale=13, lw=1.6,
                                  color="#2f6f3f", zorder=4))
ax2.add_patch(Circle((0, 0), 0.55, facecolor="#b03030", edgecolor="k", lw=0.8, zorder=5))
ax2.annotate("中心按下", xy=(0.35, -0.35), xytext=(2.6, -5.0), fontsize=9,
             arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#b03030"))
ax2.annotate("四向倾斜", xy=(2.9, 0.9), xytext=(1.0, 6.2), fontsize=9,
             arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#2f6f3f"))
ax2.set_xlim(-6.4, 6.4)
ax2.set_ylim(-6.8, 7.4)
ax2.set_title("俯视：φ11 帽（5 向）", fontsize=10)
ax2.axis("off")

out = ROOT + "//out/sch_joy_drive.png"
fig.savefig(out, dpi=165)
print("wrote", out)
