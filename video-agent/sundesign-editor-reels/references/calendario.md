# Calendario de contenido — Sundesign Muebles

El calendario no es una grilla que se llena a pulmón: es un **ritmo que se puede sostener**, con una estructura que se repite y hace que cada mes sea completar casilleros, no inventar de cero.

## Principios
1. **El ritmo se ajusta a la capacidad real.** Mejor 3 reels por semana todo el año que 7 durante un mes. Si el pedido o el ritmo configurado no se pueden sostener (rodaje, edición, aprobación), decilo y proponé menos.
2. **Esqueleto que se repite:** cada casillero es *pilar × formato × día*, no un video suelto. Así el operador sabe qué toca cada día.
3. **Una o dos series fijas** con nombre y día ("Lo armamos en 5 segundos" los martes): generan hábito en la audiencia y ahorran decisiones.
4. **Lugar para lo que surja:** dejá libre el % de `ritmo.reactivo` (20 % por defecto) para tendencias, novedades o algo que pase en el showroom. Un calendario 100 % cerrado no puede subirse a una tendencia.
5. **Promoción como minoría:** el pilar «Vení al showroom» (ofertas, showroom, envíos) no pasa del 10–20 % del mes. El resto es valor: ideas, demostraciones, fábrica, transformaciones.
6. **Variedad:** que no se repitan el mismo formato, la misma fórmula ni el mismo producto dos días seguidos.

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
   "pilar": "mesa", "serie": "", "titulo": "Mesa para las Fiestas: entran todos",
   "gancho": "Mesa navideña para 4 que se estira para 8 cuando suena el timbre",
   "formula": "Antes / después", "producto_id": "", "producto": "Mesas extensibles",
   "objetivo": "Que vengan al showroom", "duracion": 24, "estado": "idea",
   "notas": "Por qué ahora + 📹 rodaje en tanda con la del 9/12"}
 ],
 "momentos": [{"fecha": "2026-12-24", "nombre": "Nochebuena", "nota": "Sin promo; última pieza de Fiestas el 21/12"}]}
```
- `id`: único, empezá con `p` + fecha + número (solo minúsculas y números).
- `estado`: siempre `idea` (después el operador crea el video desde el calendario y el estado avanza solo).
- `hora`: la habitual del ritmo. Los horarios son una guía general, **no** sacados de estadísticas (salvo que haya métricas reales que lo muestren).
- Al terminar: `calendario/estado.json` → `{"estado": "listo", "mes": "AAAA-MM", "actualizado": "AAAA-MM-DD HH:MM", "pedido": "<igual>"}` y un resumen en el chat: cuántas piezas por pilar, series, fechas comerciales y días de rodaje propuestos.

## Publicación y métricas
- Hoy el operador publica a mano y carga links y números en cada pieza (`links`, `metricas.instagram|tiktok` con vistas, me_gusta, comentarios, guardados, compartidos, seguidores; `metricas.consultas_whatsapp`).
- Si en Claude está conectado un programador de publicaciones (por ejemplo **Metricool**) y el operador lo pide, podés programar la pieza con el video final de `trabajos/<trabajo_id>/salida/` y el texto de `caption.md`, **siempre confirmando con el operador fecha, hora y redes antes de programar**; después poné la pieza en `programado`. Si el conector no permite subir el archivo, decilo y dejá todo listo para que lo programe a mano.
- Las métricas también se pueden traer del conector si está disponible; nunca inventes números.
