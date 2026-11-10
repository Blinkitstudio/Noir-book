"""ALIAS · Prólogo (montaje de archivo) — paso 1: segmentos de video + subtítulos ASS + timeline.json.

Se corre dentro de la carpeta de trabajo (ver README.md). Cachea cada plano en seg/NN.mp4:
si cambias un plano, BORRA ese índice (y los siguientes si cambian las duraciones) antes de volver a correr.
"""
import subprocess, json, os


def run(c): subprocess.run(c, shell=True, check=True)


SRC = {'reel25': 'moderno/reel25.src', 'def25v': 'moderno/def25v.src', 'convoy': 'moderno/convoy.src', 'costco': 'moderno/costco.src',
       'A1': '/home/user/alias/shots/s01.mp4', 'A2': '/home/user/alias/shots/s02.mp4',  # planos de la intro 2237
       'eu': 'moderno/eu.src', 'chips': 'moderno/chips.src', 'gj': 'moderno/gj.src', 'kit': 'moderno/kit.src', 'dct': 'moderno/dc_tour.src',
       'ibe': 'moderno/iberia.src', 'lis': 'moderno/lisboa.src', 'sat': 'moderno/sat_kill.src', 'tdr': 'moderno/tdrs.src',
       'tom': 'moderno/tomahawk.src', 'bal': 'moderno/bal.src', 'kyi': 'moderno/kyiv.src',
       'NR': 'cuba/newsreel.ogv', 'BR': 'cuba/brink.webm', 'RG': 'fuentes/gov.doe.0800010_512kb.mp4',
       'CR': 'fuentes/gov.doe.0800002.ogv', 'CA': 'fuentes/gov.doe.0800013.mpeg', 'DC': 'fuentes/DuckandC1951_edit.mp4', 'RD': 'fuentes/Radiolog1961_edit.mp4'}
# frases de la narración: (archivo, inicio, fin) — vo = vo_n.wav, vo2 = l13_n.wav
VO = [('vo2', 0.00, 2.63), ('vo', 4.16, 11.04), ('vo2', 4.34, 9.36), ('vo', 17.44, 21.76), ('vo', 22.72, 27.68), ('vo', 28.64, 37.20)]
# grupos: (fecha, segmentos[(fuente,inicio,dur[,fx])], vo_index | None, audio_archivo(fuente,inicio,dur,offset,traduccion) | None, sfx[(nombre,offset,vol)], tipo)
G = [
 # v14: abre con el hongo (gancho); las pruebas pasan a 1946 · 1951 (Crossroads + Buster-Jangle) para respetar la cronología
 ('1946', [('CR', 682.0, 3.4)], None, ('DC', 141.0, 2.6, 0.3, 'Hay un destello, más brillante que el sol...'), [('rumble', 0.0, 1.0)], 'arch'),
 ('1946', [('CR', 140.0, 3.6)], 0, None, [], 'arch'),
 ('1946 · 1951', [('CR', 722.0, 2.4), ('RG', 1060.0, 2.4), ('RG', 1083.5, 2.6)], 1, None, [('rumble', 4.8, .7)], 'arch'),
 ('1951', [('DC', 281.4, 4.8)], None, ('DC', 281.4, 4.8, 0.0, 'Si hay una alerta, la escucharás antes de que explote la bomba.'), [], 'arch'),
 ('1951', [('DC', 185.0, 2.6), ('DC', 425.0, 2.8)], 2, None, [], 'arch'),
 ('1951', [('DC', 369.8, 3.8)], None, ('DC', 369.8, 3.8, 0.0, '¡Es una bomba! Agáchate y cúbrete.'), [], 'arch'),
 ('1961', [('RD', 286.0, 2.6), ('RD', 308.5, 2.3)], 3, None, [], 'arch'),
 ('', [('BR', 13.0, 2.5, 'jfk'), ('BR', 60.5, 1.4, 'mod'), ('NR', 50.0, 1.5), ('NR', 57.3, 1.1), ('NR', 61.0, 1.5)], None, ('JFK', 521.6, 7.7, 0.15, '«…arriesgar el costo de una guerra nuclear mundial, en la que hasta los frutos de la victoria serían cenizas en nuestra boca.»'), [('hiss', 0.0, .05)], 'kennedy'),
 ('1962', [('RD', 545.0, 2.7), ('RD', 795.0, 2.7)], 4, None, [('rumble', 0.0, .6)], 'arch'),
 ('', [], None, None, [('hiss', 0.0, .04)], 'futuro2'),
 ('', [('BARS', 0, 0.6), ('BLACK', 0, 2.6)], None, None, [('pitido', 0.0, .18), ('rumble', 0.65, .8)], 'aliastitle'),
 ('', [('A2', 0.4, 3.0, 'full')], None, None, [('a2', 0.0, .7)], 'aliasfut'),
 ('', [('A1', 0.0, 6.0, 'fulldim')], None, ('CTA', 0.0, 5.6, 0.15, None), [('a1', 0.0, .4)], 'cta'),
]

