"""Water-cycle animation. Original rigs/scenery, reused flowers/stream, illustrative diagrams."""
import argparse,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from producao.animacao import empty,key,material,shot_camera,smooth,pulse,sphere
from producao.serie.cena import character,configure

def library(name):
 with bpy.data.libraries.load(str(ROOT/'EPISODIO_04/ASSETS'/name),link=False) as (src,dst):dst.objects=list(src.objects)
 for o in dst.objects:
  if o:bpy.context.collection.objects.link(o)
 return dst.objects

def droplet(name,parent,mat,size=1):
 root=empty(name,(0,0,0),parent)
 sphere(name+'_Corpo',(0,0,0),(.13*size,.085*size,.18*size),mat,root)
 tip=sphere(name+'_Ponta',(0,0,.14*size),(.075*size,.055*size,.12*size),mat,root);tip.rotation_euler.y=.12
 return root

def build(t,out,width=1920,engine='BLENDER_WORKBENCH'):
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'EPISODIO_01/CENAS/personagens.blend'))
 s=bpy.context.scene;configure(s,width,engine);s.frame_start=1;s.frame_end=t['frames'];s.render.fps=t['fps']
 for o in list(bpy.data.objects):
  o.animation_data_clear()
  if o.type=='MESH' and o.name.startswith(('Capi_','Teco_','Maya_')):
   for poly in o.data.polygons:poly.use_smooth=True
 seed=bpy.data.objects.get('Sementinha Magica')
 if seed:seed.hide_render=True
 ground=bpy.data.objects.get('Clareira')
 if ground:ground.scale.x*=1.6;ground.scale.y*=1.6
 dark=material('EP4_Escuro',(.10,.045,.045));pink=material('EP4_Lingua',(1,.32,.45));blue=material('EP4_Agua',(.08,.59,.96));cyan=material('EP4_Reflexo',(.59,.90,1));white=material('EP4_Branco',(.97,.98,1));gold=material('EP4_Sol',(1,.75,.08));orange=material('EP4_Setas',(1,.46,.06));green=material('EP4_Folha',(.23,.66,.25))
 rigs={n:character(n,x,y,dark,pink) for n,x,y in [('Capi',-2.2,-.5),('Teco',2.2,-.5),('Maya',0,1.8)]}
 for name,r in rigs.items():
  mat=bpy.data.objects[name+'_corpo'].data.materials[0]
  for arm,side in r['arms']:sphere(name+'_EP4_Mao'+str(side),(0,0,-.59),(.11,.09,.11),mat,arm)
 for o in bpy.data.objects:
  if '_EP2_' in o.name:o.name=o.name.replace('_EP2_','_EP4_')
 roots={n:r['origin'].copy() for n,r in rigs.items()};roots['Maya'].y=1.05
 library('riacho_reutilizado.blend');flowers=library('flores_reutilizadas.blend')
 plants=sorted([o for o in flowers if o.name.startswith('EP2_Flor_')],key=lambda o:o.name)
 for group,pos in zip(plants,[(-4,1.2),(-3.8,-1.7),(3.9,-1.5),(4.5,1),(2.1,1.3),(-1.8,1.15)]):group.location=(pos[0],pos[1],0);group.scale=(1,1,1)
 trunks=[o for o in bpy.data.objects if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='Tronco'];crowns=[o for o in bpy.data.objects if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='Folhas']
 if trunks and crowns:
  for i,(x,y) in enumerate([(-7,6),(-3.8,7),(0,7.5),(4,7),(7,6),(-8,-1),(8,0)]):
   for proto,z in [(trunks[0],1.5),(crowns[0],3.5)]:
    o=bpy.data.objects.new(f'EP4_Arvore_{i}_{z}',proto.data);bpy.context.collection.objects.link(o);o.location=(x,y,z)
 puddle=empty('EP4_Poca',(-.15,-1.10,.005));sphere('EP4_PocaSuperficie',(0,0,0),(1.15,.65,.018),blue,puddle)
 for i in range(3):sphere('EP4_PocaReflexo'+str(i),(-.5+i*.42,.05*math.sin(i),.019),(.20,.025,.004),cyan,puddle)
 sun=empty('EP4_Sol',(-4.5,5.0,6.0));sphere('EP4_SolDisco',(0,0,0),(.56,.14,.56),gold,sun)
 rays=empty('EP4_Raios',(0,0,0),sun)
 for i in range(10):
  a=i*math.tau/10;o=sphere('EP4_Raio'+str(i),(.82*math.cos(a),0,.82*math.sin(a)),(.07,.05,.22),gold,rays);o.rotation_euler.y=math.pi/2-a
 for side in (-1,1):sphere('EP4_SolOlho'+str(side),(side*.18,-.14,.1),(.04,.02,.07),dark,sun)
 sphere('EP4_SolSorriso',(0,-.145,-.16),(.17,.02,.035),orange,sun)
 board=empty('EP4_Modelo',(0,1.4,5.0));boardmat=material('EP4_FundoModelo',(.35,.72,.90));sphere('EP4_Painel',(0,.55,0),(3.3,.06,1.8),boardmat,board)
 cloud=empty('EP4_Nuvem',(0,0,.2),board)
 for i in range(9):
  x=(i%5-2)*.46;z=.15+(.18 if i%3==0 else 0)
  sphere('EP4_NuvemParte'+str(i),(x,(i//5)*.12,z),(.53,.25,.38),white,cloud)
 little=[]
 for i in range(18):
  d=droplet('EP4_GotinhaNuvem'+str(i),board,cyan,.5);little.append(d)
 mascot=droplet('EP4_Gotinha',board,blue,2.0)
 for side in (-1,1):
  sphere('EP4_GotinhaOlho'+str(side),(side*.10,-.16,.04),(.055,.025,.07),white,mascot)
  sphere('EP4_GotinhaPupila'+str(side),(side*.10,-.184,.03),(.025,.012,.04),dark,mascot)
  sphere('EP4_GotinhaMao'+str(side),(side*.30,0,-.03),(.09,.06,.055),blue,mascot)
 sphere('EP4_GotinhaSorriso',(0,-.17,-.12),(.095,.015,.025),dark,mascot)
 rainhero=droplet('EP4_GotaCrescendo',board,blue,1)
 arrows=[]
 for i in range(4):
  a=empty('EP4_Seta'+str(i));sphere('EP4_SetaHaste'+str(i),(0,0,0),(.035,.035,.22),orange,a)
  for side in (-1,1):
   head=sphere(f'EP4_SetaPonta{i}_{side}',(side*.065,0,.17),(.025,.025,.11),orange,a);head.rotation_euler.y=side*-.65
  arrows.append(a)
 drops=[droplet('EP4_Chuva'+str(i),None,blue,.72+(i%4)*.10) for i in range(44)]
 sc={x['mode']:x for x in t['scenes']};beat=60/112
 def position(name,seconds):
  loc=roots[name].copy();arrival=smooth(1,9,seconds);loc.x+=(-.30 if name=='Teco' else .30 if name=='Capi' else .25)*arrival
  if sc['discovery']['start']<=seconds<sc['chase']['start']:
   amount=pulse(sc['discovery']['start']+1,sc['discovery']['end']-2,seconds,2);loc.x+=(-.30 if name=='Teco' else .25 if name=='Capi' else 0)*amount
  if sc['chase']['start']<=seconds<sc['chase']['end']:
   p=smooth(sc['chase']['start']+3,sc['chase']['end']-3,seconds);loc.x+=(.55 if name=='Teco' else -.25 if name=='Capi' else .18)*math.sin(p*math.tau);loc.y-=.15*(1-math.cos(p*math.tau))
  if seconds>=sc['finale']['start']:
   p=seconds-sc['finale']['start'];loc.x+=.18*math.sin(p/beat*math.pi);loc.y+=.06*math.sin(p/beat*math.pi*2)
  return loc
 shots=[]
 for scene in t['scenes']:
  entries=[dict(start=scene['start'],speaker='NARRADORA')]+[c for c in t['dialogue'] if c['scene']==scene['id']]
  for i,line in enumerate(entries):
   time=line['start'];end=entries[i+1]['start'] if i+1<len(entries) else scene['end'];mode=scene['mode'];kind='wide'
   loc=Vector((5,-12,6));target=Vector((0,.3,1.0));lens=43
   if line['speaker']!='NARRADORA':
    pos=position(line['speaker'].title(),time);loc=pos+Vector((1.4 if line['speaker']=='TECO' else -1.4,-6.7,2.7));target=pos+Vector((0,0,1.17));lens=47;kind='speaker'
   if mode=='intro' and i==1:loc=Vector((3,-5,4.6));target=Vector((-.15,-1.1,.05));lens=45;kind='puddle'
   if mode=='discovery' and i in (2,4,5):loc=Vector((4,-8,4.3));target=Vector((0,-.8,1.1));lens=43;kind='evaporation'
   if mode in ('chase','investigate') and i in (0,2,4,5,6):loc=Vector((0,-7.0,5.7));target=Vector((0,1.4,5.0));lens=44;kind='diagram'
   if mode=='garden' and i in (0,1,2,3):loc=Vector((0,-7.2,5.8));target=Vector((0,1.4,4.8));lens=44;kind='diagram'
   if line.get('event') in ('stretch','rain_game','chorus') or mode=='finale':loc=Vector((2.8,-10.8,4.6));target=Vector((0,.1,1.0));lens=44;kind='action'
   name=f'EP4_Camera_{len(shots):02}';cam=shot_camera(name,loc,target,lens);a=round(time*t['fps'])+1;b=max(a+1,round(end*t['fps']));marker=s.timeline_markers.new(name,frame=a);marker.camera=cam
   key(cam,'location',a);cam.location+=(target-loc).normalized()*.17;key(cam,'location',b)
   shots.append(dict(name=name,start=time,end=end,camera=cam.name,kind=kind))
 s.camera=bpy.data.objects[shots[0]['camera']]
 for f in range(1,t['frames']+1):
  seconds=(f-1)/t['fps'];current_shot=next(x for x in shots if x['start']<=seconds<x['end']);board.scale=(1 if current_shot['kind']=='diagram' else .001,)*3;key(board,'scale',f)
  active=next((c for c in t['dialogue'] if c['start']<=seconds<c['end']),None)
  interaction=next((c for c in t['dialogue'] if c.get('event') and c['end']<=seconds<c['end']+c.get('pause_after',.8)),None)
  game=next((c for c in t['dialogue'] if c.get('event')=='rain_game' and c['start']<=seconds<c['end']+c['pause_after']),None)
  stretch=next((c for c in t['dialogue'] if c.get('event')=='stretch' and c['start']<=seconds<c['end']+c['pause_after']),None)
  dance=smooth(sc['finale']['start']+1,sc['finale']['start']+3,seconds);phase=(seconds-sc['finale']['start'])/beat*math.pi
  for i,(name,r) in enumerate(rigs.items()):
   loc=position(name,seconds);v=(position(name,seconds+1/t['fps'])-loc)*t['fps'];walk=min(1,v.length*5);r['phase']+=v.length/t['fps']/.65*math.tau;gait=r['phase']
   loc.z=.012*math.sin(seconds*2+i)+.065*abs(math.sin(gait))*walk+.065*max(0,math.sin(phase*2+i*.3))*dance
   bend=.13*pulse(sc['intro']['start']+2,sc['intro']['start']+10,seconds) if name!='Maya' else 0
   r['root'].location=loc;r['root'].rotation_euler=(bend,.06*dance*math.sin(phase+i),.18*walk*math.copysign(1,v.x or 1)+.16*dance*math.sin(phase+i*.4));key(r['root'],'location',f);key(r['root'],'rotation_euler',f)
   amp=0
   if active and active['speaker']==name.upper():
    j=int((seconds-active['start'])*t['fps']);amp=active['envelope'][j] if j<len(active['envelope']) else 0
   r['head'].rotation_euler=(.035*math.sin(seconds*2+i)+.035*amp*math.sin(seconds*8),.05*math.sin(seconds*1.7+i)+(.12 if interaction else 0),.07*math.sin(seconds*.8+i));key(r['head'],'rotation_euler',f)
   r['mouth'].scale=(.13,.035,.017+.09*amp);r['tongue'].scale=(.065,.015,.009+.025*amp);key(r['mouth'],'scale',f);key(r['tongue'],'scale',f)
   blink=1-.95*math.exp(-((((seconds+i*.72)%4.1)-.1)/.065)**2)
   for o,scale,pos in r['eyes']:o.scale=(scale.x,scale.y,scale.z*blink);key(o,'scale',f)
   goodbye=smooth(t['duration']-9,t['duration']-7,seconds)
   for arm,side in r['arms']:
    gesture=amp*(.42 if name=='Maya' else .83 if name=='Teco' else .62)*(.7+.3*math.sin(seconds*7))
    up=1.45 if stretch else .40 if interaction else 0
    tap=.4*(1+math.sin(seconds*12+side)) if game else 0
    waving=goodbye*(1.7+.4*math.sin(seconds*9+i)) if side==1 else 0
    arm.rotation_euler=(.68*walk*math.sin(gait+side*math.pi/2)-tap,-side*(.1+gesture+up+waving+dance*(.65+.45*math.sin(phase+side*1.3+i*.3))),.08*dance*math.sin(phase));
    if stretch:arm.rotation_euler=(0,-side*2.65,0)
    if game:
     direction=Vector((-side*.44,-.40,-.14 if side==-1 else -.07+.06*math.sin(seconds*12)))
     arm.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    key(arm,'rotation_euler',f)
   for foot,side in r['feet']:
    step=math.sin(gait+side*math.pi/2);foot.rotation_euler.x=.60*walk*step+.12*dance*math.sin(phase+side);foot.location.z=.28+.07*max(0,step)*walk;key(foot,'rotation_euler',f);key(foot,'location',f)
  shrink=smooth(sc['intro']['start']+3,sc['chase']['start'],seconds);refill=smooth(sc['care']['start'],sc['care']['start']+8,seconds);scale=(1-.72*shrink)+.72*refill;puddle.scale=(scale,scale,1);key(puddle,'scale',f)
  rays.rotation_euler.y=seconds*.12;key(rays,'rotation_euler',f)
  sun.rotation_euler.y=.04*math.sin(seconds*.8);key(sun,'rotation_euler',f)
  cloud.location=(.12*math.sin(seconds*.7),0,.2+.055*math.sin(seconds*.9));key(cloud,'location',f)
  mascot.location=(1.9+.18*math.sin(seconds*1.4),-.1,-.45+.17*math.sin(seconds*1.8));mascot.rotation_euler.y=.20*math.sin(seconds*2.2);key(mascot,'location',f);key(mascot,'rotation_euler',f)
  for i,group in enumerate(plants):group.rotation_euler=(.035*math.sin(seconds*1.5+i),.065*math.sin(seconds*1.3+i),0);key(group,'rotation_euler',f)
  for i,a in enumerate(arrows):
   visibility=1 if sc['discovery']['start']<=seconds<sc['chase']['end'] else .001;p=(seconds*.34+i*.25)%1;a.location=(-.8+i*.45,-1.1+.12*math.sin(i),.10+2.25*p);a.scale=(visibility,)*3;key(a,'location',f);key(a,'scale',f)
  fall=next(c['start'] for c in t['dialogue'] if c['scene']=='garden' and c['speaker']=='CAPI')
  grow=.25+1.05*smooth(sc['garden']['start']+1,fall,seconds)
  falling=smooth(fall+.7,fall+2.8,seconds)
  rainhero.location=(-.45,-.65,.15-1.65*falling);rainhero.scale=(grow if sc['garden']['start']<=seconds<fall+3 else .001,)*3;key(rainhero,'location',f);key(rainhero,'scale',f)
  for i,d in enumerate(little):
   growth=smooth(sc['chase']['start']+5,sc['investigate']['start']+7,seconds);angle=i*2.4+seconds*.4;d.location=(-1.65+(i%6)*.55+.06*math.sin(angle),-.4,-.65+(i//6)*.32+.05*math.cos(angle));d.scale=(max(.001,growth),)*3;key(d,'location',f);key(d,'scale',f)
  rain_start=round(sc['garden']['start']*t['fps']);rain_end=round((sc['care']['start']+3)*t['fps'])
  if f==1 or rain_start<=f<=rain_end+1:
   for i,d in enumerate(drops):
    visible=1 if rain_start<f<=rain_end and (current_shot['kind']=='diagram' or seconds>=sc['garden']['end']-3) else .001;p=(seconds*1.45+i*.618)%1
    # Top half is the enlarged teaching model; ground rain is confined to the later cut.
    if seconds<sc['garden']['end']-3:d.location=(-1.8+(i%9)*.44,1.0+(i%3)*.10,5.5-2.2*p)
    else:d.location=(-4+(i%11)*.8,3.8+(i//11)*.45,3.6-3.55*p)
    d.scale=(visible,)*3;key(d,'location',f);key(d,'scale',f)
 for action in bpy.data.actions:
  if action.users:
   for curve in action.fcurves:
    for pt in curve.keyframe_points:pt.interpolation='LINEAR'
 s.frame_set(1);name=f"episodio_{t['episode']}_"+('planejamento' if t['provisional'] else 'final')+'.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out/name));(out/'shots.json').write_text(json.dumps(shots,indent=2));print('SCENE_BUILT',name,t['frames'],flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--timeline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--width',type=int,default=1920);p.add_argument('--engine',default='BLENDER_WORKBENCH');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);build(json.loads(a.timeline.read_text()),a.output,a.width,a.engine)
if __name__=='__main__':main()
