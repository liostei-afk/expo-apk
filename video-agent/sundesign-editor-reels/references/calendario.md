# Calendario de contenido — Sundesign Muebles

El calendario no es una grilla que se llena a pulmón: es un **ritmo que se puede sostener**, con una estructura que se repite y hace que cada mes sea completar casilleros, no inventar de cero.

## Principios
1. **El ritmo se ajusta a la capacidad real del equipo** (`config.equipo`: quién filma, quién aparece en cámara, horas por semana, días de rodaje por mes, limitaciones). Cuentas orientativas: cada reel con presentador ≈ 1 a 1,5 h de rodaje en tanda + revisión; un carrusel ≈ 30 min; historias ≈ 10 min por día. Si lo configurado no entra en las horas o los días de rodaje, **decilo y proponé menos** (2 reels por semana es una base válida para empezar). Si nadie quiere salir en cámara, usá formatos sin presentador (manos, producto, voz en off, texto en pantalla).
2. **Público** (`config.publico`): todo se escribe para esas personas (sus problemas, su lenguaje, sus momentos). Si está vacío, avisá y usá: parejas y familias de CABA y GBA que se mudan, renuevan o reciben gente, muchas en departamentos chicos.
3. **Semana tipo (la base):** 2–3 reels por semana con **al menos 24 h entre reel y reel** (`config.min_horas_entre_reels`), **1 carrusel en un día sin reel** (`config.carrusel`), **4 o más historias por semana** y **1 día sin historias** (`config.historias`).
4. **Dos formatos fijos:** mientras la cuenta está creciendo, se eligen **2 formatos** y se repiten siempre en el mismo día (`config.formatos_fijos`, por ejemplo martes «Antes y después», jueves «Pregunta y respuesta», sábado otra vez «Antes y después»). **Lo que varía es el tema** (pilar, producto, enfoque), no el formato: así la audiencia aprende qué esperar y el equipo filma siempre parecido, que es más fácil. Si un día no tiene formato fijo, elegilo vos entre los 12 de `guionista-viral.md` y proponé fijarlo. Recién cuando haya resultados (8–10 publicaciones o más), sugerí probar un tercer formato.
5. **Esqueleto que se repite:** cada casillero es *pilar × formato × día*, no un video suelto. Así el operador sabe qué toca cada día.
6. **Una o dos series fijas** con nombre y día ("Lo armamos en 5 segundos" los martes): generan hábito en la audiencia y ahorran decisiones.
7. **Lugar para lo que surja:** dejá libre el % de `ritmo.reactivo` (20 % por defecto) para tendencias, novedades o algo que pase en el showroom. Un calendario 100 % cerrado no puede subirse a una tendencia.
8. **Promoción como minoría:** el pilar «Vení al showroom» (ofertas, showroom, envíos) no pasa del 10–20 % del mes. El resto es valor: ideas, demostraciones, fábrica, transformaciones.
9. **Variedad dentro de la repetición:** el formato se repite a propósito; lo que no se repite dos veces seguidas es el **producto**, el **pilar** ni el **enfoque**.

## Temas × enfoques (de dónde salen las ideas)
Cruzá cada pilar con 4 enfoques y ya hay ideas de sobra para el mes:
| Enfoque | Qué hace | Ejemplo (pilar «La mesa del encuentro») |
|---|---|---|
| **Enseñar** | tips, paso a paso, medidas | «Cuánto lugar necesitás para que entren 8» |
| **Romper una creencia** | mitos, errores | «3 errores al elegir sillas» |
| **Caso real** | cliente, resultado, antes/después | «Así quedó el comedor de un cliente» (solo con permiso y material real) |
| **Conectar** | historia, opinión, detrás de escena | «Por qué en Sundesign las mesas se prueban en el showroom» |
Con 4–5 pilares × 4 enfoques hay 16–20 ideas: más de las que hace falta para un mes. Cada pieza lleva su `enfoque`.

## Carrusel semanal
Formato `carrusel`, en el día configurado (sin reel ese día). Ideal para lo que se **guarda**: medidas, combinaciones, «3 errores», comparativas, ficha de un producto. En `notas` escribí el contenido: **portada** (gancho grande) + 5 a 8 placas (una idea por placa, texto corto) + placa final con CTA, y qué **foto** usar en cada una (de `productos/*/fotos`, `banco-de-material` o "foto a sacar"). Puede reutilizar el tema del reel de la semana (repurposing).

## Historias
No van como piezas sueltas: agregá **una pieza por semana** con `formato: "historia"`, `fecha` = lunes de esa semana, `titulo: "Historias de la semana"` y en `notas` la lista de 4+ historias con su día (respetando el día de descanso). Tipos que funcionan para Sundesign: compartir el reel del día, encuesta o pregunta («¿mesa redonda o rectangular?»), detrás de escena del showroom o la fábrica, novedad o llegada de producto, respuesta a una pregunta de un cliente, recordatorio de horario del showroom. Las historias son simples: celular, sin edición.

