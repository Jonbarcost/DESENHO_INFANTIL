"""Run inside Blender. Derive a complete episode from the preserved character scene."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def smooth(a, b, t):
    x = max(0, min(1, (t-a)/(b-a)))
    return x*x*(3-2*x)


def pulse(a, b, t, edge=.35):
    return smooth(a, a+edge, t) * (1-smooth(b-edge, b, t))


def material(name, color, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = .65
    if emission:
        bs.inputs['Emission Color'].default_value = (*color, 1)
        bs.inputs['Emission Strength'].default_value = emission
    return m


def empty(name, location=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = location
    o.parent = parent
    return o


def sphere(name, location, scale, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=location)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    o.parent = parent
    return o


def parent_keep(o, parent):
    world = o.matrix_world.copy()
    o.parent = parent
    o.matrix_world = world


def key(o, path, frame):
    o.keyframe_insert(data_path=path, frame=frame)


def shot_camera(name, location, target, lens):
    data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z', 'Y').to_euler()
    data.lens = lens
    data.clip_end = 200
    return cam


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--width', type=int, default=1920)
    parser.add_argument('--samples', type=int, default=8)
    parser.add_argument('--engine', default='BLENDER_WORKBENCH')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    root, out = Path(args.root), Path(args.output)
    timeline = json.loads((out/'timeline.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(root/'EPISODIO_01/CENAS/personagens.blend'))
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, timeline['frames']
    scene.render.fps = timeline['fps']
    scene.render.resolution_x, scene.render.resolution_y = args.width, args.width*9//16
    scene.render.resolution_percentage = 100
    scene.render.engine = args.engine
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.compression = 25
    scene.render.film_transparent = False
    scene.render.filepath = str(out/'frames')+'/'
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = False
    scene.cycles.max_bounces = 4
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.studio_light = 'paint.sl'
    shading.studiolight_rotate_z = .4
    shading.color_type = 'MATERIAL'
    # Clean toy-like shading avoids unsupported denoising and software shadow artifacts.
    shading.show_shadows = False
    shading.show_cavity = False
    shading.cavity_type = 'BOTH'
    shading.curvature_ridge_factor = 1.1
    shading.curvature_valley_factor = .7
    shading.cavity_ridge_factor = 1.0
    shading.cavity_valley_factor = .7
    shading.show_specular_highlight = True
    shading.show_object_outline = False
    shading.background_type = 'WORLD'
    scene.world.color = (.48, .73, .88)
    scene.display.render_aa = '8'
    # Animation is rebuilt only in this derivative scene.
    for o in list(bpy.data.objects):
        o.animation_data_clear()
        if o.type == 'MESH' and any(o.name.startswith(n+'_') for n in ('Capi','Teco','Maya')):
            for p in o.data.polygons:
                p.use_smooth = True
    for action in list(bpy.data.actions):
        if action.users == 0:
            bpy.data.actions.remove(action)
    dark = material('Novo_Boca', (.15, .035, .055))
    pink = material('Novo_Lingua', (1, .32, .43))
    green = material('Novo_Verde', (.22, .60, .12))
    petalmat = material('Novo_Petala', (1, .30, .58))
    gold = material('Novo_Dourado', (1, .72, .08), 1)
    watermat = material('Novo_Agua', (.17, .65, 1))
    blue = material('Novo_Regador', (.08, .51, .69))
    earth = material('Novo_Terra', (.29, .14, .055))
    rigs = {}
    for name, x, y in [('Capi', -2.2, -.5), ('Teco', 2.2, -.5), ('Maya', 0, 1.8)]:
        parts = [o for o in bpy.data.objects if o.name.startswith(name+'_')]
        control = empty(name+'_Controle', (x,y,0))
        head = empty(name+'_Expressao', (0,0,1.18), control)
        bpy.context.view_layer.update()
        arms, feet, eyes = [], [], []
        for o in parts:
            if '_braco' in o.name:
                side = -1 if o.location.x < x else 1
                pivot = empty(name+'_Ombro_'+str(side), (side*.5,0,1.03), control)
                bpy.context.view_layer.update()
                parent_keep(o,pivot)
                arms.append((pivot,side))
            elif any(z in o.name for z in ('_cabeca','_olho','_pupila','_nariz')):
                parent_keep(o,head)
                if '_olho' in o.name or '_pupila' in o.name:
                    eyes.append((o, o.scale.copy(), o.location.copy()))
            else:
                parent_keep(o,control)
                if '_pe' in o.name:
                    feet.append((o, o.location.copy()))
        mouth = sphere(name+'_BocaAnimada', (0,-.43,-.10), (.13,.04,.022),dark,head)
        tongue = sphere(name+'_Lingua', (0,-.465,-.125), (.07,.018,.012), pink,head)
        # Small eyebrows make listening/surprise legible without redesigning models.
        brows = [sphere(name+'_Sobrancelha'+str(side), (side*.22,-.435,.47),(.12,.026,.024),dark,head)
                 for side in (-1,1)]
        rigs[name] = dict(root=control,head=head,arms=arms,feet=feet,eyes=eyes,
                          mouth=mouth,tongue=tongue,brows=brows,origin=Vector((x,y,0)))
    seed = bpy.data.objects['Sementinha Magica']
    for p in seed.data.polygons:
        p.use_smooth = True
    seed.scale = (.16,.16,.25)
    sphere('Terra_Plantio',(0,-.75,-.035),(.58,.48,.065),earth)
    # One flower rooted at the patch; trunk grows from its bottom rather than through the ground.
    flower = empty('Flor_Crescimento',(0,-.75,0))
    stem = sphere('Flor_Caule',(0,0,.62),(.055,.055,.65),green,flower)
    leaves=[]
    for side in (-1,1):
        leaf=sphere('Flor_Folha'+str(side),(side*.22,0,.48+side*.12),(.30,.075,.12),green,flower)
        leaf.rotation_euler.y=side*-.35
        leaves.append(leaf)
    petals=[]
    for i in range(8):
        ang=i*math.tau/8
        pet=sphere('Flor_Petala'+str(i),(math.cos(ang)*.29,-.055,1.25+math.sin(ang)*.29),(.24,.08,.14),petalmat,flower)
        pet.rotation_euler.y=-ang
        petals.append((pet,pet.location.copy(),pet.scale.copy(),ang))
    center=sphere('Flor_Miolo',(0,-.12,1.25),(.19,.10,.19),gold,flower)
    can=empty('Regador_Controle')
    sphere('Regador_Corpo',(0,0,0),(.23,.18,.24),blue,can)
    spout=sphere('Regador_Bico',(-.28,0,.12),(.25,.07,.07),blue,can)
    spout.rotation_euler.y=.45
    bpy.ops.mesh.primitive_torus_add(major_radius=.18,minor_radius=.038,major_segments=16,minor_segments=6)
    handle=bpy.context.object
    handle.name='Regador_Alca';handle.parent=can;handle.location=(.19,0,.11);handle.rotation_euler.x=math.pi/2
    handle.data.materials.append(blue)
    drops=[sphere('Gota_'+str(i),(0,0,0),(.025,.025,.065),watermat) for i in range(10)]
    stars=[]
    colors=[gold,petalmat,watermat]
    for i in range(18):
        verts=[]
        for j in range(10):
            ang=math.pi/2+j*math.pi/5
            radius=1 if j%2==0 else .43
            verts.append((math.cos(ang)*radius,0,math.sin(ang)*radius))
        mesh=bpy.data.meshes.new('EstrelaMesh_'+str(i))
        mesh.from_pydata(verts,[],[list(range(10))]);mesh.update()
        star=bpy.data.objects.new('Magia_'+str(i),mesh)
        bpy.context.collection.objects.link(star)
        star.data.materials.append(colors[i%3])
        stars.append(star)
    e=timeline['events']; d=timeline['dialogue']
    # Camera changes at dialogue boundaries; all cameras keep the front side of the characters.
    shots=[
        (0,'Abertura',(5.2,-10.6,5.0),(0,.35,1),42),
        (d[1]['start'],'Capi_descobre',(-3.7,-6.5,2.7),(-1.5,-.25,1.05),48),
        (d[2]['start'],'Teco_imagina',(4.1,-6.9,2.8),(1.7,-.15,1.1),48),
        (d[3]['start'],'Maya_convida',(1.4,-5.5,2.7),(0,1.1,1.15),48),
        (d[4]['start'],'Capi_pergunta',(-3.7,-6.5,2.7),(-1.5,-.25,1.05),48),
        (d[5]['start'],'Maya_explica',(1.4,-5.5,2.7),(0,1.1,1.15),48),
        (d[6]['start'],'Vamos_cuidar',(4.8,-9,4),(0,.2,.9),45),
        (e['plant_start'],'Plantio',(2.2,-5.9,3.7),(-.5,-.35,.55),49),
        (e['plant_end'],'Agua_e_sol',(4.1,-8.5,4.4),(0,.2,.8),44),
        (e['magic_start'],'Luz_magica',(3.8,-8,3.7),(0,.2,1),44),
        (e['growth_start'],'Flor_cresce',(2.8,-6.8,2.9),(0,-.2,.95),48),
        (d[9]['start'],'Conseguimos',(-3.3,-6.7,2.8),(-.5,-.05,1.05),45),
        (d[10]['start'],'Maya_natureza',(-2.6,-5.6,3.4),(-.55,1.5,1.18),48),
        (d[11]['start'],'Amizade',(4.6,-10,4.6),(0,.3,1),43),
    ]
    shot_manifest=[]
    for i,(start,name,loc,target,lens) in enumerate(shots):
        cam=shot_camera(name,loc,target,lens)
        a=round(start*timeline['fps'])+1
        end=shots[i+1][0] if i+1<len(shots) else timeline['duration']
        b=max(a+1,round(end*timeline['fps']))
        marker=scene.timeline_markers.new(name,frame=a);marker.camera=cam
        # Gentle dolly, reset per shot; never interpolate through a cut.
        key(cam,'location',a)
        cam.location=Vector(target)+(Vector(loc)-Vector(target))*.965
        key(cam,'location',b)
        shot_manifest.append(dict(name=name,start=start,end=end,camera=cam.name))
    scene.camera=bpy.data.objects[shots[0][1]]
    # Bake at output cadence so saved .blend works without handlers or custom plugins.
    for f in range(1,timeline['frames']+1):
        t=(f-1)/timeline['fps']
        active=next((c for c in d if c['start']<=t<c['end']),None)
        goodbye=smooth(e['goodbye'],e['goodbye']+.5,t)
        for index,(name,r) in enumerate(rigs.items()):
            speak=active is not None and active['speaker']==name.upper()
            amp=0
            if speak:
                j=int((t-active['start'])*timeline['fps'])
                amp=active['envelope'][j] if j<len(active['envelope']) else 0
            root=r['root']; loc=r['origin'].copy()
            approach=smooth(e['plant_start']-.8,e['plant_start']+1,t)*(1-smooth(e['plant_end']+.2,e['plant_end']+1.5,t))
            if name=='Capi': loc.x+=1.18*approach
            if name=='Teco': loc.x-=.85*pulse(e['plant_end']-.4,e['plant_end']+4.4,t,.8)
            if name=='Maya': loc.x-=.55*smooth(e['plant_end'],e['plant_end']+2,t)
            celebrating=pulse(d[9]['start']-.2,d[10]['end'],t)
            step=abs(math.sin(t*7))* .10 * pulse(e['plant_start']-.8,e['plant_start']+1,t) if name=='Capi' else 0
            hop=max(0,math.sin(t*7+index))* .15 * celebrating
            loc.z=.016*math.sin(t*2.1+index)+step+hop
            root.location=loc
            root.rotation_euler=(.28*approach if name=='Capi' else 0,
                                 .035*math.sin(t*2+index), .025*math.sin(t*1.2+index))
            key(root,'location',f);key(root,'rotation_euler',f)
            head=r['head']
            head.rotation_euler=(.04*math.sin(t*3+index)+(.045*math.sin(t*9) if speak else 0),
                                 .055*math.sin(t*2+index),.07*math.sin(t*1.3+index))
            key(head,'rotation_euler',f)
            r['mouth'].scale=(.13*(1+.12*amp),.04,.016+.085*amp)
            r['tongue'].scale=(.07,.018,.009+.025*amp)
            key(r['mouth'],'scale',f);key(r['tongue'],'scale',f)
            phase=(t+index*.83)%3.9
            blink=1-.95*math.exp(-((phase-.12)/.075)**2)
            for eye,scale,pos in r['eyes']:
                eye.scale=(scale.x,scale.y,scale.z*blink)
                key(eye,'scale',f)
                if '_pupila' in eye.name:
                    eye.location=pos+Vector((.018*math.sin(t*.9+index),-.003,0))
                    key(eye,'location',f)
            for side,brow in zip((-1,1),r['brows']):
                brow.location.z=.47+.045*amp+.04*celebrating
                brow.rotation_euler.y=side*(.12+.12*math.sin(t*1.7))
                key(brow,'location',f);key(brow,'rotation_euler',f)
            for arm,side in r['arms']:
                gesture=(.7+.3*math.sin(t*8))*amp
                wave=goodbye*(1.8+.45*math.sin(t*10+index)) if side==1 else .15*goodbye
                planting=approach*1.0 if name=='Capi' and side==1 else 0
                watering=pulse(e['plant_end']+.2,e['plant_end']+3.7,t) if name=='Teco' and side==-1 else 0
                arm.rotation_euler=(-.25*amp-.8*planting-.8*watering,
                                    -side*(.12+gesture+wave+.6*celebrating),
                                    .08*math.sin(t*3+index))
                key(arm,'rotation_euler',f)
            for foot,pos in r['feet']:
                foot.location=pos+Vector((0,0,step*.5*math.sin(t*7+pos.x*3)))
                key(foot,'location',f)
        # Seed floats by Capi's inner hand before he carries it to the patch.
        planting=smooth(e['plant_start']+.6,e['plant_end']-.5,t)
        # Carry beside the inner hand while Capi approaches; avoid drifting across his face.
        carry_x=-1.55+1.18*approach
        seed.location=Vector((carry_x,-1.15,1.04+.06*math.sin(t*3))).lerp(Vector((0,-.75,-.12)),planting)
        seed.rotation_euler=(0,.25*math.sin(t*2),t*.6)
        seed.scale=(.16,.16,.25) if t<e['plant_end'] else (.001,.001,.001)
        key(seed,'location',f);key(seed,'rotation_euler',f);key(seed,'scale',f)
        growth=smooth(e['growth_start'],e['growth_end'],t)
        flower.scale=(max(.001,growth),)*3
        flower.rotation_euler=(.035*math.sin(t*2)*growth,.055*math.sin(t*2.4)*growth,0)
        key(flower,'scale',f);key(flower,'rotation_euler',f)
        for pet,loc,scale,ang in petals:
            opening=smooth(e['growth_start']+.8,e['growth_end']+.3,t)
            pet.location=Vector((loc.x*(.25+.75*opening),loc.y,1.25+(loc.z-1.25)*(.25+.75*opening)))
            pet.scale=scale*(.15+.85*opening)
            key(pet,'location',f);key(pet,'scale',f)
        water=pulse(e['plant_end']+.3,e['plant_end']+3.5,t)
        can.location=(.68,-.75,1.12)
        can.rotation_euler=(0,-.42*water,0)
        can.scale=(max(.001,water),)*3
        key(can,'location',f);key(can,'rotation_euler',f);key(can,'scale',f)
        for i,drop in enumerate(drops):
            phase=(t*1.7+i/10)%1
            drop.location=(.22*(1-phase),-.75+.035*math.sin(i),1.1*(1-phase))
            drop.scale=(.024*water,.024*water,.06*water)
            key(drop,'location',f);key(drop,'scale',f)
        magic=pulse(e['magic_start'],e['growth_end']+2,t)
        for i,star in enumerate(stars):
            ang=t*2+i*math.tau/len(stars)
            radius=.25+.65*((t*.5+i/len(stars))%1)
            star.location=(math.cos(ang)*radius,-.75+math.sin(ang)*radius,.25+((t*.7+i*.13)%1)*1.9)
            k=magic*(.5+.5*math.sin(t*9+i)**2)
            star.scale=(.085*k,.085*k,.085*k)
            star.rotation_euler.y=t*.8+i
            key(star,'location',f);key(star,'scale',f)
            key(star,'rotation_euler',f)
    for action in bpy.data.actions:
        for curve in action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation='LINEAR'
    (out/'shots.json').write_text(json.dumps(shot_manifest,ensure_ascii=False,indent=2))
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'episodio_01_final.blend'))
    print('PRODUCTION_BUILT',timeline['frames'],args.engine,args.width)


if __name__=='__main__':
    main()
