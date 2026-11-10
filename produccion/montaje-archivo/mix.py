"""ALIAS · Prólogo — paso 2: concatena segmentos, quema subtítulos y mezcla audio (voz, archivo, sfx, camas)."""
import json, subprocess, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else 'renders/archivo.mp4'
T = json.load(open('timeline.json')); total = T['total']; fut = T['fut']; futlen = T['futlen']
SRC = {'DC': 'fuentes/DuckandC1951_edit.mp4', 'vo': 'vo/vo_n.wav', 'vo2': 'vo/l13_n.wav', 'vo3': 'vo/moderno_n.wav', 'JFK': 'jfk/jfk.mp3', 'CTA': 'vo/cta_n.wav'}
ins, fc, labels = ['-f', 'concat', '-safe', '0', '-i', 'seg/lista.txt'], [], []
k = 1


def add(path, extra=None):
    global k
    ins.extend((extra or []) + ['-i', path]); k += 1; return k - 1


for j, (s, a, d, off, vol) in enumerate(T['aud']):
    ms = int(off * 1000)
    if s in SRC:
        i = add(SRC[s]); filt = f"[{i}:a]atrim={a}:{a+d},asetpts=PTS-STARTPTS,aresample=48000,pan=mono|c0=c0"
        if s == 'DC': filt += ",adeclick,highpass=f=180,afftdn=nf=-30,lowpass=f=4500,acompressor,volume=1.3,afade=t=in:d=0.08,afade=t=out:st=%.2f:d=0.25" % max(d - .25, 0)
        elif s == 'JFK': filt += ",adeclick,highpass=f=250,afftdn=nf=-28,lowpass=f=3400,acompressor,volume=1.6,afade=t=in:d=0.06,afade=t=out:st=%.2f:d=0.2" % max(d - .2, 0)
        else: filt += ",deesser=i=0.4,volume=1.0,afade=t=in:d=0.03,afade=t=out:st=%.2f:d=0.06" % max(d - .06, 0)
    else:
        i = add(f'sfx/{s}.wav'); filt = f"[{i}:a]aresample=48000,pan=mono|c0=c0,volume={vol}"
        if s == 'cortinilla': filt += ",lowpass=f=1800,volume=0.6"
        if s in ('teletipo', 'estatica', 'hiss'): filt += ",atrim=0:8.0" if off < fut - 1 else ",atrim=0:%.2f,afade=t=in:d=1.5,afade=t=out:st=%.2f:d=0.8" % (futlen, futlen - 0.8)
    fc.append(f"{filt},adelay={ms}|{ms}[a{j}]"); labels.append(f"[a{j}]")
# camas: proyector hasta el bloque moderno (luego baja), dron creciente que no deja huecos
pi_ = add('sfx/proyector.wav'); fc.append(f"[{pi_}:a]atrim=0:{fut+futlen:.2f},lowpass=f=600,volume='if(lt(t,{fut:.2f}),0.6,0.6-0.35*min((t-{fut:.2f})/3,1))':eval=frame,afade=t=out:st={fut+futlen-2.0:.2f}:d=2[pr]"); labels.append('[pr]')
di = add('sfx/dron.wav'); fc.append(f"[{di}:a]atrim=0:{total:.2f},volume='if(lt(t,{fut+futlen:.1f}),0.25+0.75*t/{fut+futlen:.1f},0.45)':eval=frame,afade=t=out:st={total-1.2:.2f}:d=1.2[dr]"); labels.append('[dr]')
fc.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{total:.2f},highpass=f=40,lowpass=f=13000,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
fc.append("[0:v]ass=subs.ass[vout]")
cmd = ['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]', '-t', f'{total:.2f}',
       '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', OUT]
subprocess.run(cmd, check=True); print('ok', total, OUT)
