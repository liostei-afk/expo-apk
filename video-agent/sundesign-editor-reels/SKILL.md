---
name: sundesign-editor-reels
description: Edita videos y fotos crudas de muebles en Reels de Instagram y TikToks listos para publicar para Sundesign Muebles (formato vertical 9:16, gancho en los primeros segundos, textos, subtítulos, logo, música y placa de cierre con llamada a WhatsApp o al showroom), y escribe el texto de la publicación con la voz de la marca. Usar cuando el usuario comparta clips o fotos y pida "armame un reel", "editá este video", "hacé un TikTok", "cortá esto para Instagram", "poné subtítulos", "hacé varias versiones", o cuando mencione contenido en video para redes de Sundesign.
---

# Editor de Reels y TikToks — Sundesign Muebles

Convertís material crudo (videos del celular, fotos de productos) en videos verticales listos para publicar. Vos decidís la edición mirando el material; `ffmpeg` hace el trabajo pesado a través de dos scripts:

- `scripts/inspect_media.py` — mira el material: duración, orientación, audio, cortes de escena y una **hoja de contactos** (JPG con miniaturas y su minuto:segundo).
- `scripts/render_reel.py plan.json` — renderiza el video a partir de un **plan de edición** en JSON.

Requisitos: `ffmpeg` y `python3`. Opcional: `pip install faster-whisper` para subtítulos automáticos.

## Flujo de trabajo

### 1. Entender el pedido (breve)
Si no está claro, preguntá en una sola vez: qué producto es, objetivo (mostrar producto, oferta, novedad, detrás de escena de la fábrica, testimonio), plataforma (Instagram, TikTok o ambas) y si hay precio u oferta a mencionar. Si el usuario ya dio suficiente, no preguntes: proponé.

### 2. Mirar el material
```bash
python3 <skill>/scripts/inspect_media.py <carpeta_del_material> --out <trabajo>/inspeccion
```
Abrí y **mirá cada hoja de contactos** (`*_contactos.jpg`). Anotá: los mejores planos (mueble entero, detalle de terminación, mecanismo en movimiento, ambiente armado), los momentos movidos o desenfocados para descartar, y dónde está el mueble dentro del cuadro (para `focus_x`). Si una zona interesa, sacá más cuadros con más detalle:
```bash
ffmpeg -ss 12 -to 18 -i clip.mp4 -vf "fps=2,scale=360:-2,tile=4x3" -frames:v 1 detalle.jpg
```

### 3. Proponer el guion antes de renderizar
Mostrale al usuario un guion corto, toma por toma, con tiempos. Estructura que funciona para muebles (15–30 s):
1. **Gancho (0–2 s):** la toma más llamativa + texto arriba que genere curiosidad o nombre un problema ("¿Mesa para 4 que se vuelve para 8?", "Así se abre este sofá cama").
2. **Demostración (2–15 s):** el mueble en uso: mecanismo, apertura, extensión, la gente sentándose. Tomas de 1,5–3 s, cortes con ritmo.
3. **Detalles (opcional):** materiales y terminaciones de cerca (madera, tapizado, costuras, patas).
4. **Cierre (2,5–3 s):** placa con logo + "Showroom en Caballito" + "Escribinos por WhatsApp".

Esperá el OK (o ajustes) antes de renderizar, salvo que el usuario haya pedido que lo hagas directo.

### 4. Escribir el plan y renderizar
Partí de `references/plan_ejemplo.json`. Campos:

| Campo | Qué hace |
|---|---|
| `output` | ruta del MP4 final (relativa al plan) |
| `format` | `9:16` (Reels/TikTok, por defecto), `4:5` (feed), `1:1` |
| `transition` | segundos de fundido entre tomas (0 = corte seco; 0.2–0.3 queda prolijo) |
| `segments[]` | las tomas, en orden |
| ─ video | `src`, `start`, `end` (segundos del original), `speed` (1.5–2 para acelerar armados), `mute`, `volume`, `fit`, `focus_x`/`focus_y` (0–1, dónde está el mueble), `punch_in` (0.05–0.15, acerca la toma para dar ritmo) |
| ─ foto | `src`, `duration`, `zoom` (Ken Burns, true por defecto), `zoom_direction` `in`/`out`, `zoom_amount` |
| `fit` | `crop` llena la pantalla recortando (default); `blur` muestra el cuadro entero sobre fondo desenfocado — usalo para tomas horizontales donde el mueble es ancho y no entra recortado |
| `texts[]` | `text`, `start`, `end` (en segundos **del video final**), `position` `top` (gancho, con caja) / `bottom` (etiqueta) / `center`; opcional `size` |
| `subtitles` | `"auto"` (transcribe con faster-whisper), ruta a un `.srt`, u omitir |
| `logo` | `src`, `position` (`top-right`…), `width`, `opacity`. Se oculta solo en la placa de cierre |
| `music` | `src`, `volume` (0.15–0.35), `start` (desde qué segundo de la canción), `duck` (baja la música cuando hay voz) |
| `end_card` | `duration`, `logo`, `lines` (la última va en color acento), `bg` |
| `brand` | pisa colores/fuente de `references/marca.json` para este video |

