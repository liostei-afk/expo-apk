# Registro de Feria — Sundesign Muebles China

App de una sola página (`feria-china-tracker.html`) para registrar proveedores durante **CIFF** y **Furniture China 2026**. Pensada para funcionar 100% sin internet y sin depender de Claude/Anthropic (bloqueados en China sin VPN).

## Cómo funciona (importante)

- Todos los datos (fichas, fotos) se guardan **en el propio dispositivo**, en el almacenamiento local del navegador (IndexedDB). No hay servidor, no hay nube, no hay login.
- La app nunca necesita internet para cargar, guardar, editar o listar proveedores. Funciona igual con el celular en modo avión.
- La app **nunca** llama a ningún servicio de internet por su cuenta, ni pide API keys ni cuentas. Cuando quieras que la IA complete los datos de las tarjetas (empresa, teléfono, mail...), lo hacés compartiendo el backup JSON en un chat con Claude — ver más abajo.

## Instalación en el celular/tablet (antes de viajar, con internet normal)

En Android, si abrís el `.html` directo desde el Explorador de archivos / Files, Chrome muchas veces lo abre en una
ventana simplificada **sin el menú completo** — por eso no aparece "Agregar a pantalla de inicio". Hay dos formas de
instalarla, la B es la robusta (recomendada para el viaje):

### Opción A — rápida, sin configurar nada (funciona ya)

1. Descargá `feria-china-tracker.html` a tu celular.
2. Abrí la app **Chrome** primero (no el Explorador de archivos), tocá la barra de direcciones y escribí `file:///` —
   Chrome te muestra tus carpetas; navegá hasta el archivo descargado y abrilo desde ahí. Así se abre con la barra de
   Chrome completa y su menú entero.
3. Menú ⋮ (arriba a la derecha) → **"Agregar a pantalla de inicio"**.
4. Con este método el ícono se crea, pero al abrirlo se ve con la barra de Chrome (no pantalla completa tipo app) —
   funciona igual, guarda todo local.

### Opción B — instalación real de un toque, offline garantizado (recomendada)

Convertí la carpeta en un sitio (gratis, con GitHub Pages) para que Chrome la reconozca como app instalable de
verdad, con ícono propio y pantalla completa. Se hace **una sola vez, antes de viajar**:

1. En GitHub, andá al repo → **Settings → Pages**.
2. En "Build and deployment" → Source: **Deploy from a branch**. Elegí la rama `claude/mobile-app-china-trip-lz80j5`
   (o `main` si ya la mergeaste) y carpeta `/ (root)`. Guardar.
3. Esperá 1-2 minutos y GitHub te va a dar una URL tipo `https://TU-USUARIO.github.io/expo-apk/feria-china-tracker.html`.
4. Abrí esa URL en Chrome del celular. Al ratito Chrome va a mostrar (solo o en el menú ⋮) **"Instalar app"**. Tocalo.
5. Listo: ícono propio en pantalla de inicio, abre en pantalla completa como una app real, y queda **cacheada para
   andar sin internet** desde ese momento (por eso hay que hacer este paso con internet normal, antes de viajar).

Con cualquiera de las dos opciones: probá cargando una ficha de prueba **antes de viajar**, para confirmar que en tu
celular guarda bien. Una vez instalada, no hace falta volver a abrir nada desde claude.ai ni tener conexión.

## Rutina diaria en la feria

1. Cargá fichas de proveedores normalmente (foto de tarjeta, fotos de producto, valoración, notas). Todo queda guardado al toque, en el celular, sin conexión.
2. Si el celular se apaga o la app se cierra a mitad de una ficha, al volver a abrirla te va a preguntar si querés recuperar el borrador — no se pierde nada.
3. La app te avisa con un cartel si pasaron más de 6 horas sin hacer un backup.

## Backup al final del día (celular → PC)

