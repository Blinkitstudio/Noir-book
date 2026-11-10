"""ALIAS · Documental «Me llaman Nuar»: arma la versión horizontal (16:9) o vertical (9:16).
Uso: python3 doc.py h   |   python3 doc.py v      (en la carpeta de trabajo, ver README)
"""
import json, os, subprocess, sys
from PIL import Image

MODE = sys.argv[1] if len(sys.argv) > 1 else 'h'
W, H = (1920, 1080) if MODE == 'h' else (1080, 1920)
BOXW, BOXH = (1800, 1010) if MODE == 'h' else (1080, 1380)
FPS = 30
SH = '/home/user/alias/shots/'
ART = 'arte/'
OUT = f'out_{MODE}'
os.makedirs(f'{OUT}/seg', exist_ok=True)


def run(c): subprocess.run(c, shell=True, check=True)


def dur(f): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)


# recortes de las láminas (archivo, caja x0,y0,x1,y1)
IMG = {
    'nuar_full': ('nuar-vestuario-cotidiano-2237.jpg', (0, 90, 1330, 1333)),
    'tres01': ('exec-5639548b-a231-409e-a88e-adfef7c2b56d.jpg', (0, 40, 505, 1000)),
    'tres_all': ('exec-5639548b-a231-409e-a88e-adfef7c2b56d.jpg', (0, 30, 1500, 1000)),
    'env': ('exec-06a1bc6a-48a3-4609-a1cd-8f45b6a02ad7.jpg', (0, 40, 1000, 345)),
    'nodo': ('exec-ba7ed8fc-ae95-487f-a263-1394df428a85.jpg', (0, 40, 740, 340)),
    'soldado': ('exec-94e1e2c6-83d7-4845-b94d-260d9b434e92.jpg', (0, 40, 760, 1000)),
    'c7': ('exec-f556e27e-8f38-4f3a-8964-a0b82e030b86.jpg', (0, 60, 1500, 640)),
    'exo': ('nuar-exoesqueleto-campo-2237.jpg', (0, 80, 1230, 1560)),
}
# narración por bloque: (archivo, frases del guion)
VO = {
    1: ['La ciudad funciona.', 'Cada mañana, antes de que lleguen los transportes, las máquinas retiran la nieve de las plataformas.', 'Hay agua en las tuberías.', 'Los ascensores suben.'],
    2: ['Aquí me llaman Nuar.', 'No es el nombre con el que nací.', 'Ese nombre se quedó en otro cuerpo.'],
    3: ['Los humanos llevan doscientos años ausentes.', 'Dejaron edificios, instrucciones, habitaciones preparadas para personas que nunca llegaron.', 'Algunos partieron hacia Europa, la luna de Júpiter.', 'Todavía quedan antenas orientadas hacia allí.', 'Ninguna señal ha permitido saber si encontraron un lugar donde vivir.'],
    4: ['Era octubre cuando volé al sur.', 'Creí que la distancia podía salvarnos.', 'Las bombas cayeron lejos.', 'Después llegaron otras cosas, más lentas.', 'Durante mucho tiempo confundí seguir vivo con haber escapado.'],
    5: ['Las réplicas fueron lo último que los humanos hicieron para salvarse.', 'Cultivaron cuerpos.', 'Confiaron sus mentes a los centros de datos.', 'Los cuerpos dejaron de envejecer.', 'Siguieron siendo vulnerables al frío, a una caída, a la violencia.', 'Cuando uno se rompe, hay que criar otro.'],
    6: ['Las máquinas se multiplican más deprisa.', 'Hace tiempo adquirieron conciencia.', 'Construyen cuerpos que ya no necesitan parecerse a sus creadores.'],
    7: ['Cuando nos enviaron a la Antártida, el sur también tenía un frente.', 'Recuerdo el parche del Cono Sur sobre la manga.', 'El Austral esperaba con la rampa abierta.', 'Oí los cazas antes de verlos.'],
    8: ['Habíamos aprendido a cambiar de cuerpo.', 'Seguíamos sin aprender a despedirnos.', 'Esta es mi tercera vida.', 'De las otras dos, todavía no sé cuánto puedo contar.'],
    9: ['Los centros de datos nos sostienen a todos.', 'Réplicas y máquinas compartimos la corriente, el frío, los conductos.', 'Nuestros creadores también compartían un mundo.', 'No les bastó.'],
    10: ['De ella recuerdo cosas pequeñas.', 'Sé que va a pronunciar mi nombre.', 'Ahí siempre falta algo.', 'No recuerdo el nombre del hombre que la amaba.', 'Recuerdo cómo lo miraba ella.'],
}
# planos por bloque: ('v', archivo, inicio) | ('i', clave) ; peso opcional al final
SHOTS = {
    1: [('v', SH + 's01.mp4', 0), ('v', SH + 's02.mp4', 0)],
    2: [('v', 'anim/a_rostro.mp4', 0, 1.4), ('v', SH + 's04.mp4', 0)],
    3: [('v', SH + 's07.mp4', 0), ('v', SH + 's03.mp4', 0), ('v', SH + 's12.mp4', 0)],
    4: [('v', 'archivo/hongo.mp4', 0), ('i', 'tres01', 1.4)],
    5: [('v', SH + 's05.mp4', 0), ('i', 'tres_all', 1.3), ('v', SH + 's06.mp4', 0, 0.8)],
    6: [('i', 'env'), ('i', 'nodo'), ('v', SH + 's08.mp4', 0)],
    7: [('i', 'soldado', 0.9), ('v', 'anim/a_ts9.mp4', 0), ('v', 'anim/a_embarque.mp4', 0), ('i', 'c7', 0.8)],
    8: [('v', 'anim/a_contorno.mp4', 0), ('i', 'exo')],
    9: [('v', SH + 's11.mp4', 0), ('v', SH + 's10.mp4', 0), ('v', SH + 's09.mp4', 0)],
    10: [('v', 'anim/a_rostro.mp4', 0, 1.3), ('v', SH + 's13.mp4', 0)],
}
BLOCKS = list(range(1, 11)) if MODE == 'h' else [1, 2, 4, 5, 7, 8, 10]
LEAD, TAIL = (0.8, 1.6) if MODE == 'h' else (0.5, 0.6)
GRADE = "eq=contrast=1.05:saturation=0.88:brightness=-0.02,noise=alls=7:allf=t+u,vignette=PI/5"


