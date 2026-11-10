# Montaje de archivo · ALIAS · Prólogo

Scripts y fuentes para volver a renderizar el prólogo (86.6 s, 9:16). Versión publicada: **v13**, en la biblioteca de Higgsfield de Raúl (media `1e8f8be0-45ef-4914-a577-abc852c28dad`). Guion, decisiones y versiones anteriores: [`../noticiero-como-empezo.md`](../noticiero-como-empezo.md). Texto del post: [`../../contenido/publicacion/alias-prologo.md`](../../contenido/publicacion/alias-prologo.md).

El repositorio es público: aquí van scripts y enlaces, **nunca** los videos ni los audios.

## Archivos
| Archivo | Qué hace |
|---|---|
| `build.py` | Corta y trata cada plano (4:3 dentro de 9:16, grano, viñeta, parpadeo), arma los subtítulos ASS (fechas, zócalos de Señal Austral, traducciones, cierre SÍGUEME) y escribe `timeline.json` con los tiempos de cada audio. |
| `mix.py` | Concatena los planos, quema los subtítulos y mezcla: voz de Raúl, audio de archivo limpiado, efectos, cama de proyector y dron; master a -14 LUFS. `python3 mix.py renders/archivo_vNN.mp4` |
| `chequeo_agudos.py` | Busca chirridos (energía > 6 kHz). Salida vacía = limpio. |
| `fuentes.md` | Todas las fuentes con licencia, autor y enlace. |

## Carpeta de trabajo (fuera del repo)
```
alias-archivo/
  fuentes/   películas de archive.org (ver fuentes.md)
  moderno/   clips de Wikimedia Commons, guardados como <nombre>.src
  jfk/jfk.mp3                discurso del 22/10/1962 (lo descarga Raúl de la Biblioteca JFK)
  vo/        vo.mp3, l13.mp3, moderno.mp3, cta.mp3  +  *_n.wav normalizados a -20 LUFS
  sfx/       proyector (120 s), dron (90 s), rumble, hiss, pitido, a1, a2 (sonido de los planos 2237)
  seg/  renders/
```
Los planos de 2237 (`A1`, `A2` en `build.py`) son `s01.mp4` y `s02.mp4` de la intro "La Tierra · 2237"; ajusta la ruta en `SRC`.

## Requisitos
ffmpeg con libass, fuente Montserrat ExtraBold instalada, Python 3 con numpy (solo para el chequeo).

## Volver a renderizar
1. Normaliza cada toma de voz nueva: `ffmpeg -i vo/x.mp3 -af loudnorm=I=-20:TP=-2 -ar 48000 vo/x_n.wav`.
2. Si cambias un plano o su duración, **borra `seg/NN.mp4` de ese índice** (y de los siguientes si cambian tiempos). `build.py` reutiliza lo que ya existe; un segmento viejo desfasa todo el final.
3. `python3 build.py` → imprime duración total y número de segmentos.
4. `python3 mix.py renders/archivo_vNN.mp4` (en el sandbox de Higgsfield: en segundo plano y tamaño XL).
5. Entrega comprimida: `ffmpeg -i renders/archivo_vNN.mp4 -c:v libx264 -crf 23 -maxrate 10M -bufsize 20M -c:a copy -movflags +faststart alias_archivo_vNN.mp4` (con crf 18 el grano dispara el bitrate a ~68 Mbps).
6. Comprueba: `python3 chequeo_agudos.py alias_archivo_vNN.mp4` vacío; `ffmpeg -i … -af ebur128 -f null -` cerca de -14 LUFS; mira 4 fotogramas (inicio, 2025, OCTUBRE, cierre).

## Cosas aprendidas
- Nada de teletipo ni estática blanca sintéticos: generan chirridos. Ruido marrón suave y fundidos.
- El archivo viejo lleva `adeclick` + `afftdn` + pasa bajos; la voz, de-esser y fundidos de 30–60 ms.
- Normalizar todas las tomas de voz antes de mezclar evita saltos de volumen bruscos.
- Las camas (proyector, dron) deben durar más que el timeline; si no, aparecen huecos de silencio.
- Videos verticales: recorte centrado `(ih-810)/2`, o se corta el cielo.
- Wikimedia: pide User-Agent (si no, 403) y pausas entre consultas (429).
