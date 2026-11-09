"""Transcribe con marcas de tiempo por palabra (faster-whisper, local).

Uso:
  python3 transcribir.py <carpeta-del-vlog>            → todos los clips (trabajo/audio o limpio)
  python3 transcribir.py <carpeta-del-vlog> --corte    → el corte ya montado (para subtítulos)
Salida: trabajo/transcripciones/<clip>.json y .txt  |  trabajo/palabras_corte.json
Modelo: WHISPER_MODEL=small (rápido) | medium (mejor, por defecto) | large-v3
"""
import json, os, sys
from comun import *
from faster_whisper import WhisperModel

p = proyecto(sys.argv[:2])
modelo = WhisperModel(os.environ.get('WHISPER_MODEL', 'medium'), device='cpu', compute_type='int8')

def transcribir(src):
    segs, _ = modelo.transcribe(str(src), language='es', word_timestamps=True,
                                vad_filter=True, beam_size=5)
    palabras, lineas = [], []
    for s in segs:
        lineas.append(f"[{s.start:7.2f}–{s.end:7.2f}] {s.text.strip()}")
        for w in s.words:
            palabras.append({'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)})
    return palabras, lineas

if '--corte' in sys.argv:
    src = p / 'trabajo' / 'corte.mp4'
    w, l = transcribir(src)
    (p / 'trabajo' / 'palabras_corte.json').write_text(json.dumps(w, ensure_ascii=False, indent=0))
    (p / 'trabajo' / 'corte.txt').write_text('\n'.join(l))
    print(f"{len(w)} palabras → trabajo/palabras_corte.json")
else:
    dst = p / 'trabajo' / 'transcripciones'
    dst.mkdir(exist_ok=True)
    limpio = p / 'trabajo' / 'limpio'
    for wav in sorted((p / 'trabajo' / 'audio').glob('*.wav')):
        if (dst / (wav.stem + '.json')).exists():
            continue
        src = limpio / wav.name if (limpio / wav.name).exists() else wav
        w, l = transcribir(src)
        (dst / (wav.stem + '.json')).write_text(json.dumps(w, ensure_ascii=False, indent=0))
        (dst / (wav.stem + '.txt')).write_text('\n'.join(l))
        print(f"✓ {wav.stem}: {len(w)} palabras")
