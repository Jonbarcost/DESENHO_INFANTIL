"""Ensure illustrative model visibility agrees with active camera on cut frames."""
import json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];out=Path(args[0]) if args else ROOT/'EPISODIO_04/ARTEFATOS';t=json.loads((out/'timeline.json').read_text());shots=json.loads((out/'shots.json').read_text());s=bpy.context.scene;checks=[]
for shot in shots:
 f=round(shot['start']*t['fps'])+1;s.frame_set(f);expected=1 if shot['kind']=='diagram' else .001;actual=bpy.data.objects['EP4_Modelo'].scale.x
 if abs(expected-actual)>.001:raise ValueError(f'Modelo incompatível com câmera no corte {f}: {shot["name"]}')
 checks.append(dict(frame=f,shot=shot['name'],scale=actual))
(out/'cut-validation.json').write_text(json.dumps(dict(passed=True,checks=checks),indent=2));print('CUTS_VALIDATED',len(checks))
