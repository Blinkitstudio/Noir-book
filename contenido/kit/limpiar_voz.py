"""Paso 2. Limpia la voz de cada clip con el Voice Isolator de ElevenLabs.

Requiere la variable de entorno ELEVENLABS_API_KEY (cuenta de Raúl).
Sin clave, usa un filtro de ruido local (afftdn), más básico pero gratis.

Uso: python3 limpiar_voz.py <carpeta-del-vlog> [clip1 clip2 ...]
Salida: trabajo/limpio/<clip>.wav   (corte.py lo usa automáticamente)
"""
import os, sys, subprocess
from comun import *

p = proyecto(sys.argv[:2])
solo = set(sys.argv[2:])
aud = p / 'trabajo' / 'audio'
out = p / 'trabajo' / 'limpio'
out.mkdir(exist_ok=True)
key = os.environ.get('ELEVENLABS_API_KEY')
if not key:
    print("! Sin ELEVENLABS_API_KEY: uso afftdn local (calidad menor).", file=sys.stderr)

for wav in sorted(aud.glob('*.wav')):
    if solo and wav.stem not in solo and wav.stem + wav.suffix not in solo:
        continue
    dst = out / wav.name
    if dst.exists():
        continue
    if key:
        mp3 = out / (wav.stem + '.eleven.mp3')
        # el endpoint acepta hasta ~500 MB / 1 h; los clips de iPhone entran sobrados
        r = subprocess.run(['curl', '-sS', '-f', '-X', 'POST',
                            'https://api.elevenlabs.io/v1/audio-isolation',
                            '-H', f'xi-api-key: {key}',
                            '-F', f'audio=@{wav}', '-o', str(mp3)])
        if r.returncode == 0 and mp3.exists() and mp3.stat().st_size > 1000:
            # vuelve a 48 kHz mono y alinea la duración con el original (pad/trim)
            d = duracion(wav)
            run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af', f'apad,atrim=0:{d}',
                 '-ac', '1', '-ar', '48000', dst])
            mp3.unlink()
            print(f"✓ {wav.name} (ElevenLabs)")
            continue
        print(f"! ElevenLabs falló con {wav.name}; uso afftdn", file=sys.stderr)
    run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-af',
         'highpass=f=90,afftdn=nf=-25:tn=1,lowpass=f=12000', dst])
    print(f"✓ {wav.name} (afftdn)")