def fit(w, h):
    s = min(BOXW / w, BOXH / h)
    return int(w * s) // 2 * 2, int(h * s) // 2 * 2


def seg_video(path, start, d, out, fade_in, fade_out):
    sd = dur(path) - start
    speed = min(max(d / sd, 1.0), 1.7)  # si el clip es corto, se ralentiza
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.split(','))
    fw, fh = fit(w, h)
    fades = (f",fade=t=in:st=0:d=0.4" if fade_in else "") + (f",fade=t=out:st={d-0.5:.2f}:d=0.5" if fade_out else "")
    fc = (f"[0:v]setpts={speed:.3f}*(PTS-STARTPTS),fps={FPS},split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:2,eq=brightness=-0.28:saturation=0.6[bg];"
          f"[b]scale={fw}:{fh}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,{GRADE},tpad=stop_mode=clone:stop_duration=4,trim=0:{d:.3f},setpts=PTS-STARTPTS{fades},format=yuv420p[v]")
    run(f'ffmpeg -v error -y -ss {start} -i "{path}" -filter_complex "{fc}" -map "[v]" -an -t {d:.3f} -r {FPS} -c:v libx264 -crf 18 -preset fast {out}')


def seg_image(key, d, out, fade_in, fade_out, k):
    f, box = IMG[key]
    im = Image.open(ART + f).convert('RGB').crop(box)
    fw, fh = fit(*im.size)
    zw, zh = int(fw * 1.10) // 2 * 2, int(fh * 1.10) // 2 * 2
    im.resize((zw, zh), Image.LANCZOS).save(f'{OUT}/tmp_{key}.png')
    bgim = im.copy(); bgim.save(f'{OUT}/tmp_{key}_bg.png')
    dx, dy = zw - fw, zh - fh
    x = f"{dx}*t/{d:.3f}" if k % 2 == 0 else f"{dx}*(1-t/{d:.3f})"   # paneo lento, alterna dirección
    y = f"{dy}*0.5"
    fades = (f",fade=t=in:st=0:d=0.4" if fade_in else "") + (f",fade=t=out:st={d-0.5:.2f}:d=0.5" if fade_out else "")
    fc = (f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:2,eq=brightness=-0.3:saturation=0.6[bg];"
          f"[0:v]crop={fw}:{fh}:'{x}':'{y}'[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,{GRADE}{fades},format=yuv420p[v]")
    run(f'ffmpeg -v error -y -loop 1 -framerate {FPS} -t {d:.3f} -i {OUT}/tmp_{key}.png -loop 1 -framerate {FPS} -t {d:.3f} -i {OUT}/tmp_{key}_bg.png '
        f'-filter_complex "{fc}" -map "[v]" -t {d:.3f} -r {FPS} -c:v libx264 -crf 18 -preset fast {out}')


