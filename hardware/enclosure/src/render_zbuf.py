#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""极简 z-buffer 光栅化渲染器：把 STEP 的三角网格渲染成干净的正交视图。
自写，只用 numpy，避免 matplotlib 3D 的排序伪影。
支持多零件着色（托盘 / 盖板 / 摇杆）。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
import cadquery as cq

OUT = ROOT + "//out/preview_{}.png"
RES = (1500, 1000)
PARTS = [
    ("tray", ROOT + "//out/stm32f429_tray.step", (0.20, 0.36, 0.60), None),
    ("lid", ROOT + "//out/stm32f429_lid.step", (0.32, 0.55, 0.84), None),
    ("joystick", ROOT + "//out/stm32f429_joystick.step", (0.95, 0.62, 0.20), None),
    # 按钮件只导出一个，渲染时复制一个到 +x 5.85（两键间距）
    ("button", ROOT + "//out/stm32f429_button.step", (0.88, 0.30, 0.30),
     (5.85, 0.0, 0.0)),
]


def box_solid(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0)
            .translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)).val())


def load(path, clip=None):
    shape = cq.importers.importStep(path).val()
    if clip is not None:
        shape = shape.intersect(box_solid(*clip))
    verts, tris = shape.tessellate(0.15)
    V = np.array([[v.x, v.y, v.z] for v in verts], dtype=float)
    F = np.array(tris, dtype=np.int64)
    return V, F


def load_all(clip=None):
    out = []
    for name, path, rgb, dup in PARTS:
        V, F = load(path, clip)
        if len(V) == 0:
            continue
        out.append((name, V, F, np.array(rgb)))
        if dup is not None:
            out.append((name + "_2", V + np.array(dup, dtype=float), F, np.array(rgb)))
    return out


def camera(az_deg, el_deg):
    a, e = np.radians(az_deg), np.radians(el_deg)
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    up_hint = np.array([0.0, 0.0, 1.0]) if abs(np.cos(e)) < 0.999 else np.array([0.0, 1.0, 0.0])
    right = np.cross(up_hint, d)
    right /= np.linalg.norm(right)
    up = np.cross(d, right)
    up /= np.linalg.norm(up)
    return right, up, d


def view_basis(name):
    """显式指定 (right, up, dv)：dv 指向相机，right × up = dv（右手系，画面不镜像）。
    实物坐标：X 右、Y 上、Z 上。"""
    return {
        # 俯视：x 向右、y 向上
        "top": (np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0])),
        # 仰视
        "bottom": (np.array([1.0, 0, 0]), np.array([0, -1.0, 0]), np.array([0, 0, -1.0])),
        # 左壁外视（从 x− 看）：y 向右、z 向上
        "side_left": (np.array([0, -1.0, 0]), np.array([0, 0, 1.0]), np.array([-1.0, 0, 0])),
        # 右壁外视（从 x+ 看）
        "side_right": (np.array([0, 1.0, 0]), np.array([0, 0, 1.0]), np.array([1.0, 0, 0])),
        # 前壁外视（从 y− 看，RESET/POWER 那一侧）
        "front": (np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), np.array([0, -1.0, 0])),
        # 后壁外视（从 y+ 看）
        "back": (np.array([-1.0, 0, 0]), np.array([0, 0, 1.0]), np.array([0, 1.0, 0])),
    }[name]


def render(parts, view, fname, title="", only=None, bg="white"):
    if isinstance(view, tuple) and len(view) == 2:
        right, up, dv = camera(*view)
    else:
        right, up, dv = view_basis(view)
    tris, cols = [], []
    for name, V, F, rgb in parts:
        if only and name not in only:
            continue
        T = V[F]
        P = T @ np.stack([right, up, dv], axis=1)   # P[...,k] = 顶点·basis_k
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
        light = np.array([-0.35, -0.60, 0.72])
        light /= np.linalg.norm(light)
        lam = np.abs(n @ light)
        c = np.clip(rgb[None, :] * (0.30 + 0.90 * lam[:, None]), 0, 1)
        tris.append(P)
        cols.append(c)
    P = np.concatenate(tris)
    col = np.concatenate(cols)

    x, y, d = P[:, :, 0], P[:, :, 1], -P[:, :, 2]
    x0, x1, y0, y1 = x.min(), x.max(), y.min(), y.max()
    W, H = RES
    pad = 40
    s = min((W - 2 * pad) / (x1 - x0), (H - 2 * pad) / (y1 - y0))
    px = (x - (x0 + x1) / 2) * s + W / 2
    py = H / 2 - (y - (y0 + y1) / 2) * s

    zbuf = np.full((H, W), np.inf)
    cbuf = np.ones((H, W, 3))
    order = np.argsort(-d.mean(axis=1))
    for i in order:
        X, Y, D = px[i], py[i], d[i]
        xmin, xmax = max(int(np.floor(X.min())), 0), min(int(np.ceil(X.max())), W - 1)
        ymin, ymax = max(int(np.floor(Y.min())), 0), min(int(np.ceil(Y.max())), H - 1)
        if xmax <= xmin or ymax <= ymin:
            continue
        gx, gy = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5,
                             np.arange(ymin, ymax + 1) + 0.5)
        (ax_, bx_, cx_), (ay_, by_, cy_) = (X[0], X[1], X[2]), (Y[0], Y[1], Y[2])
        den = (by_ - cy_) * (ax_ - cx_) + (cx_ - bx_) * (ay_ - cy_)
        if abs(den) < 1e-12:
            continue
        w0 = ((by_ - cy_) * (gx - cx_) + (cx_ - bx_) * (gy - cy_)) / den
        w1 = ((cy_ - ay_) * (gx - cx_) + (ax_ - cx_) * (gy - cy_)) / den
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
        if not inside.any():
            continue
        depth = w0 * D[0] + w1 * D[1] + w2 * D[2]
        sub = zbuf[ymin:ymax + 1, xmin:xmax + 1]
        upd = inside & (depth < sub)
        if not upd.any():
            continue
        sub[upd] = depth[upd]
        cbuf[ymin:ymax + 1, xmin:xmax + 1][upd] = col[i]

    img = np.clip(cbuf, 0, 1)
    edge = (np.abs(np.diff(img, axis=0, prepend=img[:1])).sum(2) +
            np.abs(np.diff(img, axis=1, prepend=img[:, :1])).sum(2)) > 0.28
    img[edge] *= 0.60

    fig = plt.figure(figsize=(W / 150, H / 150), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, interpolation="bilinear")
    ax.set_axis_off()
    if title:
        # 画布是满幅的，标题必须自己叠在留白上，set_title 会被裁掉
        fig.text(0.010, 0.984, title, fontsize=10, va="top", ha="left", color="#222222")
    fig.savefig(OUT.format(fname), facecolor=bg, dpi=150)
    plt.close(fig)
    print("wrote", OUT.format(fname))


