"""ALIAS · Making of (reel 9:16) presentado por Raúl con su voz de IA.
Uso: python3 mk.py   (en la carpeta de trabajo del documental; voces en vo/m01..m06_n.wav y vo/b11_n.wav)
"""
import json, os, re, subprocess, unicodedata
from PIL import Image

W, H, FPS = 1080, 1920, 30
BOXW, BOXH = 1080, 1380
SH = '/home/user/alias/shots/'
ART = 'arte/'
OUT = 'out_mk'
os.makedirs(f'{OUT}/seg', exist_ok=True)
GRADE = "eq=contrast=1.05:saturation=0.9,noise=alls=6:allf=t+u,vignette=PI/5"


def run(c): subprocess.run(c, shell=True, check=True)
def dur(f): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
def norm(s): return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode())


IMG = {
    'env': ('exec-06a1bc6a-48a3-4609-a1cd-8f45b6a02ad7.jpg', (0, 40, 720, 1000)),
    'nodo': ('exec-ba7ed8fc-ae95-487f-a263-1394df428a85.jpg', (0, 40, 760, 1000)),
    'env_full': ('exec-06a1bc6a-48a3-4609-a1cd-8f45b6a02ad7.jpg', (0, 0, 1500, 1000)),
    'nodo_full': ('exec-ba7ed8fc-ae95-487f-a263-1394df428a85.jpg', (0, 0, 1500, 1000)),
    'cont_full': ('exec-0f0a39fc-29a3-4067-8882-c6bbaed85dbd.jpg', (0, 0, 1500, 1000)),
    'c7': ('exec-f556e27e-8f38-4f3a-8964-a0b82e030b86.jpg', (0, 60, 1500, 640)),
    'tres_all': ('exec-5639548b-a231-409e-a88e-adfef7c2b56d.jpg', (0, 30, 1500, 1000)),
    'soldado': ('exec-94e1e2c6-83d7-4845-b94d-260d9b434e92.jpg', (0, 40, 760, 1000)),
    'collage': (None, None),
    'nuar3': ('exec-3909b2a1-a84a-48c0-9081-4166ca7eac29.jpg', (0, 40, 820, 1000)),
    'exo': ('nuar-exoesqueleto-campo-2237.jpg', (0, 80, 1230, 1560)),
}


def fit(w, h):
    s = min(BOXW / w, BOXH / h)
    return int(w * s) // 2 * 2, int(h * s) // 2 * 2


def fades(d, fi, fo): return (",fade=t=in:st=0:d=0.3" if fi else "") + (f",fade=t=out:st={d-0.4:.2f}:d=0.4" if fo else "")


def seg_video(path, start, d, out, fi, fo):
    sd = dur(path) - start
    speed = min(max(d / sd, 1.0), 1.7)
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.split(','))
    fw, fh = fit(w, h)
    fc = (f"[0:v]setpts={speed:.3f}*(PTS-STARTPTS),fps={FPS},split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:2,eq=brightness=-0.18:saturation=0.7[bg];"
          f"[b]scale={fw}:{fh}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,{GRADE},tpad=stop_mode=clone:stop_duration=4,trim=0:{d:.3f},setpts=PTS-STARTPTS{fades(d, fi, fo)},format=yuv420p[v]")
    run(f'ffmpeg -v error -y -ss {start} -i "{path}" -filter_complex "{fc}" -map "[v]" -an -t {d:.3f} -r {FPS} -c:v libx264 -crf 18 -preset fast {out}')


