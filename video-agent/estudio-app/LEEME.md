# Estudio de Reels — Sundesign Muebles

App de escritorio (Windows) para que un operador cargue videos crudos, guion y reels de referencia, y siga la edición que hace **Claude en Cowork** hasta tener el video final para Instagram o TikTok.

## Instalar (una sola vez)
1. Copiá la carpeta `estudio-app` y la carpeta `sundesign-editor-reels` juntas, por ejemplo en `Documentos\Estudio de Reels\`.
2. Doble clic en **`instalar.bat`**. Si no hay Python, lo instala (después hay que volver a abrir `instalar.bat`).
3. Queda el ícono **Estudio de Reels** en el Escritorio. La primera vez crea la carpeta de trabajo `Documentos\Reels Sundesign`.
4. En Claude (app de escritorio): subí la skill `sundesign-editor-reels.zip` (Configuración → Capacidades → Skills) y, en **Cowork**, conectá la carpeta `Documentos\Reels Sundesign`. La primera vez pegá el texto de instalación de `sundesign-editor-reels/references/instalacion-cowork.md` para que instale ffmpeg y la transcripción.

## Usar
1. **Nuevo video** → arrastrá los crudos, pegá el guion, completá el pedido.
2. **Enviar a Claude** → tocá **📨 Avisar a Claude** y seguí los 3 pasos (el mensaje ya queda copiado: en Claude, Ctrl+V y Enter).
3. **Aprobá el storyboard** (o pedí cambios).
4. **Revisá el video**: marcá el segundo y escribí correcciones; cada una es una versión nueva.
5. **Descargá**, copiá el texto de la publicación, publicá y marcá "Ya lo publiqué".

**Estilos**: en la sección Estilos podés crear estilos nuevos con reels de referencia actuales (las tendencias cambian). Claude los analiza y arma una ficha; cada video usa el estilo que elijas.

Opcional: en Cowork, creá una tarea programada cada 30 minutos con el mensaje del aviso, así Claude revisa la cola solo.

## Detalles técnicos
- `app.py` es un servidor local (solo Python, sin dependencias) en `http://127.0.0.1:8765`, accesible únicamente desde esta PC. Se abre en una ventana de Edge en modo app.
- La comunicación con Claude es por archivos en la carpeta de trabajo: `COLA.md`, `trabajos/<id>/estado.json`, `salida/`. El protocolo está en `sundesign-editor-reels/references/protocolo-app.md`.
- Para cambiar la carpeta de trabajo: sección Ayuda → Cambiar carpeta (se guarda en `config.json`).
