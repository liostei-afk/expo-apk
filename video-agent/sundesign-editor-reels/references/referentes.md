# Análisis de referentes — qué replicar en Sundesign

El operador carga cuentas que le parecen interesantes: **competidores** (mueblerías de Argentina), **referentes del rubro** (mueblerías o marcas de deco de otros países) u **otro rubro** (una cuenta cuyo formato le gusta). Tu trabajo no es describir la cuenta: es encontrar **qué hace que funcione** y traducirlo a **algo que Sundesign pueda hacer con su equipo**.

## Dos compromisos
1. **Mecanismo, no superficie.** Copiar el audio, el tema o la estética reproduce ruido. Buscá los 1–2 elementos que de verdad sostienen el resultado (casi siempre: el gancho y la razón por la que se comparte).
2. **Honestidad sobre la suerte.** Mucho de lo viral es tamaño de cuenta, momento o azar. Si algo no es replicable, decilo. Una fórmula falsa es peor que ninguna.

## Con qué trabajás
- `referentes/<id>/referente.json`: usuario, red, tipo, seguidores, link y **por qué le interesa al operador** (empezá por ahí).
- `referentes/<id>/material/`: videos y/o capturas. **Nunca podés ver la cuenta en vivo**: analizá solo lo que hay y **nombrá lo que falta** ("sin video no puedo evaluar el ritmo ni el sonido").
- Videos: `inspect_media.py` (duración, cortes de escena → ritmo), mirá las hojas de contactos, y si hablan, `transcribe.py` para el texto y el gancho dicho. Capturas: leelas con atención (textos en pantalla, vistas en la grilla, comentarios visibles).
- Lo de Sundesign: ficha de estilo, `calendario/config.json` (público, **equipo y capacidad**, formatos fijos), catálogo (`productos/`).

## Cómo analizar cada video (una línea por capa)
| Capa | Qué mirar |
|---|---|
| Gancho | Qué se ve, qué se lee y qué se dice en el primer segundo y hasta el 3 |
| Formato | Cuál de los 12 de `guionista-viral.md` es (o uno nuevo, nombralo) |
| Fórmula | Cómo se arma el cuerpo (PAS, lista, antes/después…) |
| Ritmo | Cortes por segundo, duración, si cambia algo cada 2–3 s |
| Textos y subtítulos | Tamaño, ubicación, cuánto texto, palabra destacada |
| Razón para compartir | Por qué alguien se lo manda a otro: utilidad, sorpresa, identificación, humor |
| Cierre / CTA | Cómo invitan a escribir, comprar o visitar |
Después, la **prueba del contrafáctico**: "si le saco esto, ¿seguiría funcionando?". Lo que no se puede sacar es el motor; lo demás es accesorio.

## Replicabilidad (antes de proponer nada)
- **Tamaño de la cuenta:** una cuenta de 500 mil seguidores tiene vistas que Sundesign no va a tener; mirá proporciones (vistas de sus mejores videos frente a su promedio), no números absolutos.
- **Un solo video no es un patrón.** Buscá lo que se repite en 3 o más.
- **Momento o suerte:** si algo explotó por una noticia o una tendencia puntual, no es una fórmula.
- **Capacidad de Sundesign:** ¿se puede filmar con el equipo, el lugar y las horas que tiene (`config.equipo`)? ¿Requiere actores, drones, producción grande? Si no, adaptalo a algo más simple o descartalo.
- **Marca:** se toma el mecanismo, nunca su texto, su música, su logo ni su estética reconocible. Y las reglas de Sundesign mandan (voseo, sin "importado", fábrica propia, cierre a WhatsApp o showroom).

## Qué entregar
### `referentes/<id>/informe.md`
```
# @cuenta — análisis
**Tipo:** … · **Material analizado:** 4 videos + 1 captura de perfil · **Lo que no pude evaluar:** …
## En una frase
(qué hace que esta cuenta funcione)
## Lo que repiten (patrones en 3+ videos)
- …
## Video por video
| Video | Gancho | Formato | Ritmo | Por qué se comparte |
## Lo que NO es replicable (y por qué)
## Qué replicar en Sundesign
1. … (concreto: con qué producto, qué formato, quién lo filma, cuánto tiempo lleva)
2. …
## Cómo encaja con el equipo de Sundesign
(¿entra en las horas y días de rodaje? ¿quién aparece?)
```
### `referentes/<id>/propuestas.json`
```json
{"formatos": [{"nombre": "Pregunta y respuesta", "descripcion": "Responden una duda de cliente mostrando el producto", "ejemplo_sundesign": "¿Entra por la puerta? con el sofá cama Milán"}],
 "ideas": [{"titulo": "…", "gancho": "…", "formato": "…", "formula": "…", "producto_id": "", "producto": "…", "objetivo": "…", "duracion": 25, "por_que": "Mecanismo tomado de @cuenta: …"}],
 "estilo": {"resumen": "Cómo editan en 2–3 líneas", "notas": "Qué tomar para un estilo de edición de Sundesign"},
 "no_copiar": ["Sus videos con actores: no hay equipo para eso", "…"]}
```
- `formatos`: 1–3, solo los que se repiten en la cuenta y Sundesign puede sostener. Si coincide con uno de los 12, usá ese nombre exacto.
- `ideas`: 3–5, ya adaptadas a productos reales del catálogo (si hay `producto_id`, que exista en `productos/`).
- `estilo`: solo si la edición es distintiva y aprovechable; si no, omitilo.
- Al terminar: en `referente.json` poné `"estado": "listo"`, `"actualizado"` y agregá al `historial` `{"fecha", "evento": "Analizado por Claude", "texto": "resumen en una línea"}`.

## Comparativo (`referentes/comparativo.md`, cuando `referentes/estado.json` está en `pendiente`)
Con 2 o más cuentas analizadas: qué hacen **todas** (eso es casi una regla del rubro), qué hace **cada una distinto**, dónde está el **hueco** que Sundesign puede ocupar (lo que nadie hace bien), y un **orden de prioridades**: las 3 cosas para adoptar primero, con su costo en tiempo para el equipo. Al terminar: `referentes/estado.json` → `{"estado": "listo", "actualizado": "AAAA-MM-DD HH:MM"}`.
