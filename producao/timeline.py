"""Relógio comum para vozes, animação, efeitos e legendas (12 fps)."""
import array
import hashlib
import json
import math
import subprocess
from pathlib import Path

FPS = 12
LINES = [
    ('NARRADORA', 'Em uma clareira encantada, três amiguinhos estavam prestes a viver uma aventura maravilhosa!'),
    ('CAPI', 'Uau! Olhem o que encontrei! Uma sementinha brilhante!'),
    ('TECO', 'Ebaaa! Será que ela vira uma árvore gigante?'),
    ('MAYA', 'Vamos descobrir juntos!'),
    ('CAPI', 'O que precisamos fazer?'),
    ('MAYA', 'Toda plantinha precisa de água, luz do sol e cuidado!'),
    ('TECO', 'Então vamos cuidar dela!'),
    ('NARRADORA', 'De repente, uma luz colorida iluminou toda a clareira!'),
    ('TECO', 'Uauuu! Está crescendo!'),
    ('CAPI', 'Conseguimos!'),
    ('MAYA', 'Quando cuidamos da natureza, coisas maravilhosas acontecem!'),
    ('NARRADORA', 'E assim nossos amigos descobriram que as pequenas coisas precisam de muito carinho!'),
]


def frame_at(seconds):
    return round(seconds * FPS) + 1


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)
    ]))


def build_timeline(root):
    root = Path(root)
    voices = root / 'EPISODIO_01/VOZES'
    clips = sorted(voices.glob('cena_*.mp3'))
    if len(clips) != 12:
        raise FileNotFoundError(f'Esperadas 12 falas em {voices}; encontradas {len(clips)}')
    dialogue, cursor, events = [], 2.0, {}
    for i, (path, (speaker, text)) in enumerate(zip(clips, LINES)):
        if speaker.lower() not in path.stem:
            raise ValueError(f'Personagem fora de ordem: {path.name}')
        duration = float(probe(path)['format']['duration'])
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path),
                                      '-ac', '1', '-ar', '12000', '-f', 's16le', '-'])
        samples = array.array('h', raw)
        rms = [math.sqrt(sum(v * v for v in samples[j:j+1000]) / max(1, len(samples[j:j+1000]))) / 32768
               for j in range(0, len(samples), 1000)]
        peak = max(rms, default=1) or 1
        envelope = [round(min(1, v / peak), 4) for v in rms]
        dialogue.append(dict(path=str(path.relative_to(root)), speaker=speaker,
                             text=text, start=round(cursor, 4), end=round(cursor + duration, 4),
                             envelope=envelope))
        cursor += duration + .6
        if i == 6:
            events['plant_start'] = cursor
            events['plant_end'] = cursor + 4
            events['care_end'] = cursor + 12
            cursor += 12
        if i == 7:
            events['magic_start'] = dialogue[-1]['start']
            events['growth_start'] = dialogue[-1]['end'] - .5
        if i == 8:
            events['growth_end'] = dialogue[-1]['end']
    events['goodbye'] = dialogue[-1]['end'] + .5
    # Whole frames, at least five seconds after the last spoken line.
    frames = math.ceil((dialogue[-1]['end'] + 5.5) * FPS)
    return dict(fps=FPS, frames=frames, duration=frames / FPS,
                dialogue=dialogue, events=events)


def write_timeline(root, output):
    timeline = build_timeline(root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'timeline.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=2))
    return timeline


def source_hashes(root):
    """Original inputs only; deliberately exclude all generated production files."""
    paths = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-r', '--name-only',
                                     'ba4eeeedbe0555e1c3d9acb2a42bef080ef3aaf4']).decode().splitlines()
    return {p: hashlib.sha256((Path(root) / p).read_bytes()).hexdigest() for p in paths}
