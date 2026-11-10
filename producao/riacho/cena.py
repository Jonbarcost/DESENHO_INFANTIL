"""Editable, baked stream adventure using the three original character meshes."""
import argparse,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from producao.animacao import empty,key,material,parent_keep,pulse,shot_camera,smooth,sphere
from producao.serie.cena import character,configure

def channel(x):return 2.8+.32*math.sin(x*.55)
def level(x):return .16-.007*x

def ribbon(name,width,mat):
    verts=[]
    for i in range(81):
        x=-10+i*.25
        for side in (-1,1):verts.append((x,channel(x)+side*width,level(x)-(0 if name=='EP3_Agua' else .025)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],[(i,i+1,i+3,i+2) for i in range(0,160,2)]);mesh.materials.append(mat)
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return o

def build(timeline,out,width=1920,engine='BLENDER_WORKBENCH'):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'EPISODIO_01/CENAS/personagens.blend'))
    s=bpy.context.scene;configure(s,width,engine);s.frame_start=1;s.frame_end=timeline['frames'];s.render.fps=timeline['fps']
    for o in list(bpy.data.objects):
        o.animation_data_clear()
        if o.type=='MESH' and any(o.name.startswith(n+'_') for n in ('Capi','Teco','Maya')):
            for p in o.data.polygons:p.use_smooth=True
    seed=bpy.data.objects.get('Sementinha Magica')
    if seed:seed.hide_render=True
    ground=bpy.data.objects.get('Clareira')
    if ground:ground.scale.x*=1.6;ground.scale.y*=1.6
    dark=material('EP3_Escuro',(.12,.045,.04));pink=material('EP3_Lingua',(1,.32,.45));green=material('EP3_Verde',(.18,.62,.22))
    earth=material('EP3_Margem',(.48,.32,.16));blue=material('EP3_Agua',(.12,.60,.87));white=material('EP3_Brilho',(.72,.94,1))
    orange=material('EP3_Peixe',(1,.52,.10));yellow=material('EP3_Amarelo',(1,.86,.32));leafmat=material('EP3_Folha',(.77,.43,.13))
    ribbon('EP3_Margem',1.13,earth);ribbon('EP3_Agua',.83,blue)
    rigs={n:character(n,x,y,dark,pink) for n,x,y in [('Capi',-2.2,-.5),('Teco',2.2,-.5),('Maya',0,1.8)]}
    # Maya's original geometry is at y=1.8; shift the finished rig, not the mesh parenting reference.
    # character() needs original world origin to preserve original proportions.
    for o in bpy.data.objects:
        if '_EP2_' in o.name:o.name=o.name.replace('_EP2_','_EP3_')
    trunks=[o for o in bpy.data.objects if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='Tronco']
    crowns=[o for o in bpy.data.objects if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='Folhas']
    for i,(x,y) in enumerate([(-7,6),(-4.5,7),(0,7),(4,7),(7,6),(-8,-1),(8,0)]):
        if trunks and crowns:
            for proto,z in [(trunks[0],1.5),(crowns[0],3.5)]:
                obj=bpy.data.objects.new(f'EP3_Arvore_{i}_{z}',proto.data);bpy.context.collection.objects.link(obj);obj.location=(x,y,z)
    rockmat=material('EP3_Pedra',(.56,.62,.62))
    for i in range(24):
        x=-8+i*.7;y=channel(x)+(-1 if i%2 else 1)*.96
        sphere('EP3_Pedra_'+str(i),(x,y,level(x)),(.22,.16,.14),rockmat)
    ripples=[sphere('EP3_Corrente_'+str(i),(0,0,0),(.22,.025,.008),white) for i in range(14)]
    leaf=empty('EP3_FolhaFlutuante');sphere('EP3_FolhaLamina',(0,0,0),(.30,.15,.025),leafmat,leaf)
    vein=sphere('EP3_FolhaNervura',(0,0,.025),(.29,.012,.008),yellow,leaf)
    fish=empty('EP3_Peixe');sphere('EP3_PeixeCorpo',(0,0,0),(.35,.14,.17),orange,fish)
    tail=empty('EP3_Cauda',(-.30,0,0),fish);sphere('EP3_CaudaForma',(-.15,0,0),(.20,.045,.22),yellow,tail)
    for side in (-1,1):
        sphere('EP3_PeixeOlho'+str(side),(.19,side*.12,.07),(.058,.025,.058),white,fish)
        sphere('EP3_PeixePupila'+str(side),(.21,side*.143,.07),(.027,.012,.03),dark,fish)
    fin=sphere('EP3_Barbatana',(0,0,.17),(.13,.035,.10),yellow,fish)
    frog=empty('EP3_Sapo',(3.5,1.30,.16));sphere('EP3_SapoCorpo',(0,0,.12),(.29,.22,.23),green,frog)
    throat=sphere('EP3_SapoPapo',(0,-.18,.12),(.20,.09,.15),yellow,frog)
    for side in (-1,1):
        sphere('EP3_SapoPe'+str(side),(side*.25,-.08,.01),(.15,.20,.07),green,frog)
        sphere('EP3_SapoOlho'+str(side),(side*.16,-.09,.33),(.11,.09,.12),white,frog)
        sphere('EP3_SapoPupila'+str(side),(side*.16,-.17,.33),(.045,.025,.06),dark,frog)
    plants=[]
    for i in range(10):
        x=-5+i*1.1;y=channel(x)-1.13
        group=empty('EP3_Planta_'+str(i),(x,y,0))
        for j in range(3):
            blade=sphere(f'EP3_Grama_{i}_{j}',((j-1)*.09,0,.22),(.035,.035,.25),green,group);blade.rotation_euler.y=(j-1)*.3
        plants.append(group)
        for j in range(3):
            root=sphere(f'EP3_Raiz_{i}_{j}',((j-1)*.12,-.12,.07),(.022,.23,.025),earth,group);root.rotation_euler.z=(j-1)*.3
    clouds=[]
    for i in range(3):
        c=empty('EP3_Nuvem_'+str(i),(-4+i*4,8,5.8))
        for j in range(3):sphere(f'EP3_Nuvem_{i}_{j}',((j-1)*.65,0,.15*(j%2)),(.75,.38,.40),white,c)
        clouds.append(c)
    paper=material('EP3_Papel',(.98,.92,.78));bagmat=material('EP3_Saco',(.44,.26,.13))
    basket=sphere('EP3_SacoColeta',(1.4,-.8,.31),(.30,.24,.35),bagmat)
    papers=[sphere('EP3_Papel_'+str(i),(.6+i*.19,-.75-i*.10,.02),(.13,.10,.012),paper) for i in range(3)]
    right=next(a for a,side in rigs['Capi']['arms'] if side==1)
    glove=sphere('EP3_Luva',(0,0,-.59),(.14,.13,.13),yellow,right)
    for side in (-1,1):sphere('EP3_Pinca'+str(side),(side*.035,-.01,-.78),(.018,.025,.16),rockmat,right)
    scenes={c['mode']:c for c in timeline['scenes']};init={n:r['origin'].copy() for n,r in rigs.items()}
    init['Maya'].y=1.1
    def position(n,t):
        loc=init[n].copy();travel=smooth(scenes['discovery']['start']+1,scenes['discovery']['start']+9,t)
        loc.x+=.45*travel;loc.y+=.13*travel
        if n=='Teco' and scenes['chase']['start']<=t<scenes['chase']['end']:
            a=math.tau*smooth(scenes['chase']['start']+2,scenes['chase']['end']-3,t);loc.x+=.7*math.sin(a);loc.y+=.25*(math.cos(a)-1)
        if n=='Capi':loc=loc.lerp(Vector((.12,-.12,0)),smooth(scenes['care']['start']-3,scenes['care']['start']+2,t))
        return loc
    shotlist=[]
    def shot(time,end,speaker,mode,index,line):
        center=Vector((.2,.8,1.0));loc=center+Vector((5,-12,5.7));target=center;lens=43
        if speaker!='NARRADORA':
            pos=position(speaker.title(),time);loc=pos+Vector((-1.3 if speaker!='TECO' else 1.3,-6.7,2.6));target=pos+Vector((0,0,1.17));lens=47
        if mode=='care':loc=Vector((3.8,-8.4,4));target=Vector((.55,-.25,.75));lens=43
        if mode=='chase' and (speaker=='NARRADORA' or index in (1,4)):
            loc=Vector((.5,5.3,6));target=Vector((.7,2.8,.15));lens=48
        if mode=='investigate' and index in (1,2):loc=Vector((2,5.7,2.5));target=Vector((1,channel(1),.22));lens=48
        if mode=='investigate' and index==4:loc=Vector((6.4,1.6,1.8));target=Vector((3.5,1.3,.4));lens=52
        name=f'EP3_Camera_{len(shotlist):02}';cam=shot_camera(name,loc,target,lens)
        a=round(time*timeline['fps'])+1;b=max(a+1,round(end*timeline['fps']));marker=s.timeline_markers.new(name,frame=a);marker.camera=cam
        key(cam,'location',a);cam.location+=(target-loc).normalized()*.16;key(cam,'location',b)
        shotlist.append(dict(name=name,start=time,end=end,camera=cam.name))
    for sc in timeline['scenes']:
        entries=[dict(start=sc['start'],speaker='NARRADORA')]+[c for c in timeline['dialogue'] if c['scene']==sc['id']]
        for i,line in enumerate(entries):shot(line['start'],entries[i+1]['start'] if i+1<len(entries) else sc['end'],line['speaker'],sc['mode'],i,line)
    s.camera=bpy.data.objects[shotlist[0]['camera']]
    stumble=next(c['start'] for c in timeline['dialogue'] if c.get('event')=='stumble')
    cleanup=next(c['start'] for c in timeline['dialogue'] if c.get('event')=='cleanup')
    for f in range(1,timeline['frames']+1):
        t=(f-1)/timeline['fps'];active=next((c for c in timeline['dialogue'] if c['start']<=t<c['end']),None)
        for i,(name,r) in enumerate(rigs.items()):
            loc=position(name,t);v=(position(name,t+1/timeline['fps'])-loc)*timeline['fps'];speed=v.length;walk=min(1,speed*5);r['phase']+=speed/timeline['fps']/.65*math.tau;gait=r['phase']
            trip=pulse(stumble,stumble+1.5,t,.35) if name=='Teco' else 0
            kneel=pulse(cleanup+.4,cleanup+14,t,.7) if name=='Capi' else 0
            cheer=pulse(scenes['finale']['start']+1,scenes['finale']['start']+5,t)
            loc.z=.012*math.sin(t*2+i)+abs(math.sin(gait))*.065*walk+max(0,math.sin(t*6+i))*.09*cheer-.18*kneel
            r['root'].location=loc;r['root'].rotation_euler=(.35*trip+.45*kneel,.12*trip,.25*walk*math.copysign(1,v.x or 1));key(r['root'],'location',f);key(r['root'],'rotation_euler',f)
            amp=0
            if active and active['speaker']==name.upper():
                j=int((t-active['start'])*timeline['fps']);env=active['envelope'];amp=env[j] if j<len(env) else 0
            r['head'].rotation_euler=(.03*math.sin(t*2+i)+.05*amp*math.sin(t*8),.045*math.sin(t*1.7+i),.08*math.sin(t*.8+i));key(r['head'],'rotation_euler',f)
            r['mouth'].scale=(.13,.035,.017+.09*amp);r['tongue'].scale=(.065,.015,.009+.025*amp);key(r['mouth'],'scale',f);key(r['tongue'],'scale',f)
            blink=1-.95*math.exp(-((((t+i*.72)%4.1)-.1)/.065)**2)
            for o,scale,pos in r['eyes']:o.scale=(scale.x,scale.y,scale.z*blink);key(o,'scale',f)
            goodbye=smooth(timeline['duration']-10,timeline['duration']-8,t)
            for arm,side in r['arms']:
                gesture=amp*(.45 if name=='Maya' else .8 if name=='Teco' else .6)*(.7+.3*math.sin(t*7))
                cycle=((t-cleanup-1)%4)/4
                pickup=(.60+.22*math.sin(cycle*math.tau))*kneel if side==1 else 0
                arm.rotation_euler=(.65*walk*math.sin(gait+side*math.pi/2)-pickup,-side*(.1+gesture+(goodbye*(1.8+.4*math.sin(t*9+i)) if side==1 else 0)+.6*trip+.5*cheer),0);key(arm,'rotation_euler',f)
            for foot,side in r['feet']:
                foot.rotation_euler.x=.55*walk*math.sin(gait+side*math.pi/2);foot.location.z=.28+max(0,math.sin(gait+side*math.pi/2))*.06*walk;key(foot,'rotation_euler',f);key(foot,'location',f)
        for i,ripple in enumerate(ripples):
            x=-9+((t*.7+i*1.31)%18);ripple.location=(x,channel(x)+.45*math.sin(i*2.3),level(x)+.009);key(ripple,'location',f)
        x=-2.6+5.2*smooth(scenes['chase']['start'],scenes['chase']['end'],t);leaf.location=(x,channel(x)-.1,level(x)+.045);leaf.rotation_euler.z=.22*math.sin(t);key(leaf,'location',f);key(leaf,'rotation_euler',f)
        fish.location=(1+.35*math.sin(t*.7),channel(1)+.2*math.sin(t),.25);fish.rotation_euler.z=.15*math.sin(t);tail.rotation_euler.z=.5*math.sin(t*8);key(fish,'location',f);key(fish,'rotation_euler',f);key(tail,'rotation_euler',f)
        frog.location.z=.16+max(0,math.sin(t*2))*.055;throat.scale=(.20,.09*(1+.25*math.sin(t*8)),.15);key(frog,'location',f);key(throat,'scale',f)
        for i,plant in enumerate(plants):plant.rotation_euler.y=.04*math.sin(t*1.5+i);key(plant,'rotation_euler',f)
        for i,c in enumerate(clouds):c.location.x=-4+i*4+.15*math.sin(t*.07);key(c,'location',f)
        visible=1 if cleanup<t<cleanup+15 else .001;glove.scale=(.14*visible,.13*visible,.13*visible);key(glove,'scale',f)
        for side in (-1,1):
            tong=bpy.data.objects['EP3_Pinca'+str(side)];tong.scale=(.018*visible,.025*visible,.16*visible);key(tong,'scale',f)
        bpy.context.view_layer.update()
        hand=right.matrix_world@Vector((0,0,-.94))
        for i,p in enumerate(papers):
            begin=cleanup+1+i*4;stage=(t-begin)/4;origin=Vector((.6+i*.19,-.75-i*.10,.02))
            if stage<0:p.location=origin;p.scale=(.13,.10,.012)
            elif stage<.28:p.location=origin.lerp(hand,smooth(0,.28,stage));p.scale=(.13,.10,.012)
            elif stage<.65:p.location=hand;p.scale=(.13,.10,.012)
            elif stage<1:p.location=hand.lerp(Vector((1.4,-.8,.40)),smooth(.65,1,stage));p.scale=(.13,.10,.012)
            else:p.location=(1.4,-.8,.25);p.scale=(.001,)*3
            key(p,'location',f);key(p,'scale',f)
    for action in bpy.data.actions:
        if action.users:
            for curve in action.fcurves:
                for pt in curve.keyframe_points:pt.interpolation='LINEAR'
    s.frame_set(1);name=f"episodio_{timeline['episode']}_"+('planejamento' if timeline['provisional'] else 'final')+'.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out/name));(out/'shots.json').write_text(json.dumps(shotlist,indent=2));print('SCENE_BUILT',name,flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--timeline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--width',type=int,default=1920);p.add_argument('--engine',default='BLENDER_WORKBENCH');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);build(json.loads(a.timeline.read_text()),a.output,a.width,a.engine)
if __name__=='__main__':main()
