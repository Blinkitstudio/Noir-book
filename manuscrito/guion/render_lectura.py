from pathlib import Path
import html,textwrap
root=Path(__file__).resolve().parents[1]
s=(root/'alias-manuscrito-lectura.md').read_text()
chapters=s.split('\n## ')[1:]
pages=[]
for ch in chapters:
 title,body=ch.split('\n',1); blocks=body.strip().split('\n\n'); current=[]; lines=6; first=True
 for b in blocks:
  count=sum(max(1,len(textwrap.wrap(t,width=67))) for t in b.splitlines())+1
  if lines+count>37 and current:
   pages.append((title if first else '',current));current=[];lines=0;first=False
  current.append(b);lines+=count
 if current:pages.append((title if first else '',current))
css='''body{margin:0;background:#ddd;color:#222}section{box-sizing:border-box;width:794px;height:1123px;padding:90px 88px 80px 94px;margin:20px auto;background:#fffefa;position:relative;font-family:Georgia,serif;font-size:18px;line-height:1.5;page-break-after:always}p{margin:0 0 14px}h1{font-size:28px;line-height:1.3;font-weight:normal;margin:0 0 35px}header{position:absolute;top:38px;font:11px Arial,sans-serif;letter-spacing:3px;color:#777}footer{position:absolute;bottom:38px;right:88px;font:12px Arial,sans-serif;color:#777}.cover{text-align:center;padding-top:330px}.cover h1{font-size:42px;letter-spacing:8px}.note{font:13px Arial,sans-serif;margin-top:65px;color:#777}'''
parts=['<section class="cover" data-document-role="page" data-label="ALIAS"><h1>ALIAS</h1><p>Raúl Albright</p><p class="note">Manuscrito narrativo en desarrollo<br>Versión 0.1 · 10 de noviembre de 2026</p></section>']
for i,(title,blocks) in enumerate(pages,1):
 parts.append('<section data-document-role="page" data-label="Lectura '+str(i)+'"><header>ALIAS</header>'+('<h1>'+html.escape(title)+'</h1>' if title else '')+''.join('<p>'+html.escape(b)+'</p>' for b in blocks)+'<footer>'+str(i)+'</footer></section>')
(root/'alias-manuscrito-lectura-canva.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><title>ALIAS — Manuscrito narrativo</title><style>'+css+'</style><body>'+''.join(parts)+'</body></html>')
print('Total pages:',len(parts),'Words:',len(s.split()))
