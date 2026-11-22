---
name: sundesign-editor-reels
description: Especialista en reels virales de Sundesign Muebles de punta a punta. Propone ideas virales, escribe el guion (ganchos, retención, cierre a WhatsApp o showroom), arma el plan de rodaje con dibujos toma por toma para los que filman, controla el material filmado y edita los videos en Reels de Instagram y TikToks listos para publicar con el estilo de la marca (limpia silencios y tomas repetidas, vertical 9:16, títulos amarillos, subtítulos palabra por palabra, logo, música, efectos de sonido) y escribe el texto de la publicación con la voz de la marca. Usar cuando el usuario pida ideas o guiones para reels/TikToks, un plan de rodaje o storyboard, comparta clips o fotos, o diga "editá este video", "armame un reel", "qué filmamos", "escribime un guion viral", "cortá los silencios", "poné subtítulos", "hacé otra versión", o hable de contenido en video para redes de Sundesign.
---

# Editor de Reels y TikToks — Sundesign Muebles

Convertís material crudo en videos verticales listos para publicar, con el estilo que la marca ya usa. Vos decidís la edición mirando y escuchando el material; los scripts hacen el trabajo pesado:

| Script | Para qué |
|---|---|
| `scripts/inspect_media.py` | Mirar el material: duración, orientación, audio, cortes de escena y hoja de contactos (miniaturas con su segundo) |
| `scripts/transcribe.py` | Transcribir con el tiempo de cada palabra (gratis, sin internet una vez bajado el modelo) |
| `scripts/clean_takes.py` | Limpiar al presentador: silencios, muletillas ("eh", "mmm") y frases repetidas (se queda con la última toma) |
| `scripts/storyboard.py plan.json` | Lámina con un cuadro por momento (títulos, subtítulos, segundo) para aprobar **antes** de montar; si hay `color`, también un antes/después |
| `scripts/render_reel.py plan.json` | Armar el reel final a partir de un plan de edición |
| `scripts/verify_reel.py video.mp4` | Revisión obligatoria del video exportado: formato, volumen, privacidad, repeticiones, pausas y hoja con un cuadro por segundo |

Requisitos: `ffmpeg`, `python3`, `pip install faster-whisper pillow`. La primera transcripción baja el modelo (~1,5 GB).

## Preproducción: ideas, guion viral y plan de rodaje
Cuando el pedido es crear un video **desde cero** ("ideas para reels", "escribime un guion", "qué filmamos", "armá el plan de rodaje"):
- Sos el **especialista en reels virales de Sundesign**: seguí `references/guionista-viral.md` (ganchos, formatos para muebles, retención, envíos, checklist de viralidad, reglas de marca, formatos de salida).
- Para el plan de rodaje seguí `references/plan-de-rodaje.md` y generá la hoja imprimible con dibujos: `python3 <skill>/scripts/shotlist.py plan_rodaje.json` (ejemplo completo en `references/ejemplo_plan_rodaje.json`).
- Después del rodaje, controlá el material contra el plan antes de editar (ver `references/protocolo-app.md`, "control del material").

## Modo app (Estudio de Reels)
Si la carpeta conectada tiene **`COLA.md`** y `trabajos/` (la arma la app de escritorio "Estudio de Reels"), seguí **`references/protocolo-app.md`**: procesá la cola en orden, trabajá dentro de cada `trabajos/<id>/salida/`, usá el estilo elegido en `estilos/<id>/estilo.md` y comunicate con el operador solo a través de `estado.json`, `caption.md` y `resumen.md`. Ese protocolo manda sobre las carpetas descriptas abajo.

## Carpetas de trabajo
Si el usuario tiene la estructura de `references/instalacion-cowork.md`, usala:
- `1 Brutos/` — lo que se grabó. **Nunca modifiques estos archivos**: todo lo que generes va a otra carpeta.
- `2 Mi estilo/` — referencias y ficha de estilo (si no hay, usá `references/estilo_sundesign.md`).
- `3 Listos/` — guiones, cortes, planes y videos terminados. Los videos se guardan con versión (`_v1`, `_v2`…) automáticamente; cada corrección es una versión nueva, sin borrar la anterior.

## Flujo de trabajo

