# Agente editor de Reels / TikToks — Sundesign Muebles

Una **skill** para Claude (Cowork) que convierte videos crudos en Reels y TikToks verticales listos para publicar, con el estilo y la voz de marca de Sundesign.

## Qué hace
1. **Mira y escucha** el material: miniaturas de cada toma y transcripción palabra por palabra (gratis, sin internet).
2. **Limpia al presentador**: saca silencios, muletillas y frases repetidas (se queda con la última toma buena).
3. **Te propone un guion** por momentos y espera tu OK.
4. **Edita con el estilo de la marca**: vertical 1080×1920, títulos amarillos, subtítulos palabra por palabra con la palabra que se dice en amarillo, barridos entre tomas, logo en círculo, promo gigante, música baja, efectos de sonido, volumen a -14 LUFS, placa de cierre con showroom y WhatsApp.
5. **Se revisa a sí mismo** (primeros 2 segundos sin sonido, que nada tape la cara, subtítulos sin errores) y guarda cada versión (`_v1`, `_v2`…).
6. Te da el **texto de la publicación** con la voz de la marca.

## Cómo empezar
Seguí `sundesign-editor-reels/references/instalacion-cowork.md`. En resumen:
1. Subí `sundesign-editor-reels.zip` en Claude → Configuración → Capacidades → Skills.
2. Creá la carpeta `Reels Sundesign` con `1 Brutos`, `2 Mi estilo` y `3 Listos`, y conectala en Cowork.
3. Pegá el texto de instalación (una vez) y las reglas de `references/reglas-de-edicion.md` en las instrucciones de la carpeta.
4. Para cada video: 4 líneas, según `references/plantilla-por-video.md`.

## Uso manual (sin Claude)
```bash
python3 sundesign-editor-reels/scripts/transcribe.py crudo.mp4
python3 sundesign-editor-reels/scripts/clean_takes.py crudo.mp4
python3 sundesign-editor-reels/scripts/render_reel.py plan.json
```
Requiere `ffmpeg`, `python3` y `pip install faster-whisper`. Tipografías incluidas: Anton y Oswald (licencia OFL).
