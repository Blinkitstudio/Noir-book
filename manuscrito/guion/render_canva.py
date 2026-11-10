from pathlib import Path
import html,re
root=Path(__file__).parent
s=(root/'alias-v01.fountain').read_text()
s=re.sub(r'/\*.*?\*/','',s,flags=re.S)
s=s[s.index('FADE IN:'):]
css='''body{margin:0;background:#ddd}section{box-sizing:border-box;width:794px;height:1123px;background:white;padding:80px 72px 65px 112px;position:relative;font-family:"Courier New",Courier,monospace;font-size:16px;line-height:1.15;page-break-after:always;margin:20px auto;color:#111}p{margin:0 0 16px}.scene{font-weight:bold;margin-top:22px}.character{margin:20px 0 0 205px}.dialogue{margin:0 80px 18px 110px}.transition{text-align:right}.num{position:absolute;top:40px;right:72px}.cover{text-align:center;padding-top:300px}.cover h1{font-size:28px;font-weight:normal;letter-spacing:5px}.cover p{margin-top:28px}.small{font-size:13px}'''
pages=['<section class="cover" data-document-role="page" data-label="Portada"><h1>ALIAS</h1><p>Guion cinematográfico</p><p>Una historia de<br>Raúl Albright</p><p class="small">Versión 0.1 · 10 de noviembre de 2026<br>Prólogo y capítulos uno y dos<br>BORRADOR EN DESARROLLO</p></section>']
for i,chunk in enumerate(s.split('==='),1):
 blocks=chunk.strip().split('\n\n'); contents=[]; dialog=False
 for b in blocks:
  b=b.strip()
  if not b:continue
  cls=''
  if b.startswith(('INT.','EXT.')): cls='scene';dialog=False
  elif b=='NUAR (V.O.)':cls='character';dialog=True
  elif dialog:cls='dialogue';dialog=False
  elif b in ['FADE IN:','FADE OUT.','CUT TO BLACK.','CUT TO:']:cls='transition'
  elif b.startswith('>'):b=b.strip('> <');cls='transition'
  contents.append('<p class="'+cls+'">'+html.escape(b).replace('\n','<br>')+'</p>')
 pages.append('<section data-document-role="page" data-label="Guion '+str(i)+'"><div class="num">'+str(i)+'.</div>'+''.join(contents)+'</section>')
(root/'alias-v01-canva.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><title>ALIAS — Guion cinematográfico v0.1</title><style>'+css+'</style><body>'+''.join(pages)+'</body></html>')
print('Pages',len(pages),'scenes',len(re.findall(r"#\d+#",s)))
# Approximate line budget check for chosen manual pagination.
import textwrap
for i,c in enumerate(s.split('==='),1):
 n=0;dia=False
 for b in c.strip().split('\n\n'):
  width=37 if dia else 63
  n+=len(textwrap.wrap(b,width=width))+1
  dia=(b.strip()=='NUAR (V.O.)')
 print(i,'estimated lines:',n)
