#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""装入演示图：把真实 PCB（pcb3d.obj，含全部有 3D 模型的器件）放进外壳里渲染。
坐标：实物坐标（X 右 / Y 上 / Z 上），与 pcb3d.obj 同手系。
外壳沿 y=15.2 半剖，看得到板、插接件穿窗、台面承板、底面器件与侧键顶针。"""
import numpy as np
import render_zbuf as R

OBJ = ROOT + "//pcb3d.obj"
S = 0.254
X0, YMIN, ZT = 4048.20, -3185.76, 10.0


def load_pcb():
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
    # 实物坐标：y 取 OBJ 的 +Y（obJ 最小 y = -3185.76 对应板的下边缘 y=0）
    P = np.stack([(V[:, 0] - X0) * S, (V[:, 1] + 3185.76) * S, (V[:, 2] - ZT) * S], 1)
    return P, np.array(F, dtype=np.int64)


def cut_pcb(pcb, y_plane, side):
    """把 PCB 顶点夹到剖面上，得到干净的半剖（spike-free）。"""
    V, F = pcb
    V = V.copy()
    if side == "front":
        V[:, 1] = np.minimum(V[:, 1], y_plane)
    else:
        V[:, 1] = np.maximum(V[:, 1], y_plane)
    cy = V[F][:, :, 1].mean(1)
    keep = F[(cy >= y_plane - 1e-6)] if side == "back" else F[(cy <= y_plane + 1e-6)]
    return ("pcb", V, keep, np.array([0.13, 0.42, 0.28]))


def main():
    pcb = load_pcb()
    YC = 15.19                                   # 剖切面（实物坐标，= 版面 y 20.00）
    front = cut_pcb(pcb, YC, "front")
    back = cut_pcb(pcb, YC, "back")
    case_f = R.load_all(clip=(-2.80, 56.50, YC, 38.00, -7.10, 18.00))
    case_b = R.load_all(clip=(-2.80, 56.50, -3.70, YC, -7.10, 18.00))
    R.render([front] + case_f, (128, 26), "asm_cut_iso",
             "装入演示（沿 y=%.1f 半剖，含真实 pcb3d.obj）：插接件穿出左侧三窗，板落在 1 mm 台面上" % YC)
    R.render([front] + case_f, (163, 12), "asm_cut_left",
             "装入演示 · 左前方（半剖）：USB-A / 烧录口 / TYPE-C 与三个阶梯窗对位")
    # 侧键局部竖剖：沿 x=45.03 切开，看膜 / 凸台 / 侧键 / 板 的层叠关系
    xc = 45.03
    V, F = pcb
    cx = V[F][:, :, 0].mean(1)
    keep = F[(cx > xc - 1.6) & (cx < xc + 1.6)]
    pcb_btn = ("pcb", V, keep, np.array([0.13, 0.42, 0.28]))
    case_btn = R.load_all(clip=(xc - 1.6, xc + 1.6, -4.60, 3.20, -7.10, 1.60))
    R.render([pcb_btn] + case_btn, "side_left", "asm_btn_section",
             "侧键竖剖（x=%.2f，从 x− 看，右 = −y）：0.6 膜 → φ3.5 凸台（留 0.10）→ 底面侧键 → 主板" % xc)
    R.render([pcb_btn] + case_btn, (-152, 24), "asm_btn_iso",
             "侧键竖剖 3/4：膜内侧凸台正对侧键（底面），间隙 0.10")


if __name__ == "__main__":
    main()
