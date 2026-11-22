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
│   ├── preproduccion/            ← ideas, guion viral, plan de rodaje, control (lo escribís vos)
│   ├── brutos/                   ← videos y fotos crudos (las tomas vienen como toma-03-xxx.mp4). NUNCA los modifiques
│   ├── salida/                   ← todo lo que generás vos
│   └── estado.json               ← estado + historial (lo leen la app y vos)
├── estilos/<id>/
│   ├── estilo.json               ← nombre, estado, notas del operador ("qué me gusta")
│   ├── referencias/              ← reels de referencia. NUNCA los modifiques
│   ├── estilo.md                 ← la ficha de estilo (la escribís vos)
│   └── muestra.jpg               ← muestra visual del estilo (la generás vos)
├── estilos/estilos.json          ← {"predeterminado": "<id>"}
├── productos/<id>/
│   ├── producto.json             ← ficha del producto (la carga el operador)
│   └── fotos/                    ← fotos y videos del producto
├── sugerencias/
│   ├── estado.json               ← {"estado": "pendiente"|"listo", "pedido": "..."}
│   └── sugerencias.json          ← lo escribís vos (ver references/agente-marketing.md)
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
| `ideas_listas` | Escribiste `preproduccion/ideas.json` + `ideas.md` |
| `guion_listo` | Escribiste `preproduccion/guion_viral.md` |
| `plan_listo` | Escribiste `preproduccion/plan_rodaje.json` y generaste `plan_rodaje.html` |
| `control_listo` | Escribiste `preproduccion/control_material.md` |
| `editando` | Al empezar un render largo (aprobado o corrección), para que el operador vea que estás trabajando |
| `storyboard_listo` | Terminaste guion propuesto + storyboard y esperás aprobación |
| `listo` | Video exportado, revisado (0 errores), con caption y resumen |
| `bloqueado` | Te falta algo imprescindible. Poné la pregunta en `"mensaje"` (corta, en lenguaje simple, con opciones). El operador responde y vuelve a la cola |

## Qué hacer según el estado (en COLA.md)

### Ficha del producto (siempre que el pedido tenga `producto_id`)
Antes de ideas, guion, plan o edición, leé `productos/<producto_id>/producto.json` y **mirá las fotos** de `productos/<producto_id>/fotos/`. Campos: `nombre`, `categoria`, `nuevo`, `fabrica_propia`, `descripcion`, `caracteristicas` (lista de `{c, beneficio, mostrar}`: cada característica con su beneficio para el cliente y cómo se muestra en video), `medidas`, `materiales`, `colores`, `precio` (solo se muestra si está cargado), `publico`, `diferenciales`, `objeciones` (dudas frecuentes de los clientes: son excelentes ganchos), `notas`.
- Las ideas y el guion se construyen sobre las **características y beneficios reales** de la ficha: cada beneficio fuerte puede ser un video entero.
- Las `objeciones` se responden mostrando, no diciendo ("¿entra por la puerta?" → se muestra entrando).
- En el plan de rodaje agregá `"foto_producto": "productos/<id>/fotos/<la mejor foto>"` (ruta relativa a la carpeta de trabajo) para que quienes filman vean el producto.
- Las fotos del producto pueden usarse como segmentos de foto en la edición.
- Si la ficha tiene un dato vacío que el guion necesita, usá `[COMPLETAR: …]` y no lo inventes.

### Sugerencias de contenido (`sugerencias/estado.json` en `pendiente`)
Seguí **`references/agente-marketing.md`**: mirá el catálogo, los trabajos hechos, la fecha y el pedido del operador; escribí `sugerencias/sugerencias.json` y dejá `estado.json` en `listo`. Cuando el operador elige una, la app crea un trabajo nuevo en `guion_pendiente` con la sugerencia en `pedido.json → idea_elegida`.

### Preproducción (crear el video desde cero)
Leé primero **`references/guionista-viral.md`** (sos el especialista en reels virales de Sundesign) y, para el plan, **`references/plan-de-rodaje.md`**. Leé el pedido completo (`producto`, `categoria`, `publico`, `objetivo`, `duracion`, `cierre`, `promo`, `quien_aparece`, `locacion`, `notas`), el historial y la ficha del estilo elegido.

- **`ideas_pendiente` → ideas:** 5 ideas con formatos distintos, aptas para filmar con lo que hay (`quien_aparece`, `locacion`). Si el operador pidió "otras ideas", leé su último mensaje y no repitas las anteriores. Escribí `preproduccion/ideas.json` (formato en guionista-viral.md) e `ideas.md` → `ideas_listas`.
- **`guion_pendiente` → guion:** la idea está en `pedido.json → idea_elegida` o, si el operador propuso la suya o pidió cambios, en el último mensaje del historial. Escribí `preproduccion/guion_viral.md` con 3 ganchos, la tabla del guion, la versión muda, el checklist de viralidad, la portada y el caption sugerido. Datos que no sepas: `[COMPLETAR: …]`, nunca inventados → `guion_listo`.
- **`plan_pendiente` → plan de rodaje:** a partir del guion aprobado, `preproduccion/plan_rodaje.json` (una toma por momento, más tomas de detalle y de ambiente, tomas extra del gancho, `orden_rodaje` agrupado por lugar) y corré `shotlist.py preproduccion/plan_rodaje.json` → `plan_listo`.
- **`control_pendiente` → control del material:** las tomas llegan a `brutos/` como `toma-NN-<nombre>`. Para cada toma del plan: `inspect_media.py` (duración, orientación, audio, hoja de contactos — miralas), transcribí las que tienen texto dicho y comparalo con `dice`. Revisá: ¿falta alguna toma? ¿es vertical? ¿dura lo suficiente? ¿se ve lo que pide el plan (encuadre, acción)? ¿luz (ventana detrás, oscuro)? ¿audio entendible? ¿quedó libre la zona de texto? Escribí `preproduccion/control_material.md`:
  ```
  # Control del material
  **Resultado:** ✅ Se puede editar  /  ⚠️ Se puede editar, pero conviene repetir 2 tomas  /  ❌ Hay que volver a filmar
  | Toma | Archivo(s) | Estado | Comentario |
  |---|---|---|---|
  | 1 · Gancho | toma-01-… | ✅ OK | La mejor es la 2.ª versión |
  | 3 · Demostración | — | ❌ Falta | … |
  ## Para la próxima vez
  - (1–3 consejos concretos de rodaje)
  ```
  Usá lenguaje simple: lo lee el operador → `control_listo`.
- Después del control, el operador aprueba y el trabajo pasa a **`aprobado`** (edición). En este flujo el operador ya aprobó guion y plan, así que **no hay storyboard de edición**: armá el `salida/plan.json` siguiendo el guion aprobado y el orden de las tomas (limpiando con `clean_takes.py` las tomas donde se habla y eligiendo la mejor versión de cada toma), renderizá, verificá y entregá como en `aprobado`.

### Edición

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
