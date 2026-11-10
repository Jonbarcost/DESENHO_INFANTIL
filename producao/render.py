"""Blender subprocess: render complete PNGs atomically and resume only valid ones."""
import argparse
import json
import os
import struct
import sys
import time
import zlib
from pathlib import Path


def valid_png(path, width, height):
    try:
        with open(path,'rb') as f:
            if f.read(8)!=b'\x89PNG\r\n\x1a\n':return False
            dimensions=None
            while True:
                raw=f.read(8)
                if len(raw)!=8:return False
                size,kind=struct.unpack('>I4s',raw)
                if size>100_000_000:return False
                data=f.read(size);crc=f.read(4)
                if len(crc)!=4 or zlib.crc32(kind+data)&0xffffffff!=struct.unpack('>I',crc)[0]:return False
                if kind==b'IHDR':dimensions=struct.unpack('>II',data[:8])
                if kind==b'IEND':return dimensions==(width,height)
    except (OSError,struct.error):return False


def main():
    import bpy
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    p.add_argument('--start',type=int,default=1)
    p.add_argument('--end',type=int)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    out=Path(a.output);frames=out/'frames';frames.mkdir(exist_ok=True)
    s=bpy.context.scene
    end=a.end or s.frame_end
    if not 1<=a.start<=end<=s.frame_end:raise ValueError('Intervalo inválido')
    stats=[];begin=time.time()
    for f in range(a.start,end+1):
        dest=frames/f'{f:04}.png'
        if valid_png(dest,s.render.resolution_x,s.render.resolution_y):continue
        s.frame_set(f)
        tmp=frames/f'{f:04}.partial.png'
        s.render.filepath=str(tmp)
        start=time.time()
        bpy.ops.render.render(write_still=True)
        if not valid_png(tmp,s.render.resolution_x,s.render.resolution_y):
            raise RuntimeError(f'PNG inválido: {tmp}')
        os.replace(tmp,dest)
        stats.append(time.time()-start)
        if f%12==0 or f==end:
            (out/'render-progress.json').write_text(json.dumps(dict(
                last_frame=f,total=s.frame_end,elapsed=time.time()-begin,
                mean_seconds=sum(stats)/len(stats)),indent=2))
            print('RENDER_PROGRESS',f,s.frame_end,round(sum(stats)/len(stats),3),flush=True)


if __name__=='__main__':main()
