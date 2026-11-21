# Estilo de edición actual de Sundesign (a replicar)

Analizado de "Tokio Septiembre V2.mp4" (reel de un sofá cama, 52 s, 1080×1920, 30 fps).

## Estructura
| Tramo | Qué pasa | Ejemplo del reel de referencia |
|---|---|---|
| 0–2 s **Gancho visual** | Imagen metáfora + subtítulo que nombra el problema | Puertas de ascensor + "Si vivís con poco espacio…" |
| 2–8 s **Presentador a cámara** | El vendedor habla a cámara con micrófono de solapa, en el showroom (paredes blancas con molduras) | "este truco oculto… es cualquier sofá" + título "COMPACTO Y ELEGANTE" |
| 8–15 s **Demostración** | Tomas del producto en uso, con título amarillo grande arriba | "ARMADO / EN 5 SEGUNDOS" mientras se abre el sofá cama |
| 15–35 s **Beneficios, uno por toma** | Cada beneficio con su toma: un nene con jugo (tela antimanchas), mano pasando (resistente), cierre de la funda (fácil de lavar), presentador sentado ("28 kilos, no se hunde") | Títulos "TELA ANTIMANCHAS", "FÁCIL DE LAVAR" |
| 35–42 s **Recorrido del producto** | Tomas generales del sofá, lentas | "Te esperamos en…" |
| 42–45 s **Logo** | Logo en círculo blanco aparece con "pop" en el centro, sobre el presentador | |
| 45–52 s **Oferta + cierre** | Presentador cuenta la promo; "20% OFF" gigante en negro aparece con animación | "20% pagando en efectivo", cuotas |

## Recursos visuales
- **Títulos**: amarillo `#F9D20A`, tipografía condensada muy gruesa (Anton), MAYÚSCULAS, arriba y centrados, con bajada chica en amarillo debajo ("EN 5 SEGUNDOS"). Aparecen de izquierda a derecha → estilo `titulo` + `bajada` (efecto `revelar`).
- **Subtítulos**: blancos, condensados en negrita (Oswald), con contorno negro, 2–3 palabras por vez, tercio inferior, minúscula normal → estilo `sub`, `subtitles: "auto"`.
- **Transiciones**: barridos con desenfoque de movimiento (whip) entre tomas → `transition_type: "barrido"`, 0.25–0.35 s.
- **Logo**: círculo blanco con lámpara amarilla, "SUNDESIGN · Tu hogar, nuestra pasión" → `stickers` con `assets/logo_circulo.png`.
- **Promo**: número gigante negro → estilo `promo` (efecto `pop`).
- Destellos (✦) sobre la tela para enfatizar "limpio" — no lo hace el script; sugerirlo como agregado en CapCut si se quiere.
- Audio: voz del presentador como protagonista, música baja de fondo (~-16 LUFS en el original; el script normaliza a -14, que es lo recomendado para redes).

## Cosas a corregir respecto del original (avisar al usuario)
- Los subtítulos del reel de referencia tenían errores: "Sungdesing" en lugar de **Sundesign**. El script corrige automáticamente variantes del nombre.
- Había frases en tuteo ("¿Quieres saber…?"). La marca habla con **voseo** ("¿Querés saber…?"). Si los subtítulos salen de la voz del presentador, se respeta lo que dice, pero los títulos y el caption van siempre en voseo.
- Duración: 52 s funciona, pero para alcance conviene probar también una versión de 20–30 s con los 3 beneficios más fuertes.

## Correcciones aprendidas
<!-- Claude agrega acá cada corrección del usuario: fecha · regla en una línea -->
- 2026-11-21 · Cuando habla el presentador, el título va a la altura del pecho (y ≈ 0.36–0.40), nunca sobre la cara.
