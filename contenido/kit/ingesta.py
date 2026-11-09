"""Paso 1. Inventario del material crudo, ordenado por hora de grabación,
y extracción del audio de cada clip (wav 48 kHz mono) para limpiar y transcribir.

Uso: python3 ingesta.py ~/Movies/Vlogs/2026-11-12_tema
Salida: trabajo/inventario.json, trabajo/audio/<clip>.wav
"""
import json, sys
from comun import *

p = proyecto(sys.argv)
crudo = p / 'crudo'
if not crudo.exists():
    sys.exit(f"No existe {crudo}. Pon el material en crudo/.")
(p / 'trabajo' / 'audio').mkdir(exist_ok=True)

items = []
for f in sorted(crudo.iterdir()):
    ext = f.suffix.lower()
    if ext in FOTO_EXT:
        items.append({'archivo': f.name, 'tipo': 'foto'})
        continue
    if ext not in VIDEO_EXT:
        if ext == '.heic':
            print(f"! {f.name}: HEIC no se lee directo. Conviértelo a JPG (sips -s format jpeg).", file=sys.stderr)
        continue
    info = probe(f)
    v = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    tags = info['format'].get('tags', {})
    fecha = (tags.get('com.apple.quicktime.creationdate') or tags.get('creation_time') or '')
    rot = 0
    for sd in (v or {}).get('side_data_list', []):
        rot = int(sd.get('rotation', 0) or 0)
    w, h = (v['width'], v['height']) if v else (0, 0)
    if abs(rot) == 90:
        w, h = h, w
    it = {'archivo': f.name, 'tipo': 'video', 'fecha': fecha,
          'duracion': round(float(info['format']['duration']), 2),
          'resolucion': f"{w}x{h}", 'vertical': h > w,
          'fps': v.get('avg_frame_rate') if v else None,
          'audio': tiene_audio(f)}
    if it['audio']:
        wav = p / 'trabajo' / 'audio' / (f.stem + '.wav')
        if not wav.exists():
            run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vn', '-ac', '1', '-ar', '48000', wav])
    items.append(it)

items.sort(key=lambda x: (x.get('fecha') or '9999', x['archivo']))
(p / 'trabajo' / 'inventario.json').write_text(json.dumps(items, indent=2, ensure_ascii=False))
total = sum(i.get('duracion', 0) for i in items)
print(f"{len(items)} archivos, {total/60:.1f} min de video → trabajo/inventario.json")
for i in items:
    print(f"  {i['archivo']:<22} {i['tipo']:<5} {i.get('duracion','')!s:>7}s {i.get('resolucion','')} {i.get('fecha','')}")
