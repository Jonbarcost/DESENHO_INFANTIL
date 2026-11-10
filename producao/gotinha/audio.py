"""Original generated music and nature effects, with no licensed sample dependency."""
import json
import subprocess
from pathlib import Path

import numpy as np

from producao.som import RATE, decode, subtitles, write_wave
from producao.serie.historia import require_final


def compose(timeline,root,out,with_dialogue=True):
    if with_dialogue:require_final(timeline)
    out=Path(out);n=round(timeline['duration']*RATE);rng=np.random.default_rng(42026)
    music=np.zeros((n,2),np.float32);fx=np.zeros_like(music);voice=np.zeros(n,np.float32)

    def add(track,time,a,gain=1,pan=0):
        at=round(time*RATE)
        if at>=n:return
        if at<0:raise ValueError('Evento antes do início')
        a=a[:n-at]
        track[at:at+len(a),0]+=a*gain*(1-pan*.4)
        track[at:at+len(a),1]+=a*gain*(1+pan*.4)

    def note(midi,duration,bell=True):
        t=np.arange(round(duration*RATE))/RATE;f=440*2**((midi-69)/12)
        env=(1-np.exp(-t*100))*np.exp(-t*(5 if bell else 1.5))
        env*=np.minimum((duration-t)/.1,1)
        return ((np.sin(2*np.pi*f*t)+.15*np.sin(2*np.pi*f*2.002*t))*env).astype(np.float32)

    beat=60/112;chords=[(60,64,67),(65,69,72),(57,60,64),(55,59,62)]
    for i,at in enumerate(np.arange(0,timeline['duration'],beat*4)):
        c=chords[(i//2)%4]
        for midi in c:add(music,at,note(midi,2.0,False),.022)
        for j in range(8):
            add(music,at+j*beat/2,note(c[(j+i)%3]+12+(12 if rng.random()<.12 else 0),.65),.032,(-1 if j%2 else 1)*.5)
        add(music,at,note(c[0]-12,1.3,False),.026)
    # Gentle acoustic-style pulse and hand percussion, synthesized from scratch.
    for i,at in enumerate(np.arange(0,timeline['duration'],beat)):
        u=np.arange(int(.16*RATE))/RATE
        kick=np.sin(2*np.pi*(105*u-110*u*u))*np.exp(-u*24)
        shaker=rng.normal(0,1,len(u))*np.exp(-u*65)
        add(music,at,kick,.015)
        if i%2:add(music,at,shaker,.004,.35)
    # Gentle smoothed wind, mathematical noise, no outside recordings.
    noise=rng.normal(0,1,n+500).astype(np.float32);c=np.cumsum(noise,dtype=np.float64)
    wind=((c[500:]-c[:-500])/500).astype(np.float32)
    fx[:,0]+=wind*.025;fx[:,1]+=wind*.022
    for i,at in enumerate(np.arange(4,timeline['duration']-2,8.7)):
        t=np.arange(int(.32*RATE))/RATE
        chirp=np.sin(2*np.pi*(1800*t+2200*t*t))*np.sin(np.pi*t/.32)**2
        add(fx,at,chirp.astype(np.float32),.012,np.sin(i)*.6)
    scenes={s['mode']:s for s in timeline['scenes']}
    for mode in ('discovery','chase','investigate','finale'):
        for j,midi in enumerate([79,83,86]):add(fx,scenes[mode]['start']+1+j*.15,note(midi,.65),.022)
    rain=scenes['garden']
    for i,at in enumerate(np.arange(rain['start']+2,rain['end']-2,.38)):
        u=np.arange(int(.12*RATE))/RATE
        ping=np.sin(2*np.pi*(1150*u-1400*u*u))*np.exp(-u*40)
        add(fx,at,ping,.010,float(np.sin(i*1.7))*.8)
    for line in timeline['dialogue']:
        if line.get('event')=='rain_game':
            for at in np.arange(line['end'],line['end']+line.get('pause_after',.8)-.1,.28):add(fx,at,note(86,.12),.012)
    duck=np.ones(n,np.float32)
    reports=[]
    if with_dialogue:
        for clip in timeline['dialogue']:
            a=decode(Path(root)/clip['path']);a*=.72/max(.001,float(np.max(np.abs(a))))
            start=round(clip['start']*RATE);end=start+len(a)
            if end>n:raise ValueError('Fala truncada')
            voice[start:end]+=a
            duck[max(0,start-5000):min(n,end+10000)]=.22
        padded=np.pad(duck,(2205,2205),mode='edge');c=np.cumsum(padded,dtype=np.float64)
        duck=((c[4410:]-c[:-4410])/4410).astype(np.float32)[:n]
        music*=duck[:,None]
        for clip in timeline['dialogue']:
            a,b=round(clip['start']*RATE),round(clip['end']*RATE)
            vr=float(np.sqrt(np.mean(voice[a:b]**2)))
            br=float(np.sqrt(np.mean((music[a:b]+fx[a:b])**2)))
            if vr<=.0001:raise ValueError('Fala sem energia audível')
            ratio=20*np.log10(vr/max(br,1e-8))
            if ratio<12:
                k=10**((ratio-12)/20);music[a:b]*=k;fx[a:b]*=k;ratio=12
            reports.append(dict(id=clip['id'],voice_background_db=round(float(ratio),2)))
    fade=np.minimum(np.arange(n)/(RATE*1.5),1)*np.minimum((n-1-np.arange(n))/(RATE*2),1)
    music*=fade[:,None];fx*=fade[:,None]
    write_wave(out/'musica_original.wav',music);write_wave(out/'efeitos_natureza.wav',fx)
    if with_dialogue:
        write_wave(out/'dialogos.wav',voice)
        mix=voice[:,None]+music+fx;mix*=min(1,.94/max(.001,float(np.max(np.abs(mix)))))
        write_wave(out/'mix_pre_master.wav',mix)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(out/'mix_pre_master.wav'),
                        '-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar',str(RATE),str(out/'master.wav')],check=True)
        subtitles(timeline,out/'legendas.srt')
    (out/'audio-report.json').write_text(json.dumps(dict(provisional=timeline['provisional'],
       dialogue_included=with_dialogue,speech_background=reports,source='Original 112 BPM major-key theme, plucked oscillators, synthesized percussion/rain/birds; no external samples'),indent=2))
