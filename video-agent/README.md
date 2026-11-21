# Agente editor de Reels / TikToks — Sundesign Muebles

Una **skill** para Claude (Cowork, Claude Code o claude.ai) que convierte videos y fotos crudas de muebles en Reels y TikToks verticales listos para publicar, con la voz de marca de Sundesign.

## Qué hace
1. Mira tu material (hojas de contactos con miniaturas) y elige las mejores tomas.
2. Te propone un guion: gancho → demostración → detalles → cierre con WhatsApp/showroom.
3. Renderiza con ffmpeg: 1080×1920, recorte inteligente o fondo desenfocado, cámara lenta/rápida, zoom sobre fotos, textos con caja, subtítulos, logo, música que baja cuando hay voz, volumen normalizado para redes, placa final.
4. Revisa el resultado y te entrega el MP4 + caption + hashtags + sugerencia de portada.

## Instalación en Claude (Cowork / claude.ai)
1. Descargá `sundesign-editor-reels.zip`.
2. **Antes de subirlo**, agregá tu logo PNG transparente en `assets/` (y si querés, la tipografía en `assets/fonts/` y colores reales en `references/marca.json`), y volvé a comprimir la carpeta.
3. En Claude: **Configuración → Capacidades → Skills → Subir skill** y elegí el zip.
4. En Cowork, dale acceso a la carpeta donde tenés los videos y pedile: *"Armame un reel de la mesa extensible con los videos de esta carpeta"*.

## Uso manual (sin Claude)
```bash
python3 sundesign-editor-reels/scripts/inspect_media.py carpeta_videos --out inspeccion
python3 sundesign-editor-reels/scripts/render_reel.py plan.json
```
Ver `references/plan_ejemplo.json`. Subtítulos automáticos: `pip install faster-whisper`.