MOD = [  # (tarjeta, zocalo1, zocalo2, [(vo_ini, vo_fin, desfase, subtitulo)], [planos]) — voz de moderno_n.wav
 ('2025', 'EUROPA · 2025', 'MANIOBRAS MILITARES EN TODO EL CONTINENTE',
  [(0.00, 3.07, 0.2, 'Pasaron décadas. Y las señales volvieron.'), (4.39, 9.57, 3.6, 'En 2025, Europa pidió a sus ciudadanos guardar provisiones para setenta y dos horas.')],
  [('def25v', 7.0, 1.1, 'mod'), ('convoy', 14.0, 1.1, 'mod'), ('def25v', 9.0, 1.1, 'mod'), ('convoy', 18.0, 1.1, 'mod'), ('def25v', 14.0, 1.1, 'mod')]),
 ('2025', 'ÚLTIMA HORA', 'LA UE PIDE A SUS CIUDADANOS PROVISIONES PARA 72 HORAS',
  [],
  [('costco', 20.0, 1.65, 'mod'), ('costco', 40.0, 1.65, 'mod')]),
 ('2025', 'ESPAÑA Y PORTUGAL · 28/04/2025', 'APAGÓN TOTAL EN LA PENÍNSULA IBÉRICA',
  [(10.68, 13.63, 0.2, 'Un apagón dejó a dos países a oscuras en segundos.')],
  [('ibe', 0.8, 1.7, 'mod'), ('lis', 3.0, 1.7, 'mod')]),
 ('PARÍS', 'PARÍS · EN VIVO', 'MILES DE PERSONAS EN LAS CALLES',
  [(14.40, 16.39, 0.2, 'Las calles se llenaron de protestas.')],
  [('gj', 48.5, 1.3, 'mod'), ('gj', 10.0, 1.3, 'mod')]),
 ('2031', 'ECONOMÍA', 'CARRERA MUNDIAL POR LOS CENTROS DE DATOS Y LOS CHIPS',
  [(17.25, 20.70, 0.2, 'Y empezó otra carrera: por los centros de datos y los chips.')],
  [('chips', 400.0, 1.3, 'mod'), ('chips', 470.0, 1.3, 'mod'), ('dct', 516.0, 1.3, 'mod')]),
 ('2036', 'ÚLTIMA HORA', 'CAEN SATÉLITES · SE CORTAN LAS REDES',
  [(21.38, 25.20, 0.2, 'Rusia, Estados Unidos, China, cada vez más cerca.')],
  [('sat', 44.0, 2.3, 'mod'), ('tdr', 67.0, 2.3, 'mod')]),
 ('OCTUBRE', '', '',
  [(25.60, 28.40, 0.1, 'Hasta que un octubre, todo pasó muy rápido.')],
  [('tom', 1.4, 1.2, 'mod'), ('bal', 45.0, 1.2, 'mod'), ('kyi', 53.0, 2.0, 'mod')]),
]
W, H, BY = 1080, 1920, 495  # caja 4:3 1080x810 desde y=495
segs, t, ev, aud = [], 0.0, [], []
MARK_FUT = FUT_LEN = 0.0
os.makedirs('seg', exist_ok=True)


def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f"{h}:{m:02d}:{s:05.2f}"


