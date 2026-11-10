"""Check actual baked demonstration poses so viewers can imitate the instructions."""
import json,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];out=Path(args[0]) if args else ROOT/'EPISODIO_04/ARTEFATOS';t=json.loads((out/'timeline.json').read_text());s=bpy.context.scene;checks=[]
for c in t['dialogue']:
 if c.get('event') not in ('stretch','rain_game'):continue
 seconds=c['end']+1;s.frame_set(round(seconds*t['fps'])+1)
 for name in ('Capi','Teco','Maya'):
  arms=[bpy.data.objects[name+'_EP4_Arm'+str(side)] for side in (-1,1)];tips=[a.matrix_world@Vector((0,0,-.59)) for a in arms]
  if c['event']=='stretch':
   z=bpy.data.objects[name+'_EP4_Root'].matrix_world.translation.z
   if min(p.z-z for p in tips)<1.25:raise ValueError('Braços não estão levantados: '+name)
  else:
   if (tips[0]-tips[1]).length>.32:raise ValueError('Mãos não se encontram na brincadeira: '+name)
  checks.append(dict(id=c['id'],character=name,hand_distance=(tips[0]-tips[1]).length))
(out/'interaction-validation.json').write_text(json.dumps(dict(passed=True,checks=checks),indent=2));print('INTERACTIONS_VALIDATED',len(checks))
