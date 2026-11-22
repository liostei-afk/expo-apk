# Montar el estudio de edición en Cowork (una sola vez)

Necesitás: Claude de pago (Pro o superior) con la **app de escritorio** (Cowork trabaja con tus carpetas; la web no sirve para esto), una compu Mac o Windows y una tarde libre la primera vez.

## 1. Carpetas
Creá en tu compu una carpeta **MARKETING SUNDESIGN** y adentro estas tres:

```
MARKETING SUNDESIGN/
├── 1 Brutos        ← los videos tal cual los grabás
├── 2 Mi estilo     ← reels que te gustan y la ficha de estilo
└── 3 Listos        ← lo que te devuelve Claude, con su número de versión
```

## 2. Instalar la skill
En Claude: **Configuración → Capacidades → Skills → Subir skill** y elegí `sundesign-editor-reels.zip`.

## 3. Conectar la carpeta y dejar todo instalado
Abrí **Cowork**, empezá una tarea nueva, conectá la carpeta **MARKETING SUNDESIGN** y pegá este texto:

```
Hola, Claude. Quiero que esta carpeta sea el estudio de edición de reels de Sundesign. Usá la skill sundesign-editor-reels. Hacelo en este orden y avisame con una frase cada vez que termines un punto:

1. Fijate qué tengo y qué me falta para trabajar con video: FFmpeg, Python 3 y faster-whisper (para transcribir gratis y sin internet) y Pillow (para el storyboard). Instalá lo que falte. Bajá el modelo de transcripción large-v3-turbo.
2. Copiá la ficha de estilo de la skill (references/estilo_sundesign.md) a "2 Mi estilo/estilo.md".
3. Hacé una prueba real: un video vertical de 5 segundos con un título amarillo y un subtítulo, y guardalo en "3 Listos".
4. Escribí en la carpeta un archivo "COMO-FUNCIONA.md" con lo que instalaste y los pasos para volver a dejar todo listo si algún día falta algo.

Normas: todo tiene que ser gratis. Si algo pide pagar, una clave o crear una cuenta, pará y preguntame. Si algo falla, intentá arreglarlo vos y, si no podés, explicámelo sin tecnicismos.
```

¿Te pide permiso para instalar o descargar algo? Aceptá: está bajando las herramientas del punto 1.
¿Otro día algo no anda? Escribile: **"Leé COMO-FUNCIONA.md y dejá todo listo."**

## 4. Guardar las reglas
En las instrucciones de la carpeta en Cowork, pegá el contenido de `references/reglas-de-edicion.md` (una sola vez).

## 5. Para cada video
Poné el crudo en `1 Brutos` y escribí las 4 líneas de `references/plantilla-por-video.md`.

## (Opcional) Afinar el estilo con más referencias
Poné en `2 Mi estilo` entre 3 y 6 reels que te gusten (tuyos o de otras cuentas) y escribile:

```
Estudiá los videos de "2 Mi estilo": cómo empiezan, cómo son los subtítulos, cada cuánto cambia el plano, qué animaciones usan, qué colores se repiten y cómo suena la música frente a la voz. Después haceme una entrevista corta, una pregunta por vez, con opciones y tu recomendación marcada, sobre subtítulos, movimiento, música, colores, cómo arranco y cómo cierro, y qué no soporto ver en un reel. Con eso actualizá "2 Mi estilo/estilo.md". Si los videos son de otras cuentas, quedate con cómo se ven, nunca con lo que dicen ni con su marca. Lo que veas en un solo video no cuenta como estilo. Antes de guardar, mostrame la ficha y cómo editarías con ella un video mío de medio minuto, momento a momento.
```

## Antes de grabar
- **Buen sonido y buena luz.** El micrófono de solapa hace toda la diferencia. Una mala toma sigue siendo mala.
- **Si te equivocás, repetí la frase entera** desde el principio: el editor se queda con la última.
- **Dejá un segundo de silencio** antes y después de cada frase.
- Grabá en vertical y en "Más compatible" (H.264) si usás iPhone.
- La primera versión es un borrador: con un par de correcciones queda a tu gusto, y las siguientes ya salen mejor.