n = 0
for fecha, ss, vi, aa, sfx, tipo in G:
    g0 = t
    if tipo == 'futuro2': ss = [p for b in MOD for p in b[4]]
    for sg in ss:
        s, a, d = sg[:3]; fx = sg[3] if len(sg) > 3 else None
        out = f'seg/{n:02d}.mp4'
        if os.path.exists(out): segs.append(out); t += d; n += 1; continue
        if s == 'BARS':
            run(f'ffmpeg -v error -y -f lavfi -i smptehdbars=s={W}x{H}:r=30:d={d} -vf "noise=alls=20:allf=t,format=yuv420p" -c:v libx264 -crf 18 -preset fast {out}')
        elif s == 'BLACK':
            run(f'ffmpeg -v error -y -f lavfi -i color=c=0x050505:s={W}x{H}:r=30:d={d} -vf "noise=alls=10:allf=t+u,format=yuv420p" -c:v libx264 -crf 18 -preset fast {out}')
        elif fx in ('full', 'fulldim'):
            dim = ",eq=brightness=-0.12:saturation=0.85" if fx == 'fulldim' else ""
            run(f'ffmpeg -v error -y -ss {a} -i {SRC[s]} -t {d} -an -vf "scale={W}:{H}{dim},fps=30,format=yuv420p" -c:v libx264 -crf 18 -preset fast {out}')
        elif s == 'JFKCARD':
            run(f'ffmpeg -v error -y -ss {a} -i {SRC["CR"]} -ss 521.6 -t {d} -i jfk/jfk.mp3 -filter_complex "[0:v]setpts=PTS/0.6,scale=1188:891,crop=1080:810,eq=saturation=0.5:contrast=1.1:brightness=-0.22,noise=alls=16:allf=t+u,vignette=PI/4,fps=30,pad={W}:{H}:0:{BY}:black[bg];[1:a]highpass=f=250,lowpass=f=3500,showwaves=s=900x200:mode=cline:rate=30:colors=0xE6E6E6:scale=sqrt[w];[bg][w]overlay=90:1040,format=yuv420p[v]" -map "[v]" -t {d} -c:v libx264 -crf 18 -preset fast {out}')
        elif s == 'CARD':
            run(f'ffmpeg -v error -y -f lavfi -i color=c=0x08090b:s={W}x{H}:r=30:d={d} -vf "noise=alls=26:allf=t+u,eq=brightness=-0.04,format=yuv420p" -c:v libx264 -crf 18 -preset fast {out}')
        elif fx == 'jfk':  # Kennedy en «To the Brink»: recorte que deja fuera el rótulo «October 22, 1962» del National Archives
            vf = (f"crop=1160:870:380:20,scale=1080:810,eq=saturation=0.75:contrast=1.08:brightness='0.012*sin(2*PI*t*9)':eval=frame,"
                  f"noise=alls=14:allf=t+u,vignette=PI/5,fps=30,pad={W}:{H}:0:{BY}:black,format=yuv420p")
            run(f'ffmpeg -v error -y -ss {a} -i {SRC[s]} -t {d} -an -vf "{vf}" -c:v libx264 -crf 18 -preset fast {out}')
        else:
            if fx in ('mod', 'modR', 'modL'):
                cx = 'in_w-out_w' if fx == 'modR' else ('0' if fx == 'modL' else '(in_w-out_w)/2')
                pre = "scale=-2:1500,crop=1080:810:60:330," if fx == 'modL' else f"scale=1080:810:force_original_aspect_ratio=increase,crop=1080:810:{cx}:(ih-810)/2,"
                vf = (f"{pre}eq=saturation=0.75:contrast=1.08:brightness='0.012*sin(2*PI*t*9)':eval=frame,"
                      f"noise=alls=14:allf=t+u,vignette=PI/5,fps=30,pad={W}:{H}:0:{BY}:black,format=yuv420p")
                run(f'ffmpeg -v error -y -ss {a} -i {SRC[s]} -t {d} -an -vf "{vf}" -c:v libx264 -crf 18 -preset fast {out}')
                segs.append(out); t += d; n += 1; continue
            look = ("hue=s=0.25,colorbalance=bs=0.18:bm=0.08:rs=-0.06,rgbashift=rh=-6:bh=6,eq=contrast=1.15:brightness=-0.05," if fx else "")
            vf = (f"scale=1188:891,crop=1080:810,{look}eq=saturation=0.85:contrast=1.08:brightness='0.012*sin(2*PI*t*9)':eval=frame,"
                  f"noise=alls=14:allf=t+u,vignette=PI/5,fps=30,pad={W}:{H}:0:{BY}:black,format=yuv420p")
            run(f'ffmpeg -v error -y -ss {a} -i {SRC[s]} -t {d} -an -vf "{vf}" -c:v libx264 -crf 18 -preset fast {out}')
        segs.append(out); t += d; n += 1
    if fecha:
        ev.append(f"Dialogue: 4,{ts(g0)},{ts(t)},Fecha,,0,0,0,,{{\\an1\\pos(40,{BY-24})\\fad(80,0)}}{fecha}")
    if vi is not None:
        vs, a, b = VO[vi]; off = g0 + 0.25
        aud.append((vs, a, b - a, off, 1.0))
    if aa:
        s, a, d, o, tr = aa; aud.append((s, a, d, g0 + o, 1.0))
        if tr: ev.append(f"Dialogue: 5,{ts(g0+o)},{ts(g0+o+d)},Trad,,0,0,0,,{{\\an8\\pos(540,{BY+840})\\fad(100,100)}}{tr}")
    for nm, o, v in sfx: aud.append((nm, 0, None, g0 + o, v))
    if tipo == 'kennedy':
        ev.append(f"Dialogue: 4,{ts(g0)},{ts(t)},Card,,0,0,0,,{{\\an5\\pos(540,330)\\fs120\\fad(100,100)}}22 · X · 1962")
        ev.append(f"Dialogue: 4,{ts(g0)},{ts(t)},Nota,,0,0,0,,{{\\an5\\pos(540,430)}}JOHN F. KENNEDY · DISCURSO A LA NACIÓN · CRISIS DE LOS MISILES")
    if tipo == 'futuro2':
        MARK_FUT = g0; bt = g0
        for card, z1, z2, vos, shots in MOD:
            bd = sum(p[2] for p in shots); be = bt + bd
            ev.append(f"Dialogue: 4,{ts(bt)},{ts(be)},Card,,0,0,0,,{{\\an5\\pos(540,320)\\fs150\\fad(60,60)\\fscx110\\fscy110\\t(0,2000,\\fscx100\\fscy100)}}{card}")
            if z1:
                ev.append(f"Dialogue: 7,{ts(bt)},{ts(be)},Bug,,0,0,0,,{{\\an9\\pos(1050,520)}}SEÑAL AUSTRAL")
                ev.append(f"Dialogue: 7,{ts(bt)},{ts(be)},EnVivo,,0,0,0,,{{\\an9\\pos(1050,568)}}EN VIVO")
                ev.append(f"Dialogue: 7,{ts(bt+.1)},{ts(be)},ChyR,,0,0,0,,{{\\an1\\pos(30,1188)\\fad(80,0)}}{z1}")
                ev.append(f"Dialogue: 7,{ts(bt+.2)},{ts(be)},ChyW,,0,0,0,,{{\\an1\\pos(30,1262)\\fad(80,0)}}{z2}")
            for va, vb, vo_d, sub in vos:
                aud.append(('vo3', va, vb - va, bt + vo_d, 1.0))
                ev.append(f"Dialogue: 6,{ts(bt+vo_d)},{ts(bt+vo_d+vb-va+.15)},Sub,,0,0,0,,{{\\an8\\pos(540,1460)\\fad(120,80)}}{sub}")
            bt = be
        FUT_LEN = bt - g0
    if tipo == 'cta':
        o = g0 + 0.15
        ev.append(f"Dialogue: 4,{ts(g0+.1)},{ts(t)},Card,,0,0,0,,{{\\an5\\pos(540,800)\\fs150\\fad(150,0)\\fscx90\\fscy90\\t(0,200,\\fscx100\\fscy100)}}SÍGUEME")
        ev.append(f"Dialogue: 4,{ts(g0+.4)},{ts(t)},Arroba,,0,0,0,,{{\\an5\\pos(540,930)\\fad(150,0)}}@raulalbright")
        ev.append(f"Dialogue: 5,{ts(o+2.8)},{ts(t)},Stamp,,0,0,0,,{{\\an5\\pos(540,1150)\\frz-4\\fscx150\\fscy150\\t(0,120,\\fscx100\\fscy100)}}GUARDA EL VIDEO")
        for a_, b_, tx in [(0.0, 2.4, 'Sígueme para ver cómo sigue esta historia.'), (2.83, 3.9, 'Y guarda este video:'), (4.2, 5.7, 'así le llega a más gente.')]:
            ev.append(f"Dialogue: 6,{ts(o+a_)},{ts(o+b_)},Sub,,0,0,0,,{{\\an8\\pos(540,1460)\\fad(100,80)}}{tx}")
    if tipo == 'aliastitle':
        a0 = g0 + 0.6
        ev.append(f"Dialogue: 4,{ts(a0+.15)},{ts(t)},Card,,0,0,0,,{{\\an5\\pos(540,920)\\fs150\\fsp40\\fad(500,300)}}ALIAS")
        ev.append(f"Dialogue: 4,{ts(a0+.7)},{ts(t)},Nota,,0,0,0,,{{\\an5\\pos(540,1060)\\fs34\\fsp14\\fad(400,300)}}PRÓLOGO")
    if tipo == 'aliasfut':
        ev.append(f"Dialogue: 4,{ts(g0+.1)},{ts(t)},Fut,,0,0,0,,{{\\an8\\pos(540,330)\\fad(300,200)}}200 AÑOS DESPUÉS")
        ev.append(f"Dialogue: 4,{ts(g0+.6)},{ts(t)},Fut,,0,0,0,,{{\\an8\\pos(540,400)\\fs40\\fsp14\\fad(300,200)}}LA TIERRA · 2237")