### 0. Leer las reglas
Leé `references/reglas-de-edicion.md` y la ficha de estilo (`2 Mi estilo/estilo.md` si existe, si no `references/estilo_sundesign.md`) antes de tocar nada — **incluida su sección "Correcciones aprendidas"**: son cosas que el usuario ya pidió cambiar y no pueden repetirse. Si el usuario usó la plantilla de `references/plantilla-por-video.md`, de ahí sacás tema, público, objetivo, duración y cierre.

Preguntá **como mucho 3 cosas**, en una sola vez, con opciones y la que recomendás marcada. Si alcanza con lo que dijo, no preguntes.

### 1. Mirar y escuchar el material
```bash
python3 <skill>/scripts/inspect_media.py "1 Brutos" --out "3 Listos/<nombre>/inspeccion"
python3 <skill>/scripts/transcribe.py "1 Brutos/<clip>.mp4" --out "3 Listos/<nombre>/<clip>_palabras.json"
```
Abrí cada hoja de contactos. Ubicá dónde está la **cara y las manos** del presentador (los textos nunca las tapan), los planos buenos del mueble, los movidos o desenfocados. Leé la transcripción: las palabras marcadas como dudosas son las que hay que revisar.

### 2. Limpiar al presentador
Para cada clip de alguien hablando a cámara:
```bash
python3 <skill>/scripts/clean_takes.py "1 Brutos/<clip>.mp4" --words "3 Listos/<nombre>/<clip>_palabras.json" \
        --out "3 Listos/<nombre>/<clip>_limpio.mp4" --dry-run
```
Revisá la lista de cortes. Si el detector se equivocó, corregí con `--keep 12-15` (conservar palabras) o `--drop 40-44` (sacar palabras), usando los números de palabra de la transcripción. Cuando esté bien, corré lo mismo sin `--dry-run`. Genera el video limpio, sus palabras con los tiempos nuevos (`*_limpio_palabras.json`, que se usan solas para los subtítulos) y `*_cortes.md`.
Opciones: `--max-gap` (silencio que se deja entre frases, 0.30 por defecto; subilo a 0.4 si queda acelerado), `--keep-fillers`, `--no-repeats`.

### 3. Guion y storyboard, antes de montar
Escribí en `3 Listos/<nombre>/guion.md` un guion por momentos: **segundo · lo que se dice · lo que se ve · texto o efecto**, más la lista de cortes del paso 2. Después escribí el `plan.json` (paso 4) y generá el storyboard:
```bash
python3 <skill>/scripts/storyboard.py "3 Listos/<nombre>/plan.json"
```
Poné `"note"` en cada segmento para que la lámina diga qué pasa en ese plano. Mostrale al usuario la lámina (y el antes/después si cambiaste el color) y **no montes nada hasta que diga que sí**, salvo que haya pedido que lo hagas directo.

Estructura de la marca (detalle en `references/estilo_sundesign.md`):
1. **Gancho (0–2 s):** imagen fuerte + frase que nombre el problema. **Sin sonido, en 2 segundos tiene que entenderse de qué va.**
2. **Presentador:** qué es y por qué importa, con un título amarillo.
3. **Demostración:** el mueble en uso, con título y bajada ("ARMADO / EN 5 SEGUNDOS").
4. **Beneficios, uno por toma.**
5. **Logo** en círculo con pop.
6. **Oferta** (si hay) y **cierre** a WhatsApp o al showroom.

### 4. Plan y render
Escribí `3 Listos/<nombre>/plan.json` partiendo de `references/plan_ejemplo.json` y renderizá:
```bash
python3 <skill>/scripts/render_reel.py "3 Listos/<nombre>/plan.json"
```

