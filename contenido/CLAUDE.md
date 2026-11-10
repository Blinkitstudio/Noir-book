# Contenido de Raúl Albright — guía para Claude

Esta carpeta es el kit de edición de video de Raúl (Instagram **@raulalbright**). Si abres Claude Code aquí o en una carpeta de vlog, este archivo es tu contexto: quién es, cómo es su estilo y cómo se edita.

## Quién es y qué publica
- Raúl Albright, mexicano (CDMX), vive en Buenos Aires. Emprendedor: tecnología e IA (Orbit, software para concesionarias), marketing, bienes raíces, fotografía.
- Contenido que mezcla:
  1. **Vlogs de viaje y negocios** al estilo HiClavero: él a cámara, calle, lugares, datos concretos. Uno de los ejes es **desmentir mitos sobre Argentina**.
  2. **Reels de IA** con su voz clonada y visuales generados (Higgsfield).
  3. **Fotografía.**
  4. **ALIAS**: su ficción de ciencia ficción (ver `../manuscrito`, `../desarrollo`, `../produccion`).
- Quiere aprender a hablar a cámara. Si un take está flojo, díselo con tacto y propón cómo regrabarlo; no lo escondas.
- Idioma: español neutro con matices mexicanos. No conviertas su forma de hablar en argentino.

## Dónde está el material (en su Mac)
```
~/Movies/Vlogs/
├── 2026-11-12_tema/
│   ├── crudo/        ← clips del iPhone tal cual (IMG_xxxx.MOV); NO se tocan ni se borran
│   ├── fotos/
│   ├── notas.txt     ← idea, frase de arranque, lo que no puede faltar (si existe, léelo primero)
│   ├── edl.json      ← lo escribes tú: la lista de cortes
│   ├── textos.json   ← lo escribes tú: palabras en rojo, correcciones, textos grandes
│   ├── mezcla.json   ← lo escribes tú: música y efectos
│   ├── trabajo/      ← intermedios generados (se pueden regenerar)
│   └── final/        ← entregables
└── _musica/
```
El video pesado **nunca** se sube a este repo (es público). Al repo solo van scripts, guías y aprendizajes.

## Preparación (una vez por Mac)
```bash
brew install ffmpeg
brew install --cask font-montserrat        # la tipografía de todos los textos
pip3 install -r <repo>/contenido/kit/requirements.txt
export ELEVENLABS_API_KEY=...              # para limpiar la voz (agrégala a ~/.zshrc)
```
Si el conector MCP de ElevenLabs está disponible en esta sesión, también puedes usar su nodo **Voice Isolator**. `limpiar_voz.py` usa la API directa, que es lo mismo.

## Flujo de edición de un vlog
`K=<repo>/contenido/kit` y `V=~/Movies/Vlogs/<vlog>`:

1. `python3 $K/ingesta.py $V`: inventario ordenado por hora de grabación y extracción de audio.
2. `python3 $K/limpiar_voz.py $V`: voz limpia con ElevenLabs (o afftdn si no hay clave).
3. `python3 $K/transcribir.py $V`: transcripción palabra por palabra de cada clip (`trabajo/transcripciones/*.txt`).
4. **Tú decides el corte.** Lee las transcripciones y `notas.txt` y escribe `$V/edl.json`. Este es el paso donde está el criterio. Ver "Estilo de corte".
5. `python3 $K/corte.py $V` → `trabajo/corte.mp4`.
6. `python3 $K/transcribir.py $V --corte` → palabras con los tiempos ya del corte.
7. Escribe `$V/textos.json` y corre `python3 $K/subs.py $V`.
8. Escribe `$V/mezcla.json` y corre `python3 $K/mezcla.py $V` → `final/<vlog>.mp4`.
9. **Revisa antes de entregar.** Extrae fotogramas en los momentos clave (`ffmpeg -ss T -i final/x.mp4 -frames:v 1 f.png`) y míralos. Comprueba:
   - textos legibles y que no se encimen con los subtítulos;
   - el gancho en los primeros 2 s;
   - el volumen en -14 LUFS (`ffmpeg -i x.mp4 -af ebur128 -f null -`).

Las plantillas de `edl.json`, `textos.json` y `mezcla.json` están en `plantillas/proyecto/`. Cada script explica sus opciones en el encabezado.

