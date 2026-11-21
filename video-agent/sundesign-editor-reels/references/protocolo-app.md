# Protocolo con la app "Estudio de Reels"

La app de escritorio (la usa un operador, no necesariamente técnico) ordena todo en una carpeta de trabajo y escribe
**`COLA.md`** con lo que te toca hacer. Vos trabajás sobre esa carpeta y le contestás a la app **solo a través de archivos**:
lo que escribís en `salida/` y en `estado.json` aparece en la pantalla del operador a los pocos segundos.

## Estructura
```
<carpeta de trabajo>/
├── COLA.md                       ← lo pendiente, en orden (lo genera la app)
├── trabajos/<id>/
│   ├── pedido.json               ← lo que pidió el operador (ver campos abajo)
│   ├── guion.md                  ← guion o puntos clave (puede estar vacío)
│   ├── brutos/                   ← videos y fotos crudos. NUNCA los modifiques
│   ├── salida/                   ← todo lo que generás vos
│   └── estado.json               ← estado + historial (lo leen la app y vos)
├── estilos/<id>/
│   ├── estilo.json               ← nombre, estado, notas del operador ("qué me gusta")
│   ├── referencias/              ← reels de referencia. NUNCA los modifiques
│   ├── estilo.md                 ← la ficha de estilo (la escribís vos)
│   └── muestra.jpg               ← muestra visual del estilo (la generás vos)
├── estilos/estilos.json          ← {"predeterminado": "<id>"}
└── musica/                       ← música libre de derechos
```

## Cómo actualizar `estado.json`
Leelo, cambiá `estado`, poné `actualizado` (`AAAA-MM-DD HH:MM`) y **agregá** (no borres) una entrada al `historial`:
```json
{"fecha": "2026-11-21 18:40", "quien": "claude", "evento": "Storyboard listo", "texto": "6 momentos, 28 s. Usé la toma 2 para la tela."}
```
Escribilo completo de una vez (no lo dejes a medio escribir). Estados que podés poner:

| Estado | Cuándo |
|---|---|
| `editando` | Al empezar un render largo (aprobado o corrección), para que el operador vea que estás trabajando |
| `storyboard_listo` | Terminaste guion propuesto + storyboard y esperás aprobación |
| `listo` | Video exportado, revisado (0 errores), con caption y resumen |
| `bloqueado` | Te falta algo imprescindible. Poné la pregunta en `"mensaje"` (corta, en lenguaje simple, con opciones). El operador responde y vuelve a la cola |

## Qué hacer según el estado (en COLA.md)

### `pendiente` → storyboard
1. Leé `pedido.json`, `guion.md`, el historial y el estilo elegido (`estilos/<pedido.estilo>/estilo.md`, incluida su sección **Correcciones aprendidas**). Si `pedido.estilo` está vacío, usá el predeterminado.
2. Trabajá **dentro de `salida/`**: inspección, transcripción y limpieza (`transcribe.py`, `clean_takes.py --out salida/<clip>_limpio.mp4`).
3. Escribí `salida/guion_propuesto.md` (momento por momento: segundo · lo que se dice · lo que se ve · texto/efecto, más la lista de cortes) y `salida/plan.json`.
4. `storyboard.py salida/plan.json` → tiene que quedar un archivo con `storyboard` en el nombre en `salida/` (y `antes_despues` si hay color).
5. Si `pedido.directo` es `true`, seguí directo con la edición (como `aprobado`). Si no, estado → `storyboard_listo`.

### `cambios_storyboard` → rehacer storyboard
El pedido de cambios está en el último mensaje del historial. Ajustá `plan.json`, regenerá el storyboard (sobrescribilo) → `storyboard_listo`.

### `aprobado` → editar
1. Estado → `editando`.
2. `render_reel.py salida/plan.json`. El `output` del plan tiene que ser un nombre simple dentro de `salida/` (ej. `"output": "sofa-nordico.mp4"`): el script le agrega `_v1`, `_v2`… y la app muestra todos los `*_vN.mp4`.
3. `verify_reel.py` sobre el video hasta **0 errores** (deja `*_revision.md` y `*_revision.jpg`, que la app muestra). Mirá la hoja de revisión.
4. Escribí `salida/caption.md`: **solo el texto listo para pegar** en Instagram/TikTok (gancho, valor, CTA a WhatsApp o showroom, hashtags). Nada de explicaciones ahí.
5. Escribí `salida/resumen.md`: 3 líneas de qué hiciste y qué ajustarías, más **qué no pudiste comprobar** (por ejemplo, el audio).
6. Estado → `listo`.