## Pilares (temas fijos)
Están en `calendario/config.json → pilares` (los edita el operador). Un pilar es un **tema** que la marca puede "tener", no una intención ("educativo") ni un formato ("detrás de escena"). La propuesta inicial:
| Pilar | % | Qué entra |
|---|---|---|
| **La mesa del encuentro** (pilar firma) | 40 | Mesas y sillas: elegir, combinar, recibir gente, medidas |
| Espacios chicos que rinden | 25 | Sofá camas, mesas extensibles, baulera: muebles que se transforman |
| Hecho en nuestra fábrica | 15 | Proceso, materiales, calidad de sofá camas y sillones de fábrica propia |
| Ideas para tu casa | 10 | Combinaciones, mesas ratonas, deco, armar un ambiente |
| Vení al showroom | 10 | Promos reales, showroom en Caballito, envíos |
Respetá los % del config (±10 puntos). Cada pieza lleva el `id` de su pilar.

## Fechas comerciales (momentos)
- Solo las que **encajan** con una mueblería: no cada "día nacional de…". En fechas sensibles o solemnes, nada de promoción.
- Planificá con anticipación: fechas grandes (Día de la Madre, Fiestas, Hot Sale, Black Friday/CyberMonday) **8 a 12 semanas antes**, como una serie de varios videos y no uno solo; fechas chicas, 2 a 4 semanas antes.
- Hot Sale, Black Friday y CyberMonday: solo con **promo real** (si no hay, proponé el video "si hay promo" y decilo en `notas`).
- Las fechas exactas cambian cada año: no inventes el día; si no lo sabés con certeza, poné el momento como "semana de…" en `notas` y avisá.
- Agregalas en `momentos` (aparecen como etiqueta amarilla en el calendario).

## Días de rodaje (producir en tanda)
Agrupá las piezas que se filman en el **mismo lugar** (sector comedor del showroom, fábrica, living) y proponé en `notas` de la primera pieza del grupo: "📹 Rodaje en tanda: filmar junto con las piezas del 5 y del 12". Un día de rodaje bien planificado alcanza para 2–3 semanas.

## Con qué se arma el plan del mes
1. `calendario/config.json` (ritmo, pilares, series) y el pedido del operador (`calendario/estado.json → pedido`).
2. Catálogo (`productos/`): lanzamientos (`nuevo`) y productos con pocos videos primero.
3. Lo que ya está en el calendario y en `trabajos/` (no duplicar; respetar piezas ya cargadas o publicadas).
4. **Resultados** de las piezas publicadas (`metricas`): los formatos, fórmulas y pilares que trajeron más **guardados, compartidos y consultas por WhatsApp** pesan más que las vistas. Con menos de 8–10 piezas publicadas no hay patrón todavía: decilo y no saques conclusiones.
5. Sugerencias pendientes (`sugerencias/sugerencias.json`) que sigan vigentes.
6. Fechas comerciales que caen en el mes o dentro de las próximas 8–12 semanas.

## Formato (`calendario/piezas.json`)
Agregá piezas a la lista existente (**no borres** las que ya están; si una no tiene sentido, sugerilo en el mensaje final):
```json
{"piezas": [
  {"id": "p2026120201", "fecha": "2026-12-02", "hora": "19:00", "formato": "reel", "canales": ["instagram", "tiktok"],
   "pilar": "mesa", "enfoque": "Caso real", "serie": "", "titulo": "Mesa para las Fiestas: entran todos",
   "gancho": "Mesa navideña para 4 que se estira para 8 cuando suena el timbre",
   "formula": "Antes / después", "producto_id": "", "producto": "Mesas extensibles",
   "objetivo": "Que vengan al showroom", "duracion": 24, "estado": "idea",
   "notas": "Por qué ahora + 📹 rodaje en tanda con la del 9/12"}
 ],
 "momentos": [{"fecha": "2026-12-24", "nombre": "Nochebuena", "nota": "Sin promo; última pieza de Fiestas el 21/12"}]}
```
- `id`: único, empezá con `p` + fecha + número (solo minúsculas y números).
- `formato`: `reel`, `carrusel` o `historia` (ver arriba). En los reels, `formula` y además el **formato de video** en `formato_video` (uno de los 12 de `guionista-viral.md`, respetando los formatos fijos del día).
- `estado`: siempre `idea` (después el operador crea el video desde el calendario y el estado avanza solo).
- `hora`: la habitual del ritmo. Los horarios son una guía general, **no** sacados de estadísticas (salvo que haya métricas reales que lo muestren).
- Al terminar: `calendario/estado.json` → `{"estado": "listo", "mes": "AAAA-MM", "actualizado": "AAAA-MM-DD HH:MM", "pedido": "<igual>"}` y un resumen en el chat: cuántas piezas por pilar, formatos fijos usados, carruseles, historias, series, fechas comerciales, días de rodaje propuestos y **si el plan entra en la capacidad del equipo** (horas y días de rodaje). Si `publico` o `equipo` están vacíos, pedí que los completen en «⚙️ Ritmo, formatos y equipo».

## Publicación y métricas
- Hoy el operador publica a mano y carga links y números en cada pieza (`links`, `metricas.instagram|tiktok` con vistas, me_gusta, comentarios, guardados, compartidos, seguidores; `metricas.consultas_whatsapp`).
- Si en Claude está conectado un programador de publicaciones (por ejemplo **Metricool**) y el operador lo pide, podés programar la pieza con el video final de `trabajos/<trabajo_id>/salida/` y el texto de `caption.md`, **siempre confirmando con el operador fecha, hora y redes antes de programar**; después poné la pieza en `programado`. Si el conector no permite subir el archivo, decilo y dejá todo listo para que lo programe a mano.
- Las métricas también se pueden traer del conector si está disponible; nunca inventes números.