def collage():
    fs = ['exec-06a1bc6a-48a3-4609-a1cd-8f45b6a02ad7.jpg', 'exec-ba7ed8fc-ae95-487f-a263-1394df428a85.jpg', 'exec-0f0a39fc-29a3-4067-8882-c6bbaed85dbd.jpg',
          'exec-2cf7700e-aef3-428d-b065-692c036d097f.jpg', 'exec-f556e27e-8f38-4f3a-8964-a0b82e030b86.jpg', 'exec-5639548b-a231-409e-a88e-adfef7c2b56d.jpg',
          'exec-94e1e2c6-83d7-4845-b94d-260d9b434e92.jpg', 'nuar-exoesqueleto-campo-2237.jpg']
    cw, chh, g = 700, 466, 16
    im = Image.new('RGB', (2 * cw + 3 * g, 4 * chh + 5 * g), (12, 12, 12))
    for i, f in enumerate(fs):
        t = Image.open(ART + f).convert('RGB'); t = t.resize((cw, int(t.height * cw / t.width))).crop((0, 0, cw, chh))
        im.paste(t, (g + (i % 2) * (cw + g), g + (i // 2) * (chh + g)))
    return im


def seg_image(key, d, out, fi, fo, k):
    f, box = IMG[key]
    im = collage() if key == 'collage' else Image.open(ART + f).convert('RGB').crop(box)
    fw, fh = fit(*im.size)
    zw, zh = int(fw * 1.10) // 2 * 2, int(fh * 1.10) // 2 * 2
    im.resize((zw, zh), Image.LANCZOS).save(f'{OUT}/tmp_{key}.png'); im.save(f'{OUT}/tmp_{key}_bg.png')
    dx, dy = zw - fw, zh - fh
    x = f"{dx}*t/{d:.3f}" if k % 2 == 0 else f"{dx}*(1-t/{d:.3f})"
    y = f"{dy}*t/{d:.3f}" if key in ('env', 'nodo', 'soldado', 'collage', 'exo') else f"{dy}*0.5"
    fc = (f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:2,eq=brightness=-0.2:saturation=0.7[bg];"
          f"[0:v]crop={fw}:{fh}:'{x}':'{y}'[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,{GRADE}{fades(d, fi, fo)},format=yuv420p[v]")
    run(f'ffmpeg -v error -y -loop 1 -framerate {FPS} -t {d:.3f} -i {OUT}/tmp_{key}.png -loop 1 -framerate {FPS} -t {d:.3f} -i {OUT}/tmp_{key}_bg.png '
        f'-filter_complex "{fc}" -map "[v]" -t {d:.3f} -r {FPS} -c:v libx264 -crf 18 -preset fast {out}')


MOD = '/home/user/alias-archivo/moderno/'
VO = {
    1: ['Este es Nuar...', 'Tiene mi cara. Mi voz.', 'Y vive en el año 2237.'],
    2: ['Cuando veo las noticias...', 'Europa pidiendo a la gente que guarde comida para tres días.', 'Apagones.', 'Protestas.',
        'Y una carrera entre Estados Unidos, China y Rusia por los chips y los centros de datos.', 'Es difícil no imaginar cómo termina.'],
    3: ['Yo vivo en Argentina, en el Cono Sur.', 'Y todo empezó probando modelos de inteligencia artificial...', 'creé uno idéntico a mí.', 'Eso me hizo pensar en los remanentes.', 'En lo que queda de nosotros.'],
    4: ['Pero ALIAS no va tanto de la guerra.', 'Va de lo que viene después: la memoria.', 'Nuar va por su tercera vida...', 'y recuerda a una mujer,', 'pero no el nombre del hombre que la amaba.'],
    5: ['Para la historia tomé mucho de Fallout, Blade Runner, Ghost in the Shell, Matrix, Stalker, Edge of Tomorrow.', 'Y para contarla... de Terminator 3, Soy leyenda, The Last of Us.'],
    6: ['Las máquinas las fui diseñando por épocas.', 'La Envoltura, cuerpos sin género.', 'El Nodo, que cada vez se parece menos a nosotros.', 'El Contorno, que carga lo que nadie más carga.', 'Y el Austral y el Aguja, de la guerra en la Antártida.'],
    7: ['Todo lo hago con inteligencia artificial.', 'Y eso también es parte de la pregunta...', 'porque hasta esta voz es una copia de la mía.'],
}
# (plano, palabra donde empieza, etiqueta (rojo, blanco) o None). Material real sin rótulos de lugar ni fecha.
SHOTS = {
    1: [(('v', 'anim/a_rostro.mp4', 0), None, None)],
    2: [(('v', MOD + 'costco.src', 20.0), 'europa', None), (('v', MOD + 'iberia.src', 0.8), 'apagones', None), (('v', MOD + 'gj.src', 48.5), 'protestas', None),
        (('v', MOD + 'chips.src', 400.0), 'carrera', None), (('v', MOD + 'dc_tour.src', 516.0), 'chips', None), (('v', 'archivo/hongo.mp4', 0), 'es|difícil|dificil', None)],
    3: [(('v', SH + 's13.mp4', 0), None, None), (('i', 'collage'), 'todo', None), (('v', 'anim/a_rostro.mp4', 0.5), 'cree', ('EL ORIGEN', 'UN MODELO DE IA IDÉNTICO A MÍ')),
        (('v', SH + 's12.mp4', 0), 'remanentes', None)],
    4: [(('i', 'nuar3'), None, ('NUAR', 'TRES VIDAS · TRES CUERPOS')), (('v', SH + 's07.mp4', 0), 'recuerda', None)],
    5: [(('i', 'exo'), None, ('LA HISTORIA', 'FALLOUT · BLADE RUNNER · GHOST IN THE SHELL\\NMATRIX · STALKER · EDGE OF TOMORROW')),
        (('i', 'soldado'), 'y', ('EL CINE', 'TERMINATOR 3 · SOY LEYENDA · THE LAST OF US'))],
    6: [(('i', 'env_full'), None, ('FICHAS', 'CADA MÁQUINA, POR ÉPOCAS')), (('i', 'env'), 'la', ('ENVOLTURA', 'CUERPOS SIN GÉNERO')),
        (('i', 'nodo'), 'el', ('NODO', 'CADA VEZ MENOS HUMANO')), (('v', 'anim/a_contorno.mp4', 0), 'el', ('CONTORNO', 'CARGA TODOTERRENO')),
        (('v', 'anim/a_ts9.mp4', 0), 'y', ('TS-9 AUSTRAL', 'TRANSPORTE DEL CONO SUR')), (('i', 'c7'), 'aguja', ('C-7 AGUJA', 'CAZA DE LA GUERRA ANTÁRTICA'))],
    7: [(('i', 'tres_all'), None, ('MAKING OF', 'HECHO CON INTELIGENCIA ARTIFICIAL')), (('v', 'anim/a_rostro.mp4', 1.0), 'porque', None)],
}
LEAD, TAIL = 0.35, 0.45


def words(path):
    from faster_whisper import WhisperModel
    global _M
    try: _M
    except NameError: _M = WhisperModel('small', compute_type='int8')
    segs, _ = _M.transcribe(path, language='es', word_timestamps=True)
    return [(w.start, w.end, norm(w.word)) for s in segs for w in s.words]


segs, aud, ev, t, n = [], [], [], 0.0, 0
for b in range(1, 8):
    vo = f'vo/m{b:02d}_n.wav'; vd = dur(vo); blen = vd + LEAD + TAIL
    aud.append((vo, t + LEAD)); wt = words(vo)
    i = 0
    for s in VO[b]:
        nw = len(s.split()); a = wt[min(i, len(wt) - 1)][0]; e = wt[min(i + nw, len(wt)) - 1][1]; i += nw
        ev.append(f"Dialogue: 6,{ts(t+LEAD+a)},{ts(t+LEAD+e+0.15)},Sub,,0,0,0,,{{\\fad(100,80)}}{s}")
    # tiempos de corte: en la palabra ancla (busca hacia delante)
    starts, wi = [], 0
    for k, (spec, anchor, lab) in enumerate(SHOTS[b]):
        if anchor is None: starts.append(0.0 if k == 0 else starts[-1] + 0.8); continue
        al = [norm(a) for a in anchor.split('|')]
        while wi < len(wt) and wt[wi][2] not in al: wi += 1
        st = LEAD + wt[wi][0] - 0.1 if wi < len(wt) else starts[-1] + 1.0
        starts.append(0.0 if k == 0 else st); wi += 1
    starts.append(blen)
    for k, (spec, anchor, lab) in enumerate(SHOTS[b]):
        d = round(starts[k + 1] - starts[k], 2); out = f'{OUT}/seg/{n:02d}.mp4'
        if not os.path.exists(out):
            if spec[0] == 'v': seg_video(spec[1], spec[2], d, out, k == 0, k == len(SHOTS[b]) - 1)
            else: seg_image(spec[1], d, out, k == 0, k == len(SHOTS[b]) - 1, n)
        segs.append(f'{n:02d}.mp4'); n += 1
        if lab:
            a0, a1 = t + starts[k], t + starts[k] + d
            ev.append(f"Dialogue: 7,{ts(a0+.05)},{ts(a1)},ChyR,,0,0,0,,{{\\an1\\pos(60,330)\\fad(80,60)}}{lab[0]}")
            ev.append(f"Dialogue: 7,{ts(a0+.15)},{ts(a1)},ChyW,,0,0,0,,{{\\an1\\pos(60,410)\\fad(80,60)}}{lab[1]}")
    if b == 2: aud.append(('sfx/rumble.wav', t + blen - 4.0))
    t += blen
cta = 6.3
out = f'{OUT}/seg/{n:02d}.mp4'
if not os.path.exists(out):
    seg_video(SH + 's01.mp4', 0, cta, out, True, True)
    run(f'ffmpeg -v error -y -i {out} -vf "eq=brightness=-0.25:saturation=0.7" -c:v libx264 -crf 18 -preset fast {out}.tmp.mp4 && mv {out}.tmp.mp4 {out}')
segs.append(f'{n:02d}.mp4'); n += 1
aud.append(('vo/b11_n.wav', t + 0.15)); o = t + 0.15
ev.append(f"Dialogue: 4,{ts(t+0.1)},{ts(t+cta)},Cta,,0,0,0,,{{\\an5\\pos(540,800)\\fad(150,0)}}SÍGUEME")
ev.append(f"Dialogue: 4,{ts(t+0.4)},{ts(t+cta)},Arroba,,0,0,0,,{{\\an5\\pos(540,930)\\fad(150,0)}}@raulalbright")
ev.append(f"Dialogue: 5,{ts(o+2.8)},{ts(t+cta)},Stamp,,0,0,0,,{{\\an5\\pos(540,1150)\\frz-4\\fscx150\\fscy150\\t(0,120,\\fscx100\\fscy100)}}GUARDA EL VIDEO")
for a_, b_, tx in [(0.0, 2.4, 'Sígueme para ver cómo sigue esta historia.'), (2.83, 3.9, 'Y guarda este video:'), (4.2, 5.7, 'así le llega a más gente.')]:
    ev.append(f"Dialogue: 6,{ts(o+a_)},{ts(o+b_)},Sub,,0,0,0,,{{\\fad(100,80)}}{tx}")
t += cta
ev.append(f"Dialogue: 8,{ts(0.2)},{ts(4.5)},Nota,,0,0,0,,{{\\an8\\pos(540,200)\\fad(300,300)}}ALIAS · MAKING OF")
TOTAL = t
ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat ExtraBold,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,2,2,90,90,330,1
Style: ChyR,Montserrat ExtraBold,44,&H00FFFFFF,&H00FFFFFF,&H002C19D7,&H00000000,0,0,0,0,100,100,3,0,3,12,0,1,0,0,0,1
Style: ChyW,Montserrat ExtraBold,30,&H00101010,&H00FFFFFF,&H00F0F0F0,&H00000000,0,0,0,0,100,100,1,0,3,12,0,1,0,0,0,1
Style: Nota,Montserrat ExtraBold,32,&H00B4B4B4,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,12,0,1,0,0,8,60,60,0,1
Style: Cta,Montserrat ExtraBold,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,10,0,1,0,0,5,0,0,0,1
Style: Arroba,Montserrat ExtraBold,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,5,0,0,0,1
Style: Stamp,Montserrat ExtraBold,90,&H00FFFFFF,&H00FFFFFF,&H002C19D7,&H00000000,0,0,0,0,100,100,6,0,3,18,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(f'{OUT}/subs.ass', 'w').write(ASS + '\n'.join(ev) + '\n')
open(f'{OUT}/seg/lista.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
json.dump({'total': TOTAL, 'aud': aud}, open(f'{OUT}/timeline.json', 'w'), indent=1)
print('total', round(TOTAL, 2), 'segs', len(segs))
ins = ['-f', 'concat', '-safe', '0', '-i', f'{OUT}/seg/lista.txt']; fc = []; labels = []; k = 1
for j, (p, off) in enumerate(aud):
    ins += ['-i', p]; ms = int(off * 1000)
    filt = f"[{k}:a]aresample=48000,pan=mono|c0=c0" + (",deesser=i=0.4" if p.startswith('vo/') else ",volume=0.7")
    fc.append(f"{filt},adelay={ms}|{ms}[a{j}]"); labels.append(f'[a{j}]'); k += 1
ins += ['-stream_loop', '-1', '-i', 'sfx/dron.wav']; fc.append(f"[{k}:a]aresample=48000,pan=mono|c0=c0,atrim=0:{TOTAL:.2f},volume=0.28,afade=t=in:d=1.5,afade=t=out:st={TOTAL-2:.2f}:d=2[dr]"); labels.append('[dr]'); k += 1
fc.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},highpass=f=40,lowpass=f=13000,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
fc.append(f"[0:v]ass={OUT}/subs.ass[vout]")
cmd = ['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]', '-t', f'{TOTAL:.2f}',
       '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f'{OUT}/alias_making_of.mp4']
subprocess.run(cmd, check=True); print('ok', f'{OUT}/alias_making_of.mp4')
