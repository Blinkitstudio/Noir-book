"""Paso 5. Render final: quema subtítulos, mezcla música (con ducking bajo la voz)
y efectos, y normaliza a -14 LUFS (estándar de Instagram/TikTok).

Uso: python3 mezcla.py <carpeta-del-vlog>
Entrada: trabajo/corte.mp4, trabajo/subs.ass, <vlog>/mezcla.json (opcional)
Salida: final/<nombre-del-vlog>.mp4

mezcla.json:
  musica  {"archivo": "ruta.mp3", "volumen": 0.25, "inicio": 0, "ducking": true}
  sfx     [{"t": 0.0, "tipo": "whoosh", "vol": 0.5}, ...]
          tipo = nombre de kit/sfx/*.wav o ruta a un archivo propio
  lufs    -14 por defecto
"""
import sys
from pathlib import Path
from comun import *

p = proyecto(sys.argv)
cfg = leer_json(p / 'mezcla.json', {})
corte = p / 'trabajo' / 'corte.mp4'
subs = p / 'trabajo' / 'subs.ass'
dur = duracion(corte)
salida = p / 'final' / f"{p.name}.mp4"

ins = ['-i', corte]
fc = []
vf = f"ass='{subs}'" if subs.exists() else 'null'
fc.append(f"[0:v]{vf}[v]")
fc.append("[0:a]aresample=48000,asplit=2[voz][vozsc]")
pistas = ['[voz]']
n = 1
mus = cfg.get('musica')
if mus and mus.get('archivo'):
    ruta = Path(mus['archivo']).expanduser()
    if not ruta.is_absolute():
        ruta = p / ruta
    ins += ['-stream_loop', '-1', '-ss', str(mus.get('inicio', 0)), '-i', ruta]
    fc.append(f"[{n}:a]aresample=48000,volume={mus.get('volumen', 0.25)},"
              f"afade=t=in:d=0.5,afade=t=out:st={max(dur-1.5,0):.2f}:d=1.5[m0]")
    if mus.get('ducking', True):
        fc.append("[m0][vozsc]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[mus]")
    else:
        fc.append("[m0]anull[mus]"); fc.append("[vozsc]anullsink")
    pistas.append('[mus]')
    n += 1
else:
    fc.append("[vozsc]anullsink")
for k, s in enumerate(cfg.get('sfx', [])):
    ruta = Path(s['tipo']).expanduser()
    if not ruta.exists():
        ruta = KIT / 'sfx' / f"{s['tipo']}.wav"
    ins += ['-i', ruta]
    ms = int(float(s['t']) * 1000)
    fc.append(f"[{n}:a]aresample=48000,volume={s.get('vol', 0.5)},adelay={ms}|{ms}[s{k}]")
    pistas.append(f"[s{k}]")
    n += 1
lufs = cfg.get('lufs', -14)
fc.append(f"{''.join(pistas)}amix=inputs={len(pistas)}:normalize=0:duration=first,"
          f"atrim=0:{dur:.3f},loudnorm=I={lufs}:TP=-1.5:LRA=11[a]")
run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc),
     '-map', '[v]', '-map', '[a]', '-t', f"{dur:.3f}",
     '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p',
     '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', salida])

# segunda pasada: medir y corregir el volumen para clavar los LUFS (el video se copia)
import json, re, subprocess
med = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(salida), '-af',
                      f'loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
m = json.loads(re.findall(r'\{[^{}]*\}', med)[-1])
if abs(float(m['input_i']) - lufs) > 0.5:
    tmp = salida.with_suffix('.tmp.mp4')
    af = (f"loudnorm=I={lufs}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
          f"offset={m['target_offset']}:linear=true,aresample=48000")
    run(['ffmpeg', '-v', 'error', '-y', '-i', salida, '-c:v', 'copy', '-af', af,
         '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', tmp])
    tmp.replace(salida)
print(f"✓ {salida}  ({dur:.1f} s)")
