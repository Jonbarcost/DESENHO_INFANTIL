"""Episode 03 adapters; validated Episode 02 source remains unchanged."""
from pathlib import Path
import sys,os
from producao.serie import pipeline as p

def main():
    # Parse exactly as argparse, including --output=path and abbreviations.
    import argparse
    guard=argparse.ArgumentParser(add_help=False)
    guard.add_argument('story',type=Path);guard.add_argument('--output',type=Path)
    args,_=guard.parse_known_args()
    story=p.load_story(args.story)
    if story['episode']!='03':raise SystemExit('Este adaptador produz somente o Episódio 03')
    out=(args.output or args.story.resolve().parent.parent/'ARTEFATOS').resolve()
    for protected in (p.ROOT/'EPISODIO_01',p.ROOT/'EPISODIO_02',p.ROOT/'build/episodio_01'):
        if out==protected or protected in out.parents:
            raise SystemExit('Saída protegida: episódios anteriores são somente leitura')
    from producao.serie import audio
    from .audio import compose
    audio.compose=compose
    original_run=p.run
    def run(cmd,log):
        cmd=[str(x).replace('producao/serie/cena.py','producao/riacho/cena.py').replace('producao/serie/qa_cena.py','producao/riacho/qa_cena.py') for x in cmd]
        original_run(cmd,log)
    original_fingerprint=p.fingerprint
    def fingerprint(*args):
        result=original_fingerprint(*args)
        result['files'].update({f.relative_to(p.ROOT).as_posix():p.sha(f) for f in Path(__file__).parent.glob('*.py')})
        return result
    p.run=run;p.fingerprint=fingerprint
    p.main()