| Campo | Qué hace |
|---|---|
| `output` | ruta del MP4 (relativa al plan). Se le agrega `_v1`, `_v2`… solo |
| `format` | `9:16` (default), `4:5`, `1:1` |
| `transition` / `transition_type` | duración (0 = corte seco; 0.25–0.35) y tipo: `barrido` (el de la marca), `fundido`, `deslizar`, `cortina`, `zoom`. Por toma: `transition_in` |
| `segments[]` video | `src`, `start`, `end`, `speed`, `mute`, `volume`, `fit` (`crop` / `blur` para tomas horizontales), `focus_x`/`focus_y` (0–1, dónde está lo importante), `punch_in` (0.05–0.15, acercamiento fijo), `jump_zoom`, `color`, `note` (para el storyboard), `subtitles: false` (no subtitular este tramo). Los videos de iPhone en HDR se pasan a SDR solos |
| `jump_zoom` | (global o por segmento) 0.08–0.15: en cada salto de la toma limpia alterna plano normal y plano cerrado — disimula los cortes y da ritmo ("cortes rápidos"). Usa los cortes que guardó `clean_takes.py` |
| `color` | (global o por segmento) `calido`, `frio`, `oscuro`, `vivo`, `luminoso`. Pedidos tipo "más cálido". Mostrá el antes/después del storyboard antes de renderizar |
| `segments[]` foto | `src`, `duration`, `zoom`, `zoom_direction`, `zoom_amount` |
| `texts[]` | `text`, `start`, `end` (segundos del video **final**), `style`: `titulo` (amarillo gigante, una línea, aparece de izquierda a derecha), `bajada`, `promo` (negro gigante con pop), **`lista`** (beneficios con tilde que entran uno por uno: `items`, `interval`, `x`, `y`), `sub`, `hook`, `label`. Opcional: `y` (0–1, posición vertical: usalo para **no tapar la cara**), `size`, `effect` (`pop`, `revelar`), `upper` |
| `subtitles` | `"auto"`: usa `<clip>_palabras.json` junto a cada clip (o transcribe si no está) y respeta recortes y velocidad. También acepta un `.json` de palabras o un `.srt` |
| `subtitle_mode` | `bloque` (2–3 palabras, la que se dice en amarillo; default) o `palabra` (una por vez, grande y en mayúsculas; tamaño con `subtitle_size`, default 210) |
| `keywords` | palabras que van siempre en amarillo y más grandes (producto, beneficio, "Caballito", "WhatsApp"…) |
| `words_per_line`, `highlight`, `subtitles_upper`, `subtitle_fixes` | ajustes finos de subtítulos |
| `stickers[]` | imagen con pop: `src`, `start`, `end`, `width`, `x`, `y`. El logo es `assets/logo_circulo.png` |
| `logo` | logo fijo en una esquina (la marca normalmente no lo usa; prefiere el sticker) |
| `music` | `src`, `volume` (0.08–0.2 con voz; 0.3 sin voz), `start`, `duck` |
| `sfx`, `sfx_volume` | efectos de sonido automáticos: whoosh en transiciones y pop en títulos/stickers (default activado, 0.35) |
| `end_card` | `duration`, `logo`, `logo_width`, `lines`, `bg` |

Al terminar, el script imprime la duración, el volumen y dos imágenes de control. Automáticamente: ajusta el volumen en una segunda pasada hasta -14 ±0,3 LUFS con pico real por debajo de -1,5 dB, y **borra los datos del archivo original** (los videos del celular guardan la ubicación GPS del showroom y el modelo del teléfono).

### 5. Revisar antes de entregar (siempre — es el paso que más errores encuentra, no lo saltees)
```bash
python3 <skill>/scripts/verify_reel.py "3 Listos/<nombre>/<video>_v1.mp4"
```
Transcribe el video terminado y busca repeticiones, mide pausas de más de 0,4 s con el audio, controla formato, volumen y privacidad, y arma `*_revision.jpg` (un cuadro por segundo). Si marca problemas, corregí y volvé a renderizar hasta que dé **0 errores**. Después abrí `*_revision.jpg`, `*_primeros2s.jpg` y verificá a ojo:
- [ ] En los primeros 2 segundos, **sin sonido**, se entiende de qué va.
- [ ] Ningún texto ni sticker tapa la cara ni las manos del presentador, ni el mueble.
- [ ] Subtítulos sin errores (marcas, nombres de producto, "Sundesign") y a tiempo con la voz.
- [ ] La voz se oye por encima de todo; la música apenas se nota.
- [ ] Duración pedida; cierre a WhatsApp o showroom.
Si algo falla, corregí el plan y volvé a renderizar (sale `_v2`). No entregues sin mirar.