TOTAL = t
# CTA intermedio (v14): 3 s, en la franja negra inferior para no tapar subtítulos
ev.append(f"Dialogue: 8,{ts(40.0)},{ts(43.0)},Stamp,,0,0,0,,{{\\an5\\pos(540,1700)\\fs58\\frz-3\\fscx130\\fscy130\\t(0,120,\\fscx100\\fscy100)\\fad(0,150)}}GUÁRDALO · PARTE 2: 2237")
ev.append(f"Dialogue: 8,{ts(0.2)},{ts(3.4)},Nota,,0,0,0,,{{\\an8\\pos(540,200)\\fs30\\fsp12\\fad(300,300)}}ALIAS · PRÓLOGO")
# subtítulos de la narración (por frase, con tiempos reales de la voz)
LINES = [(0, 'Nos enseñaron a convivir con el fin del mundo.', 0.0, 2.63), (1, 'Primero fueron pruebas. Islas lejanas, desiertos vacíos.', 4.16, 8.36), (1, 'Nadie pensaba que caería sobre una ciudad.', 8.88, 11.04),
         (2, 'Después llegaron los simulacros.', 4.34, 6.0), (2, 'Una mesa, decían, podía salvarnos.', 6.6, 9.36), (3, 'Mapas con nubes que avanzaban,', 17.44, 19.16), (3, 'periódicos que lo anunciaban como si fuera el clima.', 19.40, 21.76),
         (4, 'Una vez estuvimos al borde', 22.72, 24.2), (4, 'y aprendimos lo peor: que podíamos volver a acercarnos.', 24.3, 27.68)]