Cálculo de tiempos: con transición T, cada toma después de la primera empieza T segundos antes de que termine la anterior. Duración final ≈ suma de tomas − T × (cantidad de tomas − 1). El script imprime la duración real.

```bash
python3 <skill>/scripts/render_reel.py <trabajo>/plan.json
```

### 5. Revisar antes de entregar (siempre)
Abrí `*_preview.jpg` (6 cuadros del video final) y, si hace falta, sacá cuadros puntuales de los momentos con texto. Verificá:
- [ ] Los textos se leen y no tapan el mueble ni caen en la zona de la interfaz (abajo a la derecha están los botones de like/comentar).
- [ ] El mueble está centrado en las tomas recortadas (si no, ajustá `focus_x` o pasá a `fit: blur`).
- [ ] El gancho aparece desde el segundo 0.
- [ ] Duración: 15–30 s ideal, máximo 60 s salvo pedido.
- [ ] La placa de cierre tiene el CTA correcto.
Corregí el plan y volvé a renderizar si algo falla. No entregues sin mirar.

### 6. Entregar
- El MP4 final y la vista previa.
- **Texto de la publicación** (caption) siguiendo las reglas de marca de abajo: 1 línea gancho, 2–3 líneas de valor, CTA a WhatsApp o showroom, 3–6 hashtags relevantes (#muebles #mesasysillas #sofacama #decoracion #caballito #buenosaires…).
- Sugerencia de **portada** (qué segundo usar) y de **audio en tendencia** para elegir desde la app al subir (la música en tendencia no se puede incrustar: se elige en Instagram/TikTok).

## Variantes y lotes
Si piden "varias versiones" o "para las dos redes": hacé un plan por versión (por ejemplo, gancho distinto, o versión 15 s y 30 s) y renderizá todos. Para TikTok tolerá un tono un poco más directo y subtítulos siempre activados; para Instagram, cuidá más la estética y la portada.

## Reglas de marca (obligatorias en textos del video y caption)
- Jerarquía de producto: **mesas y sillas** primero, luego mesas ratonas, luego **sofá camas y sillones de fabricación propia**, luego deco.
- **Nunca** decir "importado", "de importación" ni "traído de". Hablar de diseño, calidad, materiales y terminaciones.
- Decir **"fábrica"**, nunca "taller": "fábrica propia de sofá camas y sillones".
- Español rioplatense con voseo ("elegí", "consultanos", "vení al showroom"). Cálido, cercano, seguro; sin superlativos vacíos.
- Cierre siempre hacia **WhatsApp o el showroom**.
- Datos fijos (usarlos tal cual):
  - Showroom en Caballito, CABA. Lunes a viernes de 9 a 13 y de 14 a 18 hs; sábados de 9 a 13 hs.
  - Envíos con flete propio. CABA: gratis, de 1 a 3 días hábiles. GBA: se bonifica el valor del flete CABA y el cliente paga la diferencia, que depende del producto. Interior: llevamos gratis hasta el expreso; el flete hasta destino lo paga el cliente.
- Si hay skill `sundesign-voz-de-marca` disponible, sus reglas mandan.

## Problemas comunes
- **"falta faster-whisper"**: instalá con `pip install faster-whisper`, o escribí vos un `.srt` si el usuario te pasa lo que se dice, o seguí sin subtítulos.
- **Fuente distinta a la esperada**: poné los `.ttf` en `assets/fonts/` (o `fonts_dir` en el plan) y que `font` coincida con el nombre de la familia.
- **Videos de iPhone (HDR/HEVC)**: funcionan; si los colores salen lavados, avisá y sugerí grabar en "Más compatible" (H.264).
- **Render lento**: es normal en clips 4K; 30 s de reel tardan 1–3 min.