if __name__ == "__main__":
    D = "STM32F429 mini 4G 开发板 · 上层外壳 v3：托盘 + 盖板 + 五向摇杆（封闭底）"
    parts = load_all()
    render(parts, (-125, 32), "iso_front",
           "前方 3/4 视图（从 y− / x− 上方看：RESET / POWER 可按压圆点 + 左侧三窗）— " + D)
    render(parts, (-58, 34), "iso_right",
           "右后 3/4 视图（可见摇杆、OLED 屏窗、3×LED 孔；右壁无开孔）")
    render(parts, (58, 34), "iso_right2",
           "右前 3/4 视图（从 y+ / x+ 上方看：右侧全封闭，看屏窗与摇杆）")
    render(parts, "top", "top",
           "俯视图（x 向右 / y 向上，与实物坐标一致）：OLED 屏窗 33.6×24.6 直角、3×φ1.5 LED 孔、φ9.6 摇杆座")
    render(parts, "bottom", "bottom", "仰视图：封闭底板，四周侧壁包住主板")
    # 侧视：只留那一面墙（否则透过窗口看到的是对面墙内表面，看不出开孔）
    render(load_all(clip=(-2.80, -0.30, -3.70, 38.00, -7.10, 12.60)), "side_left", "side_left",
           "左壁内视（只留左墙，从 x− 看，y 向右）：USB-A 6.5 高 / 烧录口 4.6 / TYPE-C 3.8 阶梯窗")
    render(load_all(clip=(54.00, 56.50, -3.70, 38.00, -7.10, 12.60)), "side_right", "side_right",
           "右壁内视（只留右墙，从 x+ 看）：整面封闭，无开孔")
    render(load_all(clip=(-2.80, 56.50, -4.20, -0.95, -7.10, 12.60)), "front", "front",
           "前壁外视（从 y− 看，x 向右）：RESET / POWER 两个独立按钮件（φ5 帽），墙里是侧键避让槽")
    render(load_all(clip=(-2.80, 56.50, 15.19, 38.00, -7.10, 12.60)), (-125, 26), "cutaway",
           "半剖视图（沿 y=15.2 切开）：1 mm 台面、下腔、背面 4G 位")
    render(load_all(clip=(40.50, 55.50, -4.50, 1.70, -5.60, 1.50)), "front", "btn_closeup",
           "前壁按钮特写：独立按钮件（φ4.0 杆 + φ5.0×0.7 帽）插在 φ4.4 通孔里，靠侧键弹片顶住定位")
    render(load_all(clip=(40.50, 55.50, -4.50, 1.70, -5.60, 1.50)), (-150, 28), "btn_iso",
           "前壁按钮 3/4 特写（从内侧看：φ4.4 通孔 + 侧键避让槽 + 杆端 φ2.4 定心窝）")
    render(load_all(clip=(40.50, 55.50, -4.50, 1.70, -1.96, -1.82)), "top", "btn_section",
           "前壁按钮水平剖面（z=−1.9 穿过按钮中心俯视）：φ4.4 孔 / φ4.0 杆 / 两侧侧键避让槽")
    render(load_all(clip=(41.50, 52.00, -0.90, 12.20, 13.06, 13.20)), "top", "joy_section",
           "摇杆座水平剖面（z=13.2 切开俯视）：φ9.6 孔 / φ11.2 沉台 / 三爪卡爪 / 杆 φ4.5")
    render(load_all(clip=(42.20, 51.00, 1.00, 10.10, 5.20, 15.20)), (-118, -26), "joy_socket",
           "摇杆帽 3/4 仰视：下端 φ3.36 内孔套住开关 ø3.00 摇杆（套口 6.30 / 套内顶 8.15），往上接杆 φ4.5 与颈")
    render(load_all(clip=(44.00, 49.20, 1.00, 10.10, 5.20, 15.20)), (-118, -22), "joy_drive",
           "驱动机构剖面（x 沿 44.0..49.2 切开）：套筒内孔 ↔ 开关摇杆 ø3.00/顶面 8.00 ↔ 盖板 φ9.6 孔与 φ11.2 沉台")
    render(parts, "top", "top_lid", "盖板单独俯视：3×φ1.5 LED 孔（内面 φ4.0 喇叭口）、OLED 直角窗、φ9.6 摇杆座", only={"lid"})
    render(parts, "bottom", "bottom_tray", "托盘单独仰视（封闭底面）", only={"tray"})
    render(parts, (-100, 18), "joy_closeup", "五向摇杆帽：帽 / 颈 / 卡爪 / 套筒（侧上 3/4）",
           only={"lid", "joystick"})