1. Pestaña **Backup** → **Exportar JSON**. Esto descarga un archivo `proveedores_feria_backup_AAAA-MM-DD.json` con todas las fichas **y las fotos incluidas**.
2. Pasá ese archivo a tu PC (cable USB, Bluetooth, WhatsApp/Telegram a vos mismo, lo que tengas a mano — no necesita ser por internet "real", con que el archivo llegue alcanza).
3. Guardalo con fecha, por ejemplo en una carpeta `backups-feria/`.
4. El botón **Exportar CSV** genera además una planilla (sin fotos) para mirar rápido en Excel/Sheets — es solo para lectura, **no se puede volver a importar**.

## Procesar en la PC y volver a subir a la app

Como la app es un solo archivo HTML autocontenido, podés abrir **ese mismo archivo** en un navegador de la PC:

1. Abrí `feria-china-tracker.html` en Chrome/Edge/Firefox de tu PC.
2. Pestaña **Backup** → **Restaurar/fusionar backup (JSON)** → elegí el JSON que bajaste del celular. Ahora tenés todas las fichas del día en la PC, con teclado completo para revisar, tipear notas más largas, sacar duplicados, etc. (Cada edición que hagas y guardes actualiza la fecha interna de esa ficha.)
3. Cuando termines de procesar, andá de nuevo a **Exportar JSON** desde la PC.
4. Pasá ese archivo nuevo al celular y en la pestaña Backup del celular, **Restaurar/fusionar backup**, elegí ese JSON.

La importación es **segura para repetir**: compara fecha de última edición ficha por ficha y solo pisa una ficha local si la del backup es más nueva. Así, si mientras procesabas en la PC seguiste cargando proveedores nuevos en el celular, no se pierden — la fusión los deja intactos.

## Lectura de tarjetas con IA — capturá offline, completá los datos después

Sacar la foto de la tarjeta **nunca** depende de internet — eso se guarda siempre al toque. Cada ficha con foto (o
con texto pegado del OCR nativo, ver abajo) queda marcada **"⏳ IA pendiente"** hasta que se completen sus datos. No
se pierde nada por no tener conexión en la feria. La app no llama a ningún servicio de IA por su cuenta ni pide
ninguna cuenta o API key — todo el análisis se hace de una sola forma:

1. En **Backup → Exportar JSON**, bajá el backup completo (trae las fotos incluidas).
2. Cuando tengas Claude a mano (de vuelta en Buenos Aires, o con VPN en el hotel), abrí un chat y compartile ese
   archivo, pidiéndole que complete empresa/persona/teléfono/mail/WeChat/web de las fichas marcadas como pendientes.
3. Te va a devolver un JSON con esos datos completos. Volvé a la app → **Backup → Restaurar/fusionar backup (JSON)**
   → elegí ese archivo. Se fusiona solo, sin pisar nada más nuevo que hayas cargado mientras tanto.

En **Backup** la app te muestra cuántas fichas están pendientes en cualquier momento, así sabés cuántas te faltan
completar.

### Texto reconocido por el celular (OCR nativo del sistema)

La mayoría de los Android/iPhone pueden sacar el texto de una foto sin ninguna app ni internet: mantenés presionada
la foto en la Galería → **"Copiar texto"** (o usás Google Lens / Circle to Search). Pegá ese texto en el campo
**"Texto reconocido por el celular"** de la ficha:

- El botón **"Completar teléfono / mail con este texto"** busca el email, teléfono, web y WeChat con reglas simples
  **al instante, sin IA y sin conexión**, y te completa el campo de contacto.
- Ese mismo texto queda guardado con la ficha y es lo que usa el análisis por lote más tarde — cuando hay texto
  pegado, el análisis con IA lo usa a él (más rápido y confiable) en vez de la imagen.

## Notas técnicas

- Sin dependencias externas, sin CDN, sin build: es un único archivo HTML que corre en cualquier navegador moderno (Android, iOS, escritorio).
- Almacenamiento: IndexedDB para las fichas (sin límite práctico de tamaño) + `localStorage` para ajustes livianos (fecha del último backup, preferencias de OCR).
- Las fotos se comprimen automáticamente al cargarlas (tarjetas a 900px, fotos de producto a 700px, calidad ~70%) para no ocupar espacio de más.
