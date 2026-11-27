#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

"""分析 EasyEDA 导出的 OBJ_PCB-主板.obj：
   1) 单位标定（用 2.54 mm 排针 pitch 反推）
   2) 连通分量 → 每个器件的 bbox / 高度
   3) 顶面高度图 + 底面高度图 → 外壳净空校核
"""
import sys
import numpy as np

OBJ = ROOT + "//pcb3d.obj"


def load_obj(path):
    V, F = [], []
    with open(path) as f:
        for line in f:
            if line.startswith('v '):
                _, a, b, c = line.split()
                V.append((float(a), float(b), float(c)))
            elif line.startswith('f '):
                p = line.split()[1:]
                idx = [int(t.split('/')[0]) - 1 for t in p]
                for k in range(1, len(idx) - 1):
                    F.append((idx[0], idx[k], idx[k + 1]))
    return np.array(V), np.array(F, dtype=np.int64)


def components(V, F):
    parent = np.arange(len(V))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for tri in F:
        union(tri[0], tri[1])
        union(tri[1], tri[2])
    roots = np.array([find(i) for i in range(len(V))])
    return roots


if __name__ == "__main__":
    V, F = load_obj(OBJ)
    print("verts %d  tris %d" % (len(V), len(F)))
    roots = components(V, F)
    uniq, inv, cnt = np.unique(roots, return_inverse=True, return_counts=True)
    print("components:", len(uniq))

    # ---- 板框（z=0 与 z=10 的那个大平面）
    X0, X1 = 4048.20, 4259.60
    Y0, Y1 = -3185.76, -3047.20
    ZT, ZB = 10.0, 0.0          # 顶面 / 底面（模型坐标）
    rows = []
    for i, r in enumerate(uniq):
        m = inv == i
        p = V[m]
        rows.append((p[:, 0].min(), p[:, 0].max(), p[:, 1].min(), p[:, 1].max(),
                     p[:, 2].min(), p[:, 2].max(), m.sum()))
    rows.sort(key=lambda t: -t[6])
    print("\n top 45 components by vertex count (OBJ units):")
    print("   n    x span          y span          z span")
    for r in rows[:45]:
        print("%5d  %8.2f..%8.2f %8.2f..%8.2f %8.2f..%8.2f  dx %6.2f dy %6.2f dz %6.2f"
              % (r[6], r[0], r[1], r[2], r[3], r[4], r[5],
                 r[1] - r[0], r[3] - r[2], r[5] - r[4]))
    np.save("/tmp/objparts.npy", np.array(
        [(r[0], r[2], r[4], r[1], r[3], r[5], r[6]) for r in rows]))
