"""Compose original procedural music/SFX and mix preserved voice clips locally."""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

RATE = 44100


def decode(path):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1',
                                   '-ar', str(RATE), '-f', 'f32le', '-'])
    return np.frombuffer(raw, dtype='<f4').copy()


def write_wave(path, data):
    data = np.asarray(data)
    if data.ndim == 1:
        data = np.column_stack((data, data))
    if not np.isfinite(data).all():
        raise ValueError('Amostras inválidas no áudio')
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(data.shape[1]);f.setsampwidth(2);f.setframerate(RATE)
        f.writeframes((np.clip(data, -1, 1)*32767).astype('<i2').tobytes())


def synthesize(timeline, root, output):
    output = Path(output)
    n = round(timeline['duration']*RATE)
    music = np.zeros((n,2),np.float32)
    sfx = np.zeros_like(music)
    voice = np.zeros(n,np.float32)
    rng = np.random.default_rng(4101)

    def add(track, start, sound, gain=1, pan=0):
        at = round(start*RATE)
        if at<0 or at>=n:
            raise ValueError('Evento sonoro fora da timeline')
        sound = sound[:n-at]
        track[at:at+len(sound),0] += sound*gain*(1-pan*.4)
        track[at:at+len(sound),1] += sound*gain*(1+pan*.4)

    def note(midi, duration, kind='bell'):
        t = np.arange(round(duration*RATE))/RATE
        freq = 440*2**((midi-69)/12)
        if kind=='pad':
            a = np.minimum(t/.15,1)*np.minimum((duration-t)/.25,1)
            return ((np.sin(2*np.pi*freq*t)+.18*np.sin(4*np.pi*freq*t))*a*.12).astype(np.float32)
        a = (1-np.exp(-t*200))*np.exp(-t*(4 if kind=='bell' else 2))
        return ((np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*freq*2.003*t))*a*.3).astype(np.float32)

    beat = .6
    chords = [(48,52,55),(53,57,60),(45,48,52),(43,47,50)]
    # Seeded arpeggios, mathematical oscillators only: no external recordings or quoted songs.
    for bar, at in enumerate(np.arange(0,timeline['duration'],beat*4)):
        chord = chords[bar%4]
        for midi in chord:
            add(music,at,note(midi,2.5,'pad'),.36)
        for j in range(8):
            start=at+j*beat/2
            if start>=timeline['duration']: break
            midi=chord[(j+bar)%3]+12+(12 if rng.random()<.22 else 0)
            add(music,start,note(midi,.65),.24,(-1 if j%2 else 1)*.5)
        add(music,at,note(chord[0]-12,1.8,'pad'),.45)
    duck=np.ones(n,np.float32)
    for clip in timeline['dialogue']:
        audio=decode(Path(root)/clip['path'])
        peak=max(.01,float(np.max(np.abs(audio))))
        audio *= .72/peak
        at=round(clip['start']*RATE)
        if at+len(audio)>n:
            raise ValueError('Fala truncada no fim da timeline')
        voice[at:at+len(audio)]+=audio
        a=max(0,at-round(.15*RATE));b=min(n,at+len(audio)+round(.3*RATE))
        duck[a:b]=.3
    # Smooth music ducking so it never pumps at clip boundaries.
    kernel=np.ones(4410,np.float32)/4410
    # Cumulative sum makes the smoothing linear in episode duration.
    padded=np.pad(duck,(2205,2205),mode='edge')
    c=np.cumsum(padded,dtype=np.float64)
    duck=((c[4410:]-c[:-4410])/4410).astype(np.float32)[:n]
    music *= duck[:,None]
    e=timeline['events']
    # Planting: soft earthy thump, not a startling impact.
    noise=rng.normal(0,1,round(.35*RATE)).astype(np.float32)
    noise=np.convolve(noise,np.ones(90)/90,mode='same')
    add(sfx,e['plant_end']-.7,noise*np.exp(-np.arange(len(noise))/RATE*12),.65)
    # Water: short falling plinks and low-level filtered noise.
    for i,at in enumerate(np.arange(e['plant_end']+.3,e['plant_end']+3.5,.19)):
        add(sfx,at,note(83+(i%4)*2,.2),.14,.2)
    # Magic grows with an ascending C-major sparkle, resolved in a warm chord.
    for i,at in enumerate(np.arange(e['magic_start'],e['growth_end']+.6,.27)):
        add(sfx,at,note([72,76,79,84,88,91][i%6],.8),.20,np.sin(i)*.7)
    for midi in (60,64,67,72):
        add(sfx,e['growth_end'],note(midi,2,'pad'),.35)
    for midi,delay in [(72,0),(76,.2),(79,.4),(84,.6)]:
        add(sfx,e['goodbye']+.4+delay,note(midi,1.8),.20)
    # Tiny synthesized bird calls establish the clearing in pauses.
    for at in (1,7.8,e['plant_start']+.2,e['plant_end']+5.2):
        t=np.arange(int(.27*RATE))/RATE
        chirp=np.sin(2*np.pi*(1800*t+1700*t*t))*np.sin(np.pi*t/.27)**2
        add(sfx,at,chirp,.015,-.7)
    master=music+sfx+voice[:,None]
    fade_in=np.minimum(np.arange(n)/(RATE*.7),1)
    fade_out=np.minimum((n-1-np.arange(n))/(RATE*1.4),1)
    master*= (fade_in*fade_out)[:,None]
    peak=float(np.max(np.abs(master)))
    if peak>.94:master*=.94/peak
    write_wave(output/'musica_original.wav',music)
    write_wave(output/'efeitos_originais.wav',sfx)
    write_wave(output/'dialogos.wav',voice)
    write_wave(output/'mix_pre_master.wav',master)
    # EBU normalization with true-peak protection, then verify the encoded export too.
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(output/'mix_pre_master.wav'),
                    '-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar',str(RATE),
                    str(output/'master.wav')],check=True)
    (output/'audio-report.json').write_text(json.dumps(dict(
        duration=timeline['duration'],voices=len(timeline['dialogue']),
        pre_master_peak=peak,source_music='Osciladores e ruído procedural, seed 4101; sem samples externos',
        existing_music='Preservada; não utilizada por ausência de documentação de licença'),indent=2,ensure_ascii=False))


def subtitles(timeline, output):
    def stamp(t):
        ms=round(t*1000);s,ms=divmod(ms,1000);m,s=divmod(s,60);h,m=divmod(m,60)
        return f'{h:02}:{m:02}:{s:02},{ms:03}'
    parts=[]
    for i,c in enumerate(timeline['dialogue'],1):
        parts.append(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['speaker']}: {c['text']}\n")
    Path(output).write_text('\n'.join(parts),encoding='utf-8')