vo_off = {a[1]: a[3] for a in aud if a[0] in ('vo', 'vo2')}
for vi, txt, a, b in LINES:
    base = VO[vi][1]; off = vo_off[base] - base
    ev.append(f"Dialogue: 6,{ts(a+off)},{ts(b+off+.15)},Sub,,0,0,0,,{{\\an8\\pos(540,1460)\\fad(120,80)}}{txt}")
ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Fecha,Montserrat ExtraBold,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,8,0,1,0,0,1,0,0,0,1
Style: Sub,Montserrat ExtraBold,50,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,0,2,8,90,90,0,1
Style: Trad,Montserrat ExtraBold,40,&H00B4B4B4,&H00FFFFFF,&H00000000,&H00000000,0,1,0,0,100,100,0,0,1,0,0,8,90,90,0,1
Style: Card,Montserrat ExtraBold,170,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,10,0,1,0,0,5,0,0,0,1
Style: Titular,Montserrat ExtraBold,40,&H002C19D7,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,6,0,1,0,0,5,60,60,0,1
Style: Arroba,Montserrat ExtraBold,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,5,60,60,0,1
Style: Stamp,Montserrat ExtraBold,90,&H00FFFFFF,&H00FFFFFF,&H002C19D7,&H00000000,0,0,0,0,100,100,6,0,3,18,0,5,0,0,0,1
Style: Bug,Montserrat ExtraBold,30,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,4,0,1,0,1,9,0,0,0,1
Style: EnVivo,Montserrat ExtraBold,24,&H00FFFFFF,&H00FFFFFF,&H002C19D7,&H00000000,0,0,0,0,100,100,3,0,3,6,0,9,0,0,0,1
Style: ChyR,Montserrat ExtraBold,30,&H00FFFFFF,&H00FFFFFF,&H002C19D7,&H00000000,0,0,0,0,100,100,2,0,3,10,0,1,0,0,0,1
Style: ChyW,Montserrat ExtraBold,30,&H00101010,&H00FFFFFF,&H00F0F0F0,&H00000000,0,0,0,0,100,100,0,0,3,12,0,1,0,0,0,1
Style: Fut,Montserrat ExtraBold,56,&H00F0F0F0,&H00FFFFFF,&H50000000,&H00000000,0,0,0,0,100,100,9,0,1,0,2,8,40,40,0,1
Style: Nota,Montserrat ExtraBold,30,&H00808080,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open('subs.ass', 'w').write(ASS + '\n'.join(ev) + '\n')
open('seg/lista.txt', 'w').write(''.join(f"file '{s.split('/')[1]}'\n" for s in segs))
json.dump({'total': TOTAL, 'fut': MARK_FUT, 'futlen': FUT_LEN, 'aud': aud}, open('timeline.json', 'w'), indent=1)
print('total', round(TOTAL, 2), 'segs', len(segs))