### `correccion` → nueva versión
El texto de la corrección está en el último mensaje del historial (puede traer marcas de tiempo `[0:12]` sobre la versión indicada en el evento). Aplicala, renderizá (sale la versión siguiente), verificá, actualizá `resumen.md` (qué cambió) y `caption.md` si corresponde → `listo`.
**Además** anotá la corrección como regla en `estilos/<estilo>/estilo.md`, sección `## Correcciones aprendidas` (fecha · regla en una línea), para no repetirla.

## Campos de `pedido.json`
| Campo | Uso |
|---|---|
| `titulo`, `producto`, `categoria`, `publico` | De qué es y para quién. Respetá la jerarquía de producto de la marca |
| `objetivo`, `cierre` | Para el cierre del video y del caption. "Que lo elija Claude" → WhatsApp + showroom |
| `duracion` | Duración máxima en segundos |
| `plataformas` | `instagram`, `tiktok` → 9:16 (un solo archivo sirve para ambas). `feed` → además una versión `format: "4:5"` con otro nombre (ej. `<nombre>-feed`). `corta` → además una versión de 15 s (`<nombre>-corta`) |
| `promo` | Promo real a mostrar (estilo `promo`). Si está vacío, **no inventes ninguna** |
| `estilo` | id de la carpeta de estilo a usar |
| `musica` | `""` = elegí de `musica/` (o sin música si no hay); `"sin"` = sin música; otro valor = ruta relativa a la carpeta de trabajo |
| `efectos` | Si viene vacío, decidí según el estilo. Si trae ítems, usá esos: `titulos`, `subtitulos`, `lista`, `zoom_cortes` (`jump_zoom`), `logo` (sticker), `promo_gigante`, `sonidos` (`sfx`) |
| `color` | `""`, `calido`, `luminoso`, `vivo`, `frio`, `oscuro` → `color` del plan |
| `directo` | `true` = no esperar aprobación del storyboard |
| `notas` | Indicaciones libres del operador. Tienen prioridad sobre el estilo |

## Estilos: `por_analizar` → ficha
1. `inspect_media.py estilos/<id>/referencias --out estilos/<id>/.analisis` y mirá todas las hojas de contactos. Si tienen voz, transcribí para ver ritmo de subtítulos. Medí cortes por segundo con los cortes de escena.
2. Leé `estilo.json → notas` (lo que le gusta al operador). Lo que aparece en un solo video no es estilo; tomá **cómo se ve**, nunca lo que dicen ni la marca de otros.
3. Escribí `estilos/<id>/estilo.md` con las mismas secciones que `references/estilo_sundesign.md` (estructura, recursos visuales, ritmo, subtítulos, música frente a voz, prohibidos) y al final un bloque:
   ````
   ## Parámetros para el plan
   ```json
   {"brand": {"font": "...", "font_titulos": "...", "color_acento": "#...", "color_texto": "#..."},
    "transition": 0.25, "transition_type": "barrido", "subtitle_mode": "bloque", "words_per_line": 3,
    "jump_zoom": 0.1, "sfx": true, "music_volume": 0.12}
   ```
   ````
   Usá solo tipografías gratuitas (Google Fonts); si el estilo pide una que no está en `assets/fonts`, descargala a `estilos/<id>/fuentes/` y usá `fonts_dir` en el plan. Conservá siempre las reglas de marca de Sundesign (voseo, CTA, sin "importado").
   Si el estilo ya tenía `## Correcciones aprendidas`, mantenelas.
4. Generá `estilos/<id>/muestra.jpg`: una imagen 9:16 con un cuadro de una referencia (o de un bruto de Sundesign) con el título, un subtítulo con palabra destacada y el logo, tal como quedarían con este estilo (podés usar `storyboard.py` con un plan mínimo).
5. En `estilo.json`: `estado` → `listo` y agregá al `historial` `{"fecha", "evento": "Analizado por Claude", "texto": "resumen en una línea"}`.

## Reglas
- Nunca modifiques `brutos/` ni `referencias/`. Nunca borres versiones anteriores.
- Nunca publiques nada: el operador descarga y publica.
- Si algo falla (falta ffmpeg, un archivo no abre), no dejes el trabajo en `editando`: poné `bloqueado` con un mensaje claro.
- Al terminar todo lo de la cola, contale al usuario en una línea por ítem qué hiciste.
