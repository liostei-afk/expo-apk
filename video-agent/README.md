# Agente editor de Reels / TikToks — Sundesign Muebles

Una **skill** para Claude (Cowork) que convierte videos crudos en Reels y TikToks verticales listos para publicar, con el estilo y la voz de marca de Sundesign.

## Qué hace
1. **Mira y escucha** el material: miniaturas de cada toma y transcripción palabra por palabra (gratis, sin internet).
2. **Limpia al presentador**: saca silencios, muletillas y frases repetidas (se queda con la última toma buena).
3. **Te propone un guion y un storyboard en imagen** (un cuadro por momento, con títulos y subtítulos) y espera tu OK.
4. **Edita con el estilo de la marca**: vertical 1080×1920, títulos amarillos, subtítulos palabra por palabra con la palabra que se dice en amarillo, barridos entre tomas, logo en círculo, promo gigante, música baja, efectos de sonido, volumen a -14 LUFS, placa de cierre con showroom y WhatsApp.
5. **Se revisa a sí mismo** con el video ya exportado: lo vuelve a transcribir para buscar repeticiones, mide pausas, volumen y formato, controla que no tape la cara y guarda cada versión (`_v1`, `_v2`…).
6. **Protege tu privacidad**: borra la ubicación GPS y el modelo del teléfono que guardan los videos del celular. Convierte solo los videos de iPhone en HDR.
7. **Aprende**: cada corrección que le hacés queda anotada en tu ficha de estilo para no repetirla.
8. Te da el **texto de la publicación** con la voz de la marca.

## App de escritorio (Windows): `estudio-app/`
Para que un operador trabaje sin escribirle a Claude: carga videos, guion y pedido; aprueba el storyboard; revisa, corrige y descarga el video final con su texto. También maneja una **biblioteca de estilos** con reels de referencia (para seguir las tendencias). Claude trabaja desde Cowork sobre la misma carpeta. Ver `estudio-app/LEEME.md`.

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
python3 sundesign-editor-reels/scripts/storyboard.py plan.json
python3 sundesign-editor-reels/scripts/render_reel.py plan.json
python3 sundesign-editor-reels/scripts/verify_reel.py "3 Listos/video_v1.mp4"
```
Requiere `ffmpeg`, `python3` y `pip install faster-whisper pillow`. Tipografías incluidas: Anton y Oswald (licencia OFL).
