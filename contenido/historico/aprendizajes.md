# Aprendizajes y proyectos anteriores

Registro vivo: agrega aquí lo que sirva para el siguiente video.

## Proyectos hechos (noviembre 2026)
| Proyecto | Formato | Cómo se hizo | Notas |
|---|---|---|---|
| Reel IA / Orbit | 9:16, 30 s | Preset Shorts Studio de Higgsfield + Seedance 2.5 + su voz en ElevenLabs | Inversión en IA, primera venta, Orbit casi listo |
| Corto de invierno / réplicas | 21:9, 65 s, 720p | Higgsfield (mejor modelo) + narración con su voz | Look Sony FX30, fotorrealista |
| ALIAS, intro Tierra 2237 | 9:16, 89 s, 720p | 13 planos Higgsfield + títulos, subtítulos y letreros ASS en post | Letreros compuestos en postproducción sobre planos fijos |
| Reel "cómo se hacen videos con IA" | 9:16 | 0 créditos: reutiliza el material de ALIAS + gráficos ASS + su voz | Orientado a viralidad |
| Reel "¿la IA tiene conciencia?" | 9:16, 53.6 s | 0 créditos: material de ALIAS + tarjetas (email, terminal) + su voz | Fuentes: Anthropic 2025 (agentic misalignment), Palisade 2025, Nature 2026 |

## Lecciones técnicas
- **La transcripción se equivoca con términos de IA y nombres propios.** Casos vistos: "una gente" → "un agente", "o 3" → "o3". Revisa siempre las `correcciones` en textos.json.
- **Saturación de texto:** si hay un texto grande en pantalla, oculta los subtítulos en ese tramo (`ocultar`). Si no, se ve amontonado.
- **Contraste:** texto blanco sobre fondo claro no se lee. Oscurece el plano o usa `stamp`. Nunca texto rojo sobre caja roja.
- **Higgsfield:**
  - el filtro NSFW da falsos positivos (tanques de réplicas, manos que se tocan). Reformula el prompt (siluetas tras vidrio esmerilado) o recorta el plano;
  - si un plano vertical llega rotado, regenera pidiendo "upright vertical composition".
- **Renders largos:** en entornos remotos los renders de más de 2 minutos pueden cortarse. Corre en segundo plano y revisa el archivo de salida (que tenga moov atom) antes de usarlo.
- **Costo:** un episodio completo de ALIAS con video generado es caro. Reutilizar material ya pagado y meter gráficos en post deja reels a costo cero.

## Vlogs
_(agrega aquí: qué gancho funcionó, retención, comentarios, qué faltó grabar)_
