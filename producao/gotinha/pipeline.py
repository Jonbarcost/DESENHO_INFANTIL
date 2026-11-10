"""Episode 04 adapters; validated Episodes 01–03 source remains unchanged."""
from pathlib import Path
import sys,os
from producao.serie import pipeline as p

def adapt_command(cmd):
    replacements={'producao/serie/cena.py':'producao/gotinha/cena.py','producao/serie/qa_cena.py':'producao/gotinha/qa_cena.py'}
    result=[]
    for arg in cmd:
        value=str(arg);normalized=value.replace(chr(92),'/')
        for source,target in replacements.items():
            if normalized==source or normalized.endswith('/'+source):
                value=str(p.ROOT/target);break
        result.append(value)
    return result

def main():
    # Parse exactly as argparse, including --output=path and abbreviations.
    import argparse
    guard=argparse.ArgumentParser(add_help=False)
    guard.add_argument('story',type=Path);guard.add_argument('--output',type=Path)
    args,_=guard.parse_known_args()
    story=p.load_story(args.story)
    if story['episode']!='04':raise SystemExit('Este adaptador produz somente o Episódio 04')
    out=(args.output or args.story.resolve().parent.parent/'ARTEFATOS').resolve()
    for protected in (p.ROOT/'EPISODIO_01',p.ROOT/'EPISODIO_02',p.ROOT/'EPISODIO_03',p.ROOT/'build/episodio_01'):
        if out==protected or protected in out.parents:
            raise SystemExit('Saída protegida: episódios anteriores são somente leitura')
    from producao.serie import audio
    from .audio import compose
    audio.compose=compose
    os.environ.setdefault('LP_NUM_THREADS','4')
    original_run=p.run
    def run(cmd,log):
        cmd=adapt_command(cmd)
        if cmd and Path(cmd[0]).name in ('ffmpeg','ffmpeg.exe') and str(cmd[-1]).endswith('episodio_04_final.partial.mp4'):
            import json
            from producao.serie.portable import bundled_font,filter_path
            timeline=json.loads((out/'timeline.json').read_text());index=cmd.index('-vf')+1
            scenes={x['mode']:x for x in timeline['scenes']}
            label=out/'representacao.txt';label.write_text('REPRESENTAÇÃO • O vapor de água é invisível',encoding='utf-8')
            font=bundled_font(p.ROOT)
            overlays=[f"drawtext=fontfile='{font}':textfile='{filter_path(label,p.ROOT)}':fontsize=30:fontcolor=white:box=1:boxcolor=0x15362c@0.7:boxborderw=10:x=(w-text_w)/2:y=h-125:enable='between(t,{scenes['discovery']['start']},{scenes['garden']['end']-3})'"]
            turn=out/'sua-vez.txt';turn.write_text('SUA VEZ!',encoding='utf-8')
            for c in timeline['dialogue']:
                if c.get('pause_after',0)>=3:
                    overlays.append(f"drawtext=fontfile='{font}':textfile='{filter_path(turn,p.ROOT)}':fontsize=40:fontcolor=0xFFE066:box=1:boxcolor=0x15362c@0.8:boxborderw=12:x=w-text_w-55:y=65:enable='between(t,{c['end']},{c['end']+c['pause_after']})'")
            cmd[index]+=','+','.join(overlays)
        original_run(cmd,log)
    original_fingerprint=p.fingerprint
    def fingerprint(*args):
        result=original_fingerprint(*args)
        result['files'].update({f.relative_to(p.ROOT).as_posix():p.sha(f) for f in list(Path(__file__).parent.glob('*.py'))+list((p.ROOT/'EPISODIO_04/ASSETS').glob('*.blend'))+[p.ROOT/'EPISODIO_04/validar_sincronismo.py',p.ROOT/'EPISODIO_04/validar_interacoes.py']})
        return result
    p.run=run;p.fingerprint=fingerprint
    from producao.serie import qualidade
    original_verify=qualidade.verify
    def verify(story,folder,timeline,width):
        import json
        report=original_verify(story,folder,timeline,width)
        run([sys.executable,'-m','producao.qa','--output',folder],folder/'motion-check.log')
        for script in ('validar_sincronismo.py','validar_interacoes.py'):
            run(['blender','-b',folder/'episodio_04_final.blend','-t','1','--python-exit-code','1','--python',p.ROOT/'EPISODIO_04'/script,'--',folder],folder/(script+'.log'))
        scene_sha=p.sha(folder/'episodio_04_final.blend')
        for name in ('motion-report.json','lip-sync-validation.json','interaction-validation.json'):
            proof=json.loads((folder/name).read_text());proof.update(video_sha256=report['sha256'],scene_sha256=scene_sha)
            (folder/name).write_text(json.dumps(proof,ensure_ascii=False,indent=2))
        report.update(scene_sha256=scene_sha,independent_checks='passed',proofs={n:p.sha(folder/n) for n in ('motion-report.json','lip-sync-validation.json','interaction-validation.json')})
        return report
    qualidade.verify=verify
    p.main()
