"""Utilidades compartidas del kit de edición."""
import json, os, subprocess, sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
VIDEO_EXT = {'.mov', '.mp4', '.m4v', '.mkv'}
FOTO_EXT = {'.jpg', '.jpeg', '.png'}
W, H, FPS = 1080, 1920, 30
ROJO_ASS = '&H2C19D7&'          # rojo de marca (#D7192C) en formato BGR de ASS

GRADES = {
    # cálido de viaje: un poco más de contraste y saturación, sombras frías leves
    'calido': "eq=contrast=1.06:saturation=1.10:gamma=0.98,"
              "colorbalance=rs=0.03:bs=-0.03:rh=0.04:bh=-0.04,vignette=PI/6",
    # neutro: solo corrección suave
    'neutro': "eq=contrast=1.03:saturation=1.03",
    # noche: más contraste, sombras azuladas
    'noche':  "eq=contrast=1.10:saturation=0.95:gamma=0.95,"
              "colorbalance=bs=0.05:rs=-0.02:rh=0.05,vignette=PI/5",
    'ninguno': "null",
}

def run(cmd, **kw):
    print('$', ' '.join(str(c) for c in cmd)[:300], file=sys.stderr)
    subprocess.run([str(c) for c in cmd], check=True, **kw)

def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                          '-of', 'json', str(path)], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)

def duracion(path):
    return float(probe(path)['format']['duration'])

def tiene_audio(path):
    return any(s['codec_type'] == 'audio' for s in probe(path)['streams'])

def ts_ass(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def proyecto(argv):
    if len(argv) < 2:
        sys.exit(f"Uso: python3 {Path(argv[0]).name} <carpeta-del-vlog>")
    p = Path(argv[1]).expanduser().resolve()
    for d in ('trabajo', 'final'):
        (p / d).mkdir(exist_ok=True)
    return p

def leer_json(path, defecto=None):
    path = Path(path)
    if not path.exists():
        if defecto is None:
            sys.exit(f"Falta {path}")
        return defecto
    return json.loads(path.read_text())
