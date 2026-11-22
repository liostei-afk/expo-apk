# Plan de rodaje (storyboard de producción)

El plan de rodaje es lo que se le da a la gente que filma: **qué filmar, cómo y en qué orden**, toma por toma, para que el material que vuelva sea exactamente el que el guion necesita. Se escribe en `preproduccion/plan_rodaje.json` y se convierte en una hoja imprimible con dibujos con:

```bash
python3 <skill>/scripts/shotlist.py "trabajos/<id>/preproduccion/plan_rodaje.json"
```
(genera `plan_rodaje.html` al lado: se abre en la app, se imprime o se guarda como PDF para mandarlo por WhatsApp).

## Formato
```json
{
  "titulo": "La mesa que crece en 5 segundos",
  "producto": "Mesa extensible Nórdica + 8 sillas",
  "duracion": 25,
  "locacion": "Showroom Caballito, sector comedor",
  "quien_aparece": "Presentador (Pablo) + 4 personas",
  "orden_rodaje": [3, 4, 1, 2, 5],
  "preparar": ["Mesa cerrada y limpia, 4 sillas puestas y 4 al costado", "Vajilla para 8", "Luz: abrir cortinas, prender todas las luces del sector"],
  "tomas": [
    {"n": 1, "momento": "Gancho", "duracion": 3,
     "plano": "general", "angulo": "altura de ojos", "movimiento": "fija", "sujeto": "producto",
     "que_se_ve": "Mesa para 4 servida, llegan 4 amigos más por la izquierda",
     "accion": "El presentador tira de los extremos y la mesa se estira",
     "dice": "", "texto_pantalla": "¿Mesa para 4… o para 8?", "zona_texto": "arriba",
     "extra": "Grabar también la extensión sola, sin gente, 2 veces",
     "notas": "Que la mesa entre completa en el cuadro"}
  ]
}
```
| Campo | Valores |
|---|---|
| `plano` | `general` (ambiente completo), `medio` (persona de la cintura para arriba / mueble entero de cerca), `primer_plano` (cara / parte del mueble), `detalle` (textura, costura, mecanismo), `cenital` (desde arriba) |
| `angulo` | `altura de ojos`, `bajo` (desde abajo, agranda), `alto` (desde arriba), `cenital` |
| `movimiento` | `fija`, `acercarse`, `alejarse`, `paneo` (girar de costado), `seguimiento` (acompañar la acción), `giro` (alrededor del mueble) |
| `sujeto` | `presentador`, `producto`, `manos`, `ambiente` |
| `zona_texto` | dónde va a ir el texto en la edición: hay que **dejar ese lugar libre** al filmar (`arriba`, `abajo`, `ninguna`) |
| `dice` | texto **exacto** que dice el presentador en esa toma (vacío si no habla) |
| `extra` | tomas de seguridad o recursos (B-roll) para tener en edición |

## Reglas para escribir las tomas
- **Una toma = una acción**, de 2 a 6 s útiles. Pedí grabar **2 segundos antes y después** de la acción.
- Las tomas se numeran en el orden del guion, pero **se filman agrupadas por lugar/encuadre** (todo lo del sector comedor junto, todos los detalles juntos, todo lo del presentador junto): poné ese **orden de rodaje** en `orden_rodaje` (lista de números) y explicalo en `preparar`. Así se filma en una tarde lo de varios videos.
- Pedí **tomas de más del gancho** (3 o 4 versiones): es la toma más importante.
- Siempre al menos **3 tomas de detalle** del producto (terminaciones, textura, mecanismo) y **una toma general del ambiente** aunque el guion no las pida: salvan la edición.
- Si habla el presentador: frases cortas, **mirando a cámara**, y que repita la frase entera si se equivoca (el editor se queda con la última).
- Pensá dónde va a ir el texto: el producto y la cara nunca en la zona de texto.

## Reglas técnicas para los que filman (van impresas en la hoja)
- Celular **vertical**, cámara trasera, 1080p o 4K a 30 fps. En iPhone: Formatos → "Más compatible".
- Limpiar la lente. Luz de frente o de costado (ventana delante del sujeto, nunca detrás).
- Micrófono corbatero si alguien habla. Silencio en el lugar (aire, música, teléfonos).
- Pulso firme: apoyar el celular o usar trípode/gimbal. Movimientos lentos.
- Cada toma: **2 veces como mínimo**. Grabar 2 s antes y después.
- Al terminar: subir cada video **en el casillero de su toma** en la app (o nombrarlo `toma-03.mp4`).