## Estilo de corte (vlog estilo HiClavero, adaptado a Raúl)
- **Gancho en 0–2 s.** Abre con la frase más fuerte o la imagen más rara, aunque esté a mitad del material. Va con texto grande (`big`) y sin subtítulo encima (`ocultar`).
- **Ritmo.** Corta silencios, "eh", "este" y respiraciones largas. Ningún plano a cámara de más de 4–5 s sin un corte, un zoom `punch` o un b-roll encima. Un take repetido: quédate con el mejor y descarta el resto.
- **B-roll** cada vez que nombra algo (un lugar, comida, un precio, un letrero). Va `mudo: true` o con ambiente bajo mientras sigue su voz. Si no hay b-roll de algo importante, anótalo para la próxima grabación.
- **Zooms.** `punch` en las palabras clave y los remates; `lento` en planos de ambiente y fotos.
- **Datos concretos en pantalla** (precios, cifras, nombres) con `label` o `big`. Si das un dato que no salió de su boca, verifícalo antes.
- **Cierre** con pregunta o llamada a comentar (`stamp`, por ejemplo "COMENTA: ¿SÍ O NO?"). Que se pueda repetir en bucle.
- **Duración:** Reel de 30–60 s por defecto. Si el material da para más, una versión larga aparte (3–8 min, horizontal 16:9 para YouTube, sin subtítulos palabra por palabra).

## Estilo visual y sonoro (identidad de Raúl)
- **Tipografía:** Montserrat ExtraBold, todo en mayúsculas.
- **Color de marca:** rojo `#D7192C` (en ASS `&H2C19D7&`) para palabras clave y stamps. El texto va blanco; los datos secundarios en gris `#C8C8C8`. El granate `#320C0E` se usó en tarjetas de los reels de IA.
- **Subtítulos:** una palabra a la vez, centrados en y=1520, con un pop de escala. Las palabras clave en rojo. Corrige siempre los errores de la transcripción, sobre todo nombres propios y términos de IA.
- **Estilos de texto:**
  - `big`: titulares de impacto (y≈760–900).
  - `label`: contexto arriba (y≈330), por ejemplo "PALERMO · BUENOS AIRES" o fuentes.
  - `stamp`: caja roja con texto blanco, inclinada. Para remates y CTA. Nunca texto rojo sobre caja roja.
- **Color de imagen:** `calido` para el día, `noche` para la noche, `neutro` si la luz ya es buena. Todo el vlog con el mismo grade salvo que el cambio sea intencional.
- **Sonido:**
  - voz limpia más un 10–20 % de ambiente real (que no suene a estudio);
  - música baja (0.18–0.25) con ducking bajo la voz;
  - efectos sutiles en cortes y textos: `whoosh`, `golpe`, `pop`, `impacto`, `obturador`, `riser`, `click` (en `kit/sfx`);
  - mezcla final a -14 LUFS.
- **Contraste:** si un texto se lee mal sobre la imagen, oscurece el plano o usa `stamp` en vez de agregar sombras.

## Voz clonada (ElevenLabs)
- Voz **"Raul Albright"**, voice_id `iLCjJRTX0YL3XzRxFmfl`, modelo `eleven_v4`. Acepta etiquetas de emoción entre corchetes ([serio], [pausa], etc.).
- En vlogs se usa solo para voces en off puntuales o para arreglar una palabra mal dicha. Avísale a Raúl cuando la uses: su voz real es la prioridad.

## Estrategia y publicación
- Qué publicar, cuándo y cómo medirlo: [`estrategia.md`](estrategia.md).
- Plan día por día y lista de grabación: [`calendario.md`](calendario.md). Actualízalo cuando Raúl confirme o cambie algo.
- Texto listo para cada post (descripción, créditos, etiqueta de IA): `publicacion/`. Cada pieza con material CC BY lleva sus créditos.
- Montaje de archivo de ALIAS (scripts y fuentes): `../produccion/montaje-archivo/`.

## Reglas
- No borres ni modifiques nada de `crudo/`. Todo lo generado va a `trabajo/` o `final/`.
- No publiques en redes sin que Raúl lo pida y lo confirme.
- Antes de gastar créditos (Higgsfield, ElevenLabs, música generada), di cuánto va a costar. Un crédito de Higgsfield cuesta unos US$0.043.
- Cuando aprendas algo que sirva para los siguientes videos (un error típico de la transcripción, un tipo de gancho que funcionó, un ajuste de volumen), agrégalo a `historico/aprendizajes.md` y haz commit.
