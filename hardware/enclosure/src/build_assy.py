#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""装配体导出：托盘 + 主板（真实 pcb3d.obj）+ 盖板 + 摇杆帽 + 背面 4G 模块包络。

输出
  out/stm32f429_assy_full.3mf     全部零件（mm，多对象，带颜色）—— 查看/切片都行
  out/stm32f429_assy_full.step    CAD 装配（外壳三件 + 主板简化板 + 4G 包络）
  out/preview_assy_full_{iso,cut,lid_lift}.png

板厚修正：OBJ 把板画成 2.54 mm 厚，真实 1.0 mm。按分段线性把 z 压回真实位置：
  z ≥ 0            → z            （顶面器件不动）
  −2.54 ≤ z < 0    → z·(1/2.54)   （板体 2.54 → 1.0）
  z < −2.54        → z + 1.54     （底面器件整体上移，仍贴着板底）
这样板顶面仍是 0、板底到 −1.0、底面器件与板的相对关系不变。
"""
import os
import zipfile
import numpy as np
import cadquery as cq

import build_case as B

OUT = ROOT + "//out"
OBJ = ROOT + "//pcb3d.obj"
S, X0, YMIN, ZT = 0.254, 4048.20, -3185.76, 10.0
BT_MODEL = 2.54

# 配色
COL = {
    "tray":     (0.784, 0.463, 0.227),
    "lid":      (0.678, 0.376, 0.176),
    "joystick": (0.878, 0.569, 0.184),
    "button":   (0.850, 0.300, 0.300),
    "pcb":      (0.125, 0.420, 0.227),
    "mod4g":    (0.690, 0.227, 0.180),
}


# ------------------------------------------------------------------ 几何
def board_z(z):
    """OBJ 的 z（板顶面=0、板厚 2.54）→ 真实板厚 BT 的 z"""
    if z >= 0.0:
        return z
    if z <= -BT_MODEL:
        return z + (BT_MODEL - B.BT)
    return z * (B.BT / BT_MODEL)


def load_obj(path):
    V, F = [], []
    with open(path) as f:
        for line in f:
            if line.startswith('v '):
                _, a, b, c = line.split()
                V.append((float(a), float(b), float(c)))
            elif line.startswith('f '):
                p = [int(t.split('/')[0]) - 1 for t in line.split()[1:]]
                for k in range(1, len(p) - 1):
                    F.append((p[0], p[k], p[k + 1]))
    return np.array(V), np.array(F, dtype=np.int64)


def pcb_mesh():
    V, F = load_obj(OBJ)
    x = (V[:, 0] - X0) * S
    y = (V[:, 1] - YMIN) * S
    z = np.array([board_z(v) for v in (V[:, 2] - ZT) * S])
    return np.stack([x, y, z], 1), F


def case_parts():
    """四件（版面坐标建模 → 实物坐标）；按钮件通用，装两处"""
    return dict(tray=B._out(B.make_tray()),
                lid=B._out(B.make_lid()),
                joystick=B._out(B.make_joy()),
                button=[B._out(B.make_button(bx)) for bx in B.BTN_CX])


# 板底最空的 26×26 位置（用底部高度图搜索：底面器件占比 0.4%）
MOD4G_C = (35.0, 19.0)


def mod4g_solid(cx=None, cy=None):
    """4G 模块包络（板底 −1.0 起向下 2.4），默认放在板底最空的位置"""
    cx = MOD4G_C[0] if cx is None else cx
    cy = MOD4G_C[1] if cy is None else cy
    w, d, h = B.MOD4G["w"], B.MOD4G["d"], B.MOD4G["h"]
    return (cq.Workplane("XY").box(w, d, h)
            .translate((cx, cy, B.Z_BOARD_BOT - h / 2)))


def pcb_plate():
    """简化主板（板厚 BT，直角矩形）"""
    return (cq.Workplane("XY").box(B.BW, B.BH, B.BT)
            .translate((B.BW / 2, B.BH / 2, B.Z_BOARD_BOT + B.BT / 2)))


def tess(shape, tol=0.06, ang=0.35):
    vs, fs = shape.val().tessellate(tol, ang)
    V = np.array([[v.x, v.y, v.z] for v in vs], dtype=np.float64)
    F = np.array(fs, dtype=np.int64)
    return V, F


# ------------------------------------------------------------------ 3MF
HEAD = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="zh-CN" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n')
CT = ('<?xml version="1.0" encoding="UTF-8"?>\n'
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
      '</Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>')


def write_3mf(path, items):
    """items: [(name, V, F, rgb)]"""
    parts = [HEAD, '<metadata name="Title">STM32F429 mini 4G 上层外壳装配体</metadata>\n',
             '<resources>\n<basematerials id="1">\n']
    for name, _, _, rgb in items:
        parts.append('<base name="%s" displaycolor="#%02X%02X%02XFF"/>\n'
                     % (name, int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)))
    parts.append('</basematerials>\n')
    for i, (name, V, F, _) in enumerate(items):
        parts.append('<object id="%d" type="model" pid="1" pindex="%d" name="%s">\n<mesh>\n<vertices>\n'
                     % (i + 2, i, name))
        for x, y, z in V:
            parts.append('<vertex x="%.4f" y="%.4f" z="%.4f"/>\n' % (x, y, z))
        parts.append('</vertices>\n<triangles>\n')
        for a, b, c in F:
            parts.append('<triangle v1="%d" v2="%d" v3="%d"/>\n' % (a, b, c))
        parts.append('</triangles>\n</mesh>\n</object>\n')
    parts.append('</resources>\n<build>\n')
    for i in range(len(items)):
        parts.append('<item objectid="%d"/>\n' % (i + 2))
    parts.append('</build>\n</model>\n')
    data = "".join(parts).encode("utf-8")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("3D/3dmodel.model", data)
    return len(data)


# ------------------------------------------------------------------ STEP
def write_step(path, solids):
    asm = cq.Assembly()
    for name, shp, col in solids:
        asm.add(shp, name=name, color=cq.Color(*col))
    asm.save(path, exportType="STEP")
    return asm


# ------------------------------------------------------------------ main
def main():
    parts = case_parts()
    V, F = pcb_mesh()
    print("主板网格 %d 顶点 / %d 三角面（z 已按 %.1f mm 板厚重映射）" % (len(V), len(F), B.BT))

    m4 = mod4g_solid()
    V4, F4 = tess(m4, 0.2, 0.6)

    items = [("tray_托盘", *tess(parts["tray"]), COL["tray"]),
             ("pcb_主板", V, F, COL["pcb"]),
             ("mod4g_4G模块包络", V4, F4, COL["mod4g"]),
             ("lid_盖板", *tess(parts["lid"]), COL["lid"]),
             ("joystick_摇杆帽", *tess(parts["joystick"]), COL["joystick"]),
             ("button_R_RESET", *tess(parts["button"][0]), COL["button"]),
             ("button_L_POWER", *tess(parts["button"][1]), COL["button"])]

    p3mf = os.path.join(OUT, "stm32f429_assy_full.3mf")
    size = write_3mf(p3mf, items)
    print("wrote %s (%.1f MB 未压缩, %.1f MB 压缩后)"
          % (p3mf, size / 1e6, os.path.getsize(p3mf) / 1e6))

    pstep = os.path.join(OUT, "stm32f429_assy_full.step")
    write_step(pstep, [("tray", parts["tray"], COL["tray"]),
                       ("pcb_plate_%0.1fmm" % B.BT, pcb_plate(), COL["pcb"]),
                       ("mod4g_26x26x2p4", m4, COL["mod4g"]),
                       ("lid", parts["lid"], COL["lid"]),
                       ("joystick", parts["joystick"], COL["joystick"]),
                       ("button_R", parts["button"][0], COL["button"]),
                       ("button_L", parts["button"][1], COL["button"])])
    print("wrote %s (%.1f MB)" % (pstep, os.path.getsize(pstep) / 1e6))

    np.savez("/tmp/assy_parts.npz", V=V, F=F,
             m4V=V4, m4F=F4)
    return items


if __name__ == "__main__":
    main()