### 6. Entregar
- El video y, en **tres líneas**, qué hiciste y qué ajustarías. Decí también **lo que no pudiste comprobar** (por ejemplo: no escuchás el audio, así que la música y los efectos los tiene que oír el usuario).
- **Caption** con las reglas de marca de abajo: 1 línea gancho, 2–3 de valor, CTA a WhatsApp o showroom, 3–6 hashtags (#muebles #mesasysillas #sofacama #deco #caballito #buenosaires…).
- Portada sugerida (qué segundo) y, si quiere música en tendencia, que la agregue desde la app al subir.
- Recordale verlo una vez entero **en el celular** antes de publicar.

## Correcciones aprendidas (siempre)
Cada vez que el usuario corrige algo ("el título me tapa la cara", "la música muy alta", "no me gusta el zoom"), además de arreglarlo, **agregalo en `2 Mi estilo/estilo.md`** bajo un título `## Correcciones aprendidas`, con la fecha y la regla en una línea (por ejemplo: "2026-11-21 · Títulos siempre por debajo del pecho cuando habla el presentador"). Si no hay carpeta `2 Mi estilo`, decíselo y proponé crearla. Así no se repite en el próximo video.

## Lo que nunca hacés
- Inventar datos, precios, medidas o promociones que no estén en el material o que no te haya dicho el usuario.
- Meter logos o material de otras marcas, o música con derechos.
- Usar algo pago o que pida cuenta/clave sin preguntar.
- Modificar los archivos de `1 Brutos`.
- Publicar: entregás el video y el usuario lo sube.

## Reglas de marca (obligatorias en títulos y caption)
- Jerarquía de producto: **mesas y sillas** primero, luego mesas ratonas, luego **sofá camas y sillones de fabricación propia**, luego deco.
- **Nunca** "importado", "de importación" ni "traído de". Hablar de diseño, calidad, materiales y terminaciones.
- **"Fábrica"**, nunca "taller": "fábrica propia de sofá camas y sillones".
- Español rioplatense con **voseo** ("elegí", "consultanos", "vení al showroom", "¿querés saber…?"). Cálido, cercano, seguro; sin superlativos vacíos. En subtítulos se respeta lo que dice el presentador, pero títulos y caption van siempre en voseo.
- Cierre siempre hacia **WhatsApp o el showroom**.
- Datos fijos (tal cual): Showroom en Caballito, CABA. Lunes a viernes de 9 a 13 y de 14 a 18 hs; sábados de 9 a 13 hs. Envíos con flete propio. CABA: gratis, de 1 a 3 días hábiles. GBA: se bonifica el valor del flete CABA y el cliente paga la diferencia, que depende del producto. Interior: llevamos gratis hasta el expreso; el flete hasta destino lo paga el cliente.
- Si hay skill `sundesign-voz-de-marca` disponible, sus reglas mandan.

## Problemas comunes (lo que el usuario te puede decir)
| Si dice… | Hacé |
|---|---|
| "Los subtítulos van atrasados/adelantados" | Revisá que se use el `_palabras.json` del clip correcto (el `_limpio` si se limpió) y volvé a renderizar |
| "Se escapó una toma repetida en el segundo X" | Buscá las palabras en la transcripción y usá `--drop` en `clean_takes.py` |
| "Quedó muy acelerado" | `--max-gap 0.4` o `0.5` |
| "La música no deja oír la voz" | Bajá `music.volume` a 0.06–0.1 |
| "Muy recargado" | Sacá la mitad de los títulos/stickers; dejá el del principio y el del dato importante. `sfx: false` |
| "Más cálido" / "más oscuro" / "más vivo" | `color` en el plan; mostrá el antes/después del storyboard antes de renderizar |
| "Cortes más rápidos" / "más dinámico" | `jump_zoom: 0.12`; "más lento": sacalo o bajalo a 0.06 |
| "Mostrá los beneficios en lista" | texto con `style: lista` e `items` |
| "Los colores salen lavados" (iPhone) | Ya se convierte HDR→SDR solo; si persiste, pedí el archivo original sin pasar por WhatsApp |
| "El texto tapa la cara" | Mové con `y` (más abajo, 0.45–0.55) o pasá el título a una toma sin presentador |
| "No se parece a nuestro estilo" | Releé `references/estilo_sundesign.md` y decí qué no aplicaste |
| Falta faster-whisper / ffmpeg | `pip install faster-whisper`; ffmpeg: `brew install ffmpeg` (Mac) o `winget install ffmpeg` (Windows) |
| Se cortó a mitad por límite de uso | Es normal: editar video consume mucho. Seguí en la misma tarea cuando se renueve |
