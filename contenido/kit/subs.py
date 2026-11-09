"""Paso 4. Subtítulos palabra por palabra + textos grandes, en el estilo de Raúl.

Uso: python3 subs.py <carpeta-del-vlog>
Entrada: trabajo/palabras_corte.json (de transcribir.py --corte) y <vlog>/textos.json
Salida: trabajo/subs.ass

textos.json (todo opcional, ver plantillas/proyecto/textos.json):
  rojas        palabras que salen en rojo (comparación sin tildes ni signos)
  correcciones {"frase mal": "frase bien"} errores de la transcripción
  ocultar      [[inicio, fin], ...] tramos sin subtítulos (cuando hay un texto grande)
  textos       [{s, e, txt, estilo: big|label|stamp, y, fs, color: blanco|rojo|gris}]
  subtitulos   false para no ponerlos (vlogs con mucho ambiente, por ejemplo)
"""
import json, sys, unicodedata
from comun import *

p = proyecto(sys.argv)
cfg = leer_json(p / 'textos.json', {})
W_ = leer_json(p / 'trabajo' / 'palabras_corte.json', []) if cfg.get('subtitulos', True) else []

def norm(t):
    t = unicodedata.normalize('NFD', t.lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').strip('.,¿?¡!:;"\'()')

# correcciones de frases (pueden abarcar varias palabras)
for mal, bien in cfg.get('correcciones', {}).items():
    m = mal.split(); b = bien.split()
    i = 0
    while i <= len(W_) - len(m):
        if [norm(x['w']) for x in W_[i:i+len(m)]] == [norm(x) for x in m]:
            grupo = W_[i:i+len(m)]
            nuevo = [{'w': b[k] if k < len(b) else '', 's': grupo[min(k, len(grupo)-1)]['s'],
                      'e': grupo[min(k, len(grupo)-1)]['e']} for k in range(max(len(b), 1))]
            if len(b) < len(m):
                nuevo[-1]['e'] = grupo[-1]['e']
            W_[i:i+len(m)] = [x for x in nuevo if x['w']]
            i += len(b)
        else:
            i += 1

rojas = {norm(x) for x in cfg.get('rojas', [])}
ocultar = cfg.get('ocultar', [])
COL = {'blanco': '&HFFFFFF&', 'rojo': ROJO_ASS, 'gris': '&HC8C8C8&'}
ev = []
for i, w in enumerate(W_):
    s = w['s']
    e = W_[i+1]['s'] if i + 1 < len(W_) else w['e'] + 0.6
    e = min(max(e, s + 0.12), s + 0.9)
    if any(a <= s < b for a, b in ocultar):
        continue
    col = f"\\c{ROJO_ASS}" if norm(w['w']) in rojas else ''
    txt = w['w'].upper().strip(',;')
    ev.append(f"Dialogue: 5,{ts_ass(s)},{ts_ass(e)},Cap,,0,0,0,,{{\\an5\\pos(540,1520)\\fad(30,0)"
              f"\\t(0,90,\\fscx108\\fscy108)\\t(90,160,\\fscx100\\fscy100){col}}}{txt}")

for t in cfg.get('textos', []):
    est = t.get('estilo', 'big')
    s, e = t['s'], t['e']
    txt = t['txt'].replace('\n', '\\N')
    col = COL.get(t.get('color', 'blanco'), t.get('color'))
    if est == 'big':
        ev.append(f"Dialogue: 3,{ts_ass(s)},{ts_ass(e)},Big,,0,0,0,,{{\\an5\\pos(540,{t.get('y', 860)})"
                  f"\\fs{t.get('fs', 120)}\\c{col}\\fad(60,80)\\fscx80\\fscy80\\t(0,140,\\fscx100\\fscy100)}}{txt}")
    elif est == 'label':
        ev.append(f"Dialogue: 4,{ts_ass(s)},{ts_ass(e)},Label,,0,0,0,,{{\\an8\\pos(540,{t.get('y', 330)})\\fad(80,80)}}{txt}")
    elif est == 'stamp':
        ev.append(f"Dialogue: 4,{ts_ass(s)},{ts_ass(e)},Stamp,,0,0,0,,{{\\an5\\pos(540,{t.get('y', 1000)})"
                  f"\\fs{t.get('fs', 110)}\\frz{t.get('giro', 6)}\\fscx150\\fscy150\\t(0,120,\\fscx100\\fscy100)}}{txt}")

ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3.5,2,5,60,60,0,1
Style: Big,Montserrat ExtraBold,120,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,-1,0,1,0,3,5,40,40,0,1
Style: Label,Montserrat ExtraBold,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,2,8,40,40,0,1
Style: Stamp,Montserrat ExtraBold,110,&H00FFFFFF,&H00FFFFFF,&H002C19D7,&H00000000,0,0,0,0,100,100,6,0,3,16,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
(p / 'trabajo' / 'subs.ass').write_text(ASS + '\n'.join(ev) + '\n')
print(f"✓ trabajo/subs.ass  ({len(ev)} eventos)")
