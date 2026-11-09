"""Paso 3. Monta el corte a partir de edl.json (lista de decisiones de edición).

Cada segmento: recorte del clip, encuadre 9:16 (1080x1920), color, zoom opcional
y audio = voz limpia (si existe en trabajo/limpio) + un poco de ambiente original.

Uso: python3 corte.py <carpeta-del-vlog>
Entrada: <vlog>/edl.json   (ver plantillas/proyecto/edl.json)
Salida: trabajo/corte.mp4
"""
import sys
from comun import *

p = proyecto(sys.argv)
edl = leer_json(p / 'edl.json')
grade_def = edl.get('grade', 'calido')
amb_def = edl.get('ambiente', 0.15)
segdir = p / 'trabajo' / 'segmentos'
segdir.mkdir(exist_ok=True)
for f in segdir.glob('*.mp4'):
    f.unlink()

def cadena_video(seg, dur):
    f = [f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}"]
    if seg.get('encuadre') in ('izq', 'der'):          # para planos horizontales: elegir lado
        x = '0' if seg['encuadre'] == 'izq' else 'in_w-out_w'
        f[1] = f"crop={W}:{H}:{x}:0"
    z = seg.get('zoom')
    if z == 'punch':                                   # golpe de zoom (énfasis)
        f += ["scale=iw*1.14:ih*1.14", f"crop={W}:{H}"]
    elif z in ('lento', 'lento-out'):                  # empuje lento a lo largo del plano
        a, b = (1.0, 1.10) if z == 'lento' else (1.10, 1.0)
        k = f"({a}+({b}-{a})*t/{dur:.3f})"
        f += [f"scale=w='trunc({W}*{k}/2)*2':h='trunc({H}*{k}/2)*2':eval=frame", f"crop={W}:{H}"]
    if seg.get('velocidad'):
        f.append(f"setpts=PTS/{seg['velocidad']}")
    f += [GRADES[seg.get('grade', grade_def)], f"fps={FPS}", "format=yuv420p", "setsar=1"]
    return ','.join(f)

for i, seg in enumerate(edl['segmentos']):
    src = p / 'crudo' / seg['clip']
    out = segdir / f"{i:03d}.mp4"
    es_foto = src.suffix.lower() in FOTO_EXT
    if es_foto:
        dur = float(seg.get('duracion', 2.5))
        seg.setdefault('zoom', 'lento')
        run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', dur, '-i', src,
             '-f', 'lavfi', '-t', dur, '-i', 'anullsrc=r=48000:cl=mono',
             '-filter_complex', f"[0:v]{cadena_video(seg, dur)}[v]",
             '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast',
             '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '1', '-t', dur, out])
        continue
    a, b = float(seg['in']), float(seg['out'])
    vel = float(seg.get('velocidad', 1))
    dur = (b - a) / vel
    limpio = p / 'trabajo' / 'limpio' / (src.stem + '.wav')
    amb = float(seg.get('ambiente', amb_def))
    vol = float(seg.get('volumen', 1.0))
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', a, '-to', b, '-i', src]
    fc = f"[0:v]{cadena_video(seg, dur)}[v];"
    tempo = f",atempo={vel}" if vel != 1 else ''
    if not tiene_audio(src) or seg.get('mudo'):
        cmd += ['-f', 'lavfi', '-t', dur, '-i', 'anullsrc=r=48000:cl=mono']
        fc += "[1:a]anull[a]"
    elif limpio.exists() and not seg.get('original'):
        cmd += ['-ss', a, '-to', b, '-i', limpio]
        fc += (f"[1:a]aresample=48000,volume={vol}{tempo}[vz];"
               f"[0:a]aresample=48000,pan=mono|c0=c0,highpass=f=120,volume={amb}{tempo}[am];"
               f"[vz][am]amix=inputs=2:normalize=0,afade=t=in:d=0.02,afade=t=out:st={max(dur-0.03,0):.3f}:d=0.03[a]")
    else:
        fc += (f"[0:a]aresample=48000,pan=mono|c0=c0,volume={vol}{tempo},"
               f"afade=t=in:d=0.02,afade=t=out:st={max(dur-0.03,0):.3f}:d=0.03[a]")
    cmd += ['-filter_complex', fc, '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-crf', '16', '-preset', 'fast',
            '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '1', '-t', f"{dur:.3f}", out]
    run(cmd)

lista = segdir / 'lista.txt'
lista.write_text(''.join(f"file '{f.name}'\n" for f in sorted(segdir.glob('*.mp4'))))
run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lista,
     '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', p / 'trabajo' / 'corte.mp4'])
print(f"✓ trabajo/corte.mp4  ({duracion(p / 'trabajo' / 'corte.mp4'):.1f} s, {len(edl['segmentos'])} segmentos)")
