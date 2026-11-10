"""Blender-only proof of frame equivalence for the fixed Workbench production.

Usage: blender -b --python comparar_cenas.py -- old.blend new.blend report.json
This reports equivalence only. It does not copy/delete renders or bypass manifests.
"""
import hashlib
import json
import sys
from pathlib import Path

import bpy


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    s=bpy.context.scene
    if s.render.engine!='BLENDER_WORKBENCH':
        raise ValueError('Equivalência implementada somente para esta produção Workbench')
    sh=s.display.shading
    static=dict(render=[s.render.engine,s.render.resolution_x,s.render.resolution_y,
                        s.render.resolution_percentage,s.display.render_aa,s.render.film_transparent],
                shading=[sh.light,sh.studio_light,sh.color_type,sh.show_shadows,sh.show_cavity,
                         sh.studiolight_rotate_z,sh.show_specular_highlight,sh.show_object_outline,
                         sh.background_type,list(s.world.color)],
                color=[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,
                       s.view_settings.gamma],objects={})
    objects=sorted(bpy.data.objects,key=lambda o:o.name)
    for o in objects:
        props=dict(type=o.type,render=o.hide_render)
        if o.type=='MESH':
            # BMesh allocation may reorder vertex/face indices between Blender runs.
            # Compare oriented geometric faces, retaining winding, smoothness and material.
            faces=[]
            for face in o.data.polygons:
                coords=[tuple(o.data.vertices[j].co) for j in face.vertices]
                canonical=min(tuple(coords[j:]+coords[:j]) for j in range(len(coords)))
                faces.append((canonical,face.use_smooth,face.material_index))
            props.update(vertices=sorted(tuple(v.co) for v in o.data.vertices),
                         polygons=sorted(faces),
                         materials=[list(m.diffuse_color) for m in o.data.materials])
        static['objects'][o.name]=props
    hashes=[]
    for frame in sorted(set(range(1,841))|{int(p.stem) for p in Path('EPISODIO_04/ARTEFATOS/frames').glob('*.png')}):
        s.frame_set(frame)
        cam=s.camera.data
        state=dict(camera=s.camera.name,projection=[cam.type,cam.lens,cam.sensor_width,cam.sensor_height,
                                                  cam.sensor_fit,cam.shift_x,cam.shift_y,cam.ortho_scale,
                                                  cam.clip_start,cam.clip_end],
                   camera_matrix=[v for row in s.camera.matrix_world for v in row],
                   objects={o.name:list(v for row in o.matrix_world for v in row)
                                               for o in objects if o.type!='CAMERA'})
        hashes.append((frame,digest(state)))
    return dict(static=digest(static),frames=hashes,scene_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def main():
    old,new,report=map(Path,sys.argv[sys.argv.index('--')+1:])
    a,b=inspect(old),inspect(new)
    if a['static']!=b['static'] or len(a['frames'])!=len(b['frames']):
        raise RuntimeError('Geometria/material/configuração diferem; não reutilizar quadros')
    changed=[x[0] for x,y in zip(a['frames'],b['frames']) if x!=y]
    result=dict(old=a['scene_sha256'],new=b['scene_sha256'],static=a['static'],
                total=len(a['frames']),changed_frames=changed,
                unchanged_frames=[x[0] for x in a['frames'] if x[0] not in changed],
                scope='Workbench: meshes/materials/settings and exact world matrices/camera per frame')
    report.write_text(json.dumps(result,indent=2))
    print('CHANGED_FRAMES',changed)


if __name__=='__main__':main()