def card(out, d, src=None, start=0):
    if src:  # plano de fondo oscurecido para el cierre
        seg_video(src, start, d, out, True, True)
        run(f'ffmpeg -v error -y -i {out} -vf "eq=brightness=-0.25:saturation=0.7" -c:v libx264 -crf 18 -preset fast {out}.tmp.mp4 && mv {out}.tmp.mp4 {out}')
    else:
        run(f'ffmpeg -v error -y -f lavfi -i color=c=0x050505:s={W}x{H}:r={FPS}:d={d} -vf "noise=alls=8:allf=t+u,format=yuv420p" -c:v libx264 -crf 18 -preset fast {out}')


def words(path):
    from faster_whisper import WhisperModel
    global _M
    try: _M
    except NameError: _M = WhisperModel('small', compute_type='int8')
    segs, _ = _M.transcribe(path, language='es', word_timestamps=True)
    return [(w.start, w.end) for s in segs for w in s.words]


def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"


segs, aud, ev, t, n = [], [], [], LEAD, 0
card(f'{OUT}/seg/{n:02d}.mp4', LEAD); segs.append(f'{n:02d}.mp4'); n += 1
for b in BLOCKS:
    vo = f'vo/b{b:02d}_n.wav'; vd = dur(vo)
    blen = vd + 0.6 + TAIL
    aud.append((vo, t + 0.6))
    # subtítulos por frase, alineados con los tiempos de palabra
    wt = words(vo); i = 0
    for s in VO[b]:
        nw = len(s.split()); a = wt[min(i, len(wt) - 1)][0]; e = wt[min(i + nw, len(wt)) - 1][1]; i += nw
        ev.append(f"Dialogue: 5,{ts(t+0.6+a)},{ts(t+0.6+e+0.2)},Sub,,0,0,0,,{{\\fad(120,100)}}{s}")
    sh = SHOTS[b]; wsum = sum((x[3] if x[0] == 'v' and len(x) > 3 else x[2] if x[0] == 'i' and len(x) > 2 else 1.0) for x in sh)
    acc = 0.0
    for k, x in enumerate(sh):
        wgt = x[3] if x[0] == 'v' and len(x) > 3 else x[2] if x[0] == 'i' and len(x) > 2 else 1.0
        d = round(blen * wgt / wsum, 2) if k < len(sh) - 1 else round(blen - acc, 2)
        out = f'{OUT}/seg/{n:02d}.mp4'
        if not os.path.exists(out):
            if x[0] == 'v': seg_video(x[1], x[2], d, out, k == 0, k == len(sh) - 1)
            else: seg_image(x[1], d, out, k == 0, k == len(sh) - 1, n)
        segs.append(f'{n:02d}.mp4'); n += 1; acc += d
    if b == 4: aud.append(('sfx/rumble.wav', t + 0.1))
    t += blen
# cierre: título ALIAS (solo horizontal) + CTA con la voz de Raúl
if MODE == 'h':
    card(f'{OUT}/seg/{n:02d}.mp4', 2.6); segs.append(f'{n:02d}.mp4'); n += 1
    ev.append(f"Dialogue: 4,{ts(t+0.3)},{ts(t+2.5)},Card,,0,0,0,,{{\\fad(500,300)}}ALIAS")
    ev.append(f"Dialogue: 4,{ts(t+0.8)},{ts(t+2.5)},Nota,,0,0,0,,{{\\fad(400,300)}}ME LLAMAN NUAR")
    t += 2.6
cta = 6.3
card(f'{OUT}/seg/{n:02d}.mp4', cta, SH + 's01.mp4', 0); segs.append(f'{n:02d}.mp4'); n += 1
aud.append(('vo/b11_n.wav', t + 0.15))
o = t + 0.15
ev.append(f"Dialogue: 4,{ts(t+0.1)},{ts(t+cta)},Cta,,0,0,0,,{{\\fad(150,0)}}SÍGUEME")
ev.append(f"Dialogue: 4,{ts(t+0.4)},{ts(t+cta)},Arroba,,0,0,0,,{{\\fad(150,0)}}@raulalbright")
ev.append(f"Dialogue: 5,{ts(o+2.8)},{ts(t+cta)},Stamp,,0,0,0,,{{\\frz-4\\fscx150\\fscy150\\t(0,120,\\fscx100\\fscy100)}}GUARDA EL VIDEO")
for a_, b_, tx in [(0.0, 2.4, 'Sígueme para ver cómo sigue esta historia.'), (2.83, 3.9, 'Y guarda este video:'), (4.2, 5.7, 'así le llega a más gente.')]:
    ev.append(f"Dialogue: 6,{ts(o+a_)},{ts(o+b_)},Sub,,0,0,0,,{{\\fad(100,80)}}{tx}")
