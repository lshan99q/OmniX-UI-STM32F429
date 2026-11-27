import os as _os
# 仓库内路径：hardware/enclosure/{out,pcb3d.obj,...}
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

import struct, numpy as np, os
for n in ("tray","lid","joystick","button"):
    p=ROOT + "//out/stm32f429_%s.stl"%n
    d=open(p,'rb').read()
    nf=struct.unpack('<I',d[80:84])[0]
    assert len(d)==84+nf*50, (n,len(d),nf)
    a=np.frombuffer(d[84:],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))
    V=a['v'].reshape(-1,3,3).astype(np.float64)
    # 体积（散度定理）
    vol=np.einsum('ij,ij->i',V[:,0],np.cross(V[:,1],V[:,2])).sum()/6.0
    mn,mx=V.reshape(-1,3).min(0),V.reshape(-1,3).max(0)
    # 边长配对 → 判断闭合
    q=np.round(V.reshape(-1,3),6)
    u,inv,cnt=np.unique(q,axis=0,return_inverse=True,return_counts=True)
    E=np.sort(np.stack([inv.reshape(-1,3)[:,[0,1]],inv.reshape(-1,3)[:,[1,2]],inv.reshape(-1,3)[:,[2,0]]],1).reshape(-1,2),axis=1)
    ue,ce=np.unique(E,axis=0,return_counts=True)
    print("%-9s 面 %5d  尺寸 %.2f x %.2f x %.2f  体积 %8.1f mm3  顶点 %d  非2度边 %d"
          %(n,nf,mx[0]-mn[0],mx[1]-mn[1],mx[2]-mn[2],vol,len(u),int((ce!=2).sum())))
