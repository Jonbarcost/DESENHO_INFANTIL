"""Blender scene builder. Reuses original geometry and Episode 1 rig primitives."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from producao.animacao import empty, key, material, parent_keep, pulse, shot_camera, smooth, sphere


def character(name,x,y,dark,pink):
    parts=[o for o in bpy.data.objects if o.name.startswith(name+'_')]
    root=empty(name+'_EP2_Root',(x,y,0))
    head=empty(name+'_EP2_Head',(0,0,1.18),root)
    bpy.context.view_layer.update()
    arms=[];feet=[];eyes=[]
    for o in parts:
        if '_braco' in o.name or '_pe' in o.name:
            arm='_braco' in o.name;side=-1 if o.location.x<x else 1
            pivot=empty(name+('_EP2_Arm' if arm else '_EP2_Foot')+str(side),
                        (side*(.5 if arm else .28),-.0 if arm else -.12,1.03 if arm else .28),root)
            bpy.context.view_layer.update();parent_keep(o,pivot)
            (arms if arm else feet).append((pivot,side))
        elif any(k in o.name for k in ('_cabeca','_olho','_pupila','_nariz')):
            parent_keep(o,head)
            if '_olho' in o.name or '_pupila' in o.name:eyes.append((o,o.scale.copy(),o.location.copy()))
        else:parent_keep(o,root)
    mouth=sphere(name+'_EP2_Mouth',(0,-.435,-.10),(.13,.035,.017),dark,head)
    tongue=sphere(name+'_EP2_Tongue',(0,-.463,-.125),(.065,.015,.01),pink,head)
    brows=[sphere(name+'_EP2_Brow'+str(i),(i*.22,-.435,.47),(.12,.025,.024),dark,head) for i in (-1,1)]
    return dict(root=root,head=head,arms=arms,feet=feet,eyes=eyes,mouth=mouth,tongue=tongue,brows=brows,
                origin=Vector((x,y,0)),phase=0)


def configure(s,width,engine):
    s.render.engine=engine;s.render.resolution_x=width;s.render.resolution_y=width*9//16
    s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=20
    s.render.threads_mode='FIXED';s.render.threads=4
    s.view_settings.view_transform='Standard';s.view_settings.look='None'
    s.cycles.use_denoising=False;s.cycles.samples=8;s.cycles.max_bounces=4
    sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='MATERIAL'
    sh.show_shadows=False;sh.show_cavity=False;sh.show_specular_highlight=True
    sh.background_type='WORLD';s.world.color=(.50,.76,.91);s.display.render_aa='8'
    s.eevee.taa_render_samples=8


def butterfly_position(t,scenes):
    travel=smooth(scenes['investigate']['start'],scenes['investigate']['end'],t)
    # At the garden, stay at flower height so wings do not cover Maya's face.
    center=Vector((-.8,-.4,1.95)).lerp(Vector((2.4,1.1,.83)),travel)
    a=t*.45
    return center+Vector(((1.2-.52*travel)*math.sin(a),(.8-.45*travel)*math.cos(a*.7),
                          (.28-.18*travel)*math.sin(a*1.3)))


def build(timeline,out,width=1920,engine='BLENDER_WORKBENCH'):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'EPISODIO_01/CENAS/personagens.blend'))
    s=bpy.context.scene;configure(s,width,engine)
    s.frame_start=1;s.frame_end=timeline['frames'];s.render.fps=timeline['fps']
    for o in list(bpy.data.objects):
        o.animation_data_clear()
        if any(o.name.startswith(n+'_') for n in ('Capi','Teco','Maya')) and o.type=='MESH':
            for p in o.data.polygons:p.use_smooth=True
    # The first episode's seed is not part of this story; original file stays untouched.
    seed=bpy.data.objects.get('Sementinha Magica')
    if seed:seed.hide_render=True
    ground=bpy.data.objects.get('Clareira')
    if ground:ground.scale.x*=1.5;ground.scale.y*=1.5
    dark=material('EP2_Boca',(.13,.035,.05));pink=material('EP2_Lingua',(1,.35,.47))
    green=material('EP2_Folha',(.20,.64,.23));earth=material('EP2_Terra',(.38,.22,.10))
    blue=material('EP2_Azul',(.025,.36,1),.15);cyan=material('EP2_Ciano',(.25,.85,1),.1)
    gold=material('EP2_Polen',(1,.77,.16));water=material('EP2_Agua',(.19,.67,.98))
    shadow=material('EP2_Contato',(.17,.40,.16))
    rigs={name:character(name,x,y,dark,pink) for name,x,y in [('Capi',-2.2,-.5),('Teco',2.2,-.5),('Maya',0,1.8)]}
    shadows={n:sphere(n+'_EP2_Shadow',(0,0,-.043),(.54,.38,.006),shadow) for n in rigs}
    # Instance the original trees at the outer edge; never rebuild their source meshes.
    trunks=[o for o in bpy.data.objects if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='Tronco']
    crowns=[o for o in bpy.data.objects if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='Folhas']
    if trunks and crowns:
        for i,(x,y) in enumerate([(-7,4),(-5.5,7),(-1,7),(2,7.5),(7,5),(8,1)]):
            for prototype,z in [(trunks[0],1.5),(crowns[0],3.5)]:
                o=bpy.data.objects.new(f'EP2_Arvore_{i}_{z}',prototype.data);bpy.context.collection.objects.link(o);o.location=(x,y,z)
    sphere('EP2_Jardim',(2.4,1.2,-.04),(1.4,1.0,.05),earth)
    flowers=[]
    colors=[material('EP2_PetalaRosa',(1,.39,.63)),material('EP2_PetalaLilas',(.64,.39,.96)),
            material('EP2_PetalaCreme',(1,.88,.46))]
    for i,(x,y) in enumerate([(1.7,.8),(3.0,.6),(2.3,1.7),(3.1,1.7),(1.5,1.5),(2.5,.5)]):
        group=empty('EP2_Flor_'+str(i),(x,y,0))
        h=.62+(i%3)*.09
        sphere('EP2_Caule_'+str(i),(0,0,h/2),(.026,.026,h/2),green,group)
        for side in (-1,1):
            leaf=sphere(f'EP2_Folha_{i}_{side}',(side*.12,0,.22),(.18,.045,.07),green,group)
            leaf.rotation_euler.y=side*-.3
        petals=[]
        for j in range(6):
            a=j*math.tau/6
            p=sphere(f'EP2_Petala_{i}_{j}',(math.cos(a)*.16,-.02,h+math.sin(a)*.16),(.14,.04,.09),colors[i%3],group)
            p.rotation_euler.y=-a;petals.append((p,p.scale.copy()))
        sphere('EP2_Miolo_'+str(i),(0,-.06,h),(.10,.07,.10),gold,group)
        flowers.append((group,petals))
    butterfly=empty('EP2_Borboleta')
    sphere('EP2_BorboletaCorpo',(0,0,0),(.055,.055,.27),dark,butterfly)
    sphere('EP2_BorboletaCabeca',(0,-.01,.26),(.08,.07,.08),dark,butterfly)
    wings=[]
    for side in (-1,1):
        wing=empty('EP2_Asa_'+str(side),(0,0,0),butterfly);wings.append((wing,side))
        sphere('EP2_AsaSuperior_'+str(side),(side*.33,0,.16),(.38,.035,.29),blue,wing)
        sphere('EP2_AsaInferior_'+str(side),(side*.27,0,-.19),(.29,.035,.22),cyan,wing)
        for j in range(3):sphere(f'EP2_Pinta_{side}_{j}',(side*(.26+j*.1),-.04,.13+j*.045),(.045,.014,.07),gold,wing)
        antenna=sphere('EP2_Antena_'+str(side),(side*.08,0,.37),(.014,.014,.11),dark,butterfly)
        antenna.rotation_euler.y=side*.35
        sphere('EP2_AntenaPonta_'+str(side),(side*.12,0,.47),(.025,.025,.025),gold,butterfly)
    pollen=[sphere('EP2_Polen_'+str(i),(0,0,0),(.024,.024,.024),gold) for i in range(6)]
    can=empty('EP2_Regador')
    sphere('EP2_RegadorCorpo',(0,0,0),(.20,.16,.22),cyan,can)
    spout=sphere('EP2_RegadorBico',(-.28,0,.1),(.24,.05,.05),cyan,can);spout.rotation_euler.y=.4
    drops=[sphere('EP2_Gota_'+str(i),(0,0,0),(.022,.022,.06),water) for i in range(8)]
    scenes={sc['mode']:sc for sc in timeline['scenes']}
    init={n:r['origin'].copy() for n,r in rigs.items()}
    garden={'Capi':Vector((.4,.6,0)),'Teco':Vector((4.3,.7,0)),'Maya':Vector((2.1,3.1,0))}

    def position(name,t):
        loc=init[name].copy();ch=scenes['chase'];inv=scenes['investigate']
        if ch['start']<=t<ch['end']:
            a=math.tau*2*smooth(ch['start']+1,ch['end']-3,t)
            if name=='Teco':loc+=Vector((1.1*(math.cos(a)-1),.65*math.sin(a),0))
            elif name=='Capi':loc+=Vector((.22*math.sin(a),.22*math.sin(a*.5),0))
        if t>=inv['start']:
            loc=init[name].lerp(garden[name],smooth(inv['start']+1,inv['end']-4,t))
        return loc

    # Every line receives a shot; wide action shots replace narrator-only close-ups.
    shotlist=[]
    for sc in timeline['scenes']:
        entries=[(sc['start'],'NARRADORA')]+[(c['start'],c['speaker']) for c in timeline['dialogue'] if c['scene']==sc['id']]
        for idx,(time,speaker) in enumerate(entries):
            center=Vector((2.4,1.2,.9)) if sc['mode'] in ('garden','care','finale') else Vector((0,.2,1))
            action=sc['mode'] in ('chase','care')
            if speaker=='NARRADORA' or action:
                loc=center+Vector((5.5,-11.5,4.6));target=center;lens=43
            else:
                locbase=position(speaker.title(),time)
                # Left/front angle keeps garden flowers to the side of Maya's face.
                offset=Vector((-2.5,-6.8,2.9)) if speaker=='MAYA' else Vector((1.6 if speaker=='TECO' else -1.6,-6.6,2.9))
                loc=locbase+offset;target=locbase+Vector((0,0,1.12));lens=46
            name=f"EP2_Camera_{sc['id']}_{idx}"
            cam=shot_camera(name,loc,target,lens);f=round(time*timeline['fps'])+1
            marker=s.timeline_markers.new(name,frame=f);marker.camera=cam
            shotlist.append(dict(name=name,start=time,camera=cam.name))
    for i,shot in enumerate(shotlist):
        end=shotlist[i+1]['start'] if i+1<len(shotlist) else timeline['duration']
        shot['end']=end;cam=bpy.data.objects[shot['camera']]
        a=round(shot['start']*timeline['fps'])+1;b=max(a+1,round(end*timeline['fps']))
        key(cam,'location',a);direction=cam.rotation_euler.to_quaternion()@Vector((0,0,-1));cam.location+=direction*.18;key(cam,'location',b)
    s.camera=bpy.data.objects[shotlist[0]['camera']]
    stumble=next((c['start'] for c in timeline['dialogue'] if c.get('event')=='stumble'),scenes['chase']['start']+8)
    care=scenes['care'];bloomline=[c for c in timeline['dialogue'] if c['scene']==care['id']][-1]
    for frame in range(1,timeline['frames']+1):
        t=(frame-1)/timeline['fps']
        sc=next(c for c in timeline['scenes'] if c['start']<=t<c['end'])
        local=t-sc['start'];phase=local/(sc['end']-sc['start'])
        active=next((c for c in timeline['dialogue'] if c['start']<=t<c['end']),None)
        for index,(name,r) in enumerate(rigs.items()):
            loc=position(name,t);velocity=(position(name,t+1/timeline['fps'])-loc)*timeline['fps']
            speed=min(1.5,velocity.length);walk=min(1,speed*5)
            r['phase']+=speed/timeline['fps']/.65*math.tau
            gait=r['phase'];trip=pulse(stumble,stumble+1.8,t,.45) if name=='Teco' else 0
            cheer=pulse(scenes['finale']['start']+1,scenes['finale']['start']+6,t)
            loc.z=.012*math.sin(t*2+index)+abs(math.sin(gait))*.065*walk+max(0,math.sin(t*6+index))*.10*cheer
            r['root'].location=loc;r['root'].rotation_euler=(.32*trip,.18*trip,.45*walk*math.copysign(1,velocity.x or 1))
            r['root'].scale=(1+.06*trip,1+.06*trip,1-.12*trip)
            for prop in ('location','rotation_euler','scale'):key(r['root'],prop,frame)
            shadows[name].location=(loc.x,loc.y,-.043);key(shadows[name],'location',frame)
            amp=0
            if active and active['speaker']==name.upper():
                j=int((t-active['start'])*timeline['fps']);env=active['envelope']
                amp=env[j] if j<len(env) else 0
            r['head'].rotation_euler=(.025*math.sin(t*2+index)+.05*amp*math.sin(t*8),.045*math.sin(t*1.8+index),.08*math.sin(t*.8+index))
            key(r['head'],'rotation_euler',frame)
            r['mouth'].scale=(.13+.02*trip,.035,.017+.09*amp+.035*trip)
            r['tongue'].scale=(.065,.015,.009+.025*amp)
            key(r['mouth'],'scale',frame);key(r['tongue'],'scale',frame)
            blink=1-.95*math.exp(-((((t+index*.72)%4.1)-.1)/.065)**2)
            for o,scale,pos in r['eyes']:
                o.scale=(scale.x,scale.y,scale.z*blink*(1+.15*trip));key(o,'scale',frame)
                if '_pupila' in o.name:o.location=pos+Vector((.024*math.sin(t*.7),-.003,.008*math.sin(t)));key(o,'location',frame)
            goodbye=smooth(scenes['finale']['end']-12,scenes['finale']['end']-10,t)
            for arm,side in r['arms']:
                gesture=(.45 if name=='Maya' else .85 if name=='Teco' else .6)*amp*(.7+.3*math.sin(t*7))
                wave=goodbye*(1.8+.4*math.sin(t*9+index)) if side==1 else 0
                arm.rotation_euler=(.65*walk*math.sin(gait+side*math.pi/2),-side*(.1+gesture+wave+1.1*trip+.6*cheer),0)
                key(arm,'rotation_euler',frame)
            for foot,side in r['feet']:
                foot.rotation_euler.x=.55*walk*math.sin(gait+side*math.pi/2)
                foot.location.z=.28+max(0,math.sin(gait+side*math.pi/2))*.06*walk
                key(foot,'rotation_euler',frame);key(foot,'location',frame)
            for brow,side in zip(r['brows'],(-1,1)):
                brow.location.z=.47+.04*amp+.08*trip;brow.rotation_euler.y=side*(.08+.09*amp)
                key(brow,'location',frame);key(brow,'rotation_euler',frame)
        pos=butterfly_position(t,scenes)
        butterfly.location=pos;butterfly.scale=(.48,)*3;butterfly.rotation_euler=(.12*math.sin(t*1.3),.15*math.sin(t),.20*math.sin(t*.8))
        key(butterfly,'location',frame);key(butterfly,'rotation_euler',frame);key(butterfly,'scale',frame)
        for wing,side in wings:
            wing.rotation_euler.z=side*(.25+1.05*math.sin(t*math.tau*2.5))
            key(wing,'rotation_euler',frame)
        for i,(group,petals) in enumerate(flowers):
            planted=smooth(care['start']+4+i*1.5,care['start']+6+i*1.5,t)
            group.scale=(1 if i<2 else max(.001,planted),)*3
            group.rotation_euler=(.025*math.sin(t*1.5+i),.035*math.sin(t*1.2+i),0)
            key(group,'scale',frame);key(group,'rotation_euler',frame)
            opening=1 if i<2 else .28+.72*smooth(bloomline['start'],min(care['end']-.3,bloomline['end']),t)
            for pet,base in petals:pet.scale=base*opening;key(pet,'scale',frame)
        watering=pulse(care['start']+5,care['start']+16,t,.6)
        loc=position('Teco',t)+Vector((-.65,-.45,.95))
        can.location=loc;can.rotation_euler.y=-.4*watering;can.scale=(max(.001,watering),)*3
        for prop in ('location','rotation_euler','scale'):key(can,prop,frame)
        for i,drop in enumerate(drops):
            p=(t*1.7+i/len(drops))%1;drop.location=loc+Vector((-.35-.15*p,0,-.9*p));drop.scale=(.022*watering,.022*watering,.06*watering)
            key(drop,'location',frame);key(drop,'scale',frame)
        pollinating=1 if sc['mode']=='garden' else 0
        for i,dot in enumerate(pollen):
            dot.location=pos+Vector((.09*math.sin(t+i),-.06,.1*math.cos(t+i)))
            dot.scale=(.023*pollinating,)*3;key(dot,'location',frame);key(dot,'scale',frame)
    for action in bpy.data.actions:
        if action.users:
            for curve in action.fcurves:
                for point in curve.keyframe_points:point.interpolation='LINEAR'
    s.frame_set(1)
    name=f"episodio_{timeline['episode']}_"+('planejamento' if timeline['provisional'] else 'final')+'.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/name))
    (out/'shots.json').write_text(json.dumps(shotlist,indent=2))
    print('SCENE_BUILT',name,timeline['frames'],flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--timeline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--width',type=int,default=1920);p.add_argument('--engine',default='BLENDER_WORKBENCH')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.mkdir(parents=True,exist_ok=True)
    build(json.loads(a.timeline.read_text()),a.output,a.width,a.engine)


if __name__=='__main__':main()