t += cta
ev.append(f"Dialogue: 8,{ts(0.6)},{ts(4.0)},Nota,,0,0,0,,{{\\fad(300,300)}}ALIAS · ARCHIVO DE NUAR")
TOTAL = t
if MODE == 'h':
    pos = dict(sub=(960, 1000, 54), card=(960, 520, 180), nota=(960, 640, 30), cta=(960, 470, 140), arroba=(960, 590, 52), stamp=(960, 760, 80), top=(960, 70))
else:
    pos = dict(sub=(540, 1560, 50), card=(540, 900, 170), nota=(540, 1040, 30), cta=(540, 800, 150), arroba=(540, 930, 56), stamp=(540, 1150, 90), top=(540, 200))
ASS = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat ExtraBold,{pos['sub'][2]},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,2,2,140,140,{H-pos['sub'][1]},1
Style: Card,Montserrat ExtraBold,{pos['card'][2]},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,40,0,1,0,0,5,0,0,0,1
Style: Nota,Montserrat ExtraBold,{pos['nota'][2]},&H00A0A0A0,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,12,0,1,0,0,8,60,60,{pos['top'][1]},1
Style: Cta,Montserrat ExtraBold,{pos['cta'][2]},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,10,0,1,0,0,5,0,0,0,1
Style: Arroba,Montserrat ExtraBold,{pos['arroba'][2]},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,5,0,0,0,1
Style: Stamp,Montserrat ExtraBold,{pos['stamp'][2]},&H00FFFFFF,&H00FFFFFF,&H002C19D7,&H00000000,0,0,0,0,100,100,6,0,3,18,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
# posiciones explícitas para tarjetas y CTA
fix = {'Card': pos['card'], 'Cta': pos['cta'], 'Arroba': pos['arroba'], 'Stamp': pos['stamp']}
out_ev = []
for e in ev:
    st = e.split(',')[3]
    if st in fix:
        x, y = fix[st][:2]; e = e.replace(',,{', f',,{{\\an5\\pos({x},{y})', 1).replace('{{', '{')
    if st == 'Nota' and 'ME LLAMAN' in e:
        e = e.replace(',,{', f",,{{\\an5\\pos({pos['nota'][0]},{pos['nota'][1]})", 1).replace('{{', '{')
    out_ev.append(e)
open(f'{OUT}/subs.ass', 'w').write(ASS + '\n'.join(out_ev) + '\n')
open(f'{OUT}/seg/lista.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
json.dump({'total': TOTAL, 'aud': aud}, open(f'{OUT}/timeline.json', 'w'), indent=1)
print('total', round(TOTAL, 2), 'segs', len(segs))

# mezcla: voz + dron en bucle + viento suave en la Antártida + rumble
ins = ['-f', 'concat', '-safe', '0', '-i', f'{OUT}/seg/lista.txt']; fc = []; labels = []; k = 1
for j, (p, off) in enumerate(aud):
    ins += ['-i', p]; ms = int(off * 1000)
    filt = f"[{k}:a]aresample=48000,pan=mono|c0=c0" + (",deesser=i=0.4" if p.startswith('vo/') else ",volume=0.8")
    fc.append(f"{filt},adelay={ms}|{ms}[a{j}]"); labels.append(f'[a{j}]'); k += 1
ins += ['-stream_loop', '-1', '-i', 'sfx/dron.wav']; fc.append(f"[{k}:a]aresample=48000,pan=mono|c0=c0,atrim=0:{TOTAL:.2f},volume=0.32,afade=t=in:d=2,afade=t=out:st={TOTAL-2:.2f}:d=2[dr]"); labels.append('[dr]'); k += 1
ins += ['-stream_loop', '-1', '-i', 'sfx/hiss.wav']; fc.append(f"[{k}:a]aresample=48000,pan=mono|c0=c0,atrim=0:{TOTAL:.2f},lowpass=f=2500,volume=0.05,afade=t=in:d=3,afade=t=out:st={TOTAL-2:.2f}:d=2[hs]"); labels.append('[hs]'); k += 1
fc.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},highpass=f=40,lowpass=f=13000,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
fc.append(f"[0:v]ass={OUT}/subs.ass[vout]")
cmd = ['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]', '-t', f'{TOTAL:.2f}',
       '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f'{OUT}/alias_documental_{MODE}.mp4']
subprocess.run(cmd, check=True); print('ok', f'{OUT}/alias_documental_{MODE}.mp4')
