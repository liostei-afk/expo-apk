# Registro de Feria — Sundesign Muebles China

App de una sola página (`feria-china-tracker.html`) para registrar proveedores durante **CIFF** y **Furniture China 2026**. Pensada para funcionar 100% sin internet y sin depender de Claude/Anthropic (bloqueados en China sin VPN).

## Cómo funciona (importante)

- Todos los datos (fichas, fotos) se guardan **en el propio dispositivo**, en el almacenamiento local del navegador (IndexedDB). No hay servidor, no hay nube, no hay login.
- La app nunca necesita internet para cargar, guardar, editar o listar proveedores. Funciona igual con el celular en modo avión.
- La única función que pide internet es la **lectura automática de tarjetas personales** (OCR con IA), y viene **desactivada por defecto**. Si la activás sin tener conexión, simplemente no hace nada y te deja completar los datos a mano — nunca traba la app.

## Instalación en el celular/tablet (antes de viajar, con internet normal)

1. Descargá `feria-china-tracker.html` a tu celular (por mail a vos mismo, Drive, cable, etc.).
2. Abrilo con el navegador (Chrome/Safari) directo desde el Explorador de archivos / Files.
3. En el menú del navegador, elegí **"Agregar a pantalla de inicio"**. Vas a tener un ícono como el de una app, en pantalla completa.
4. Probala una vez (cargá una ficha de prueba) **antes de viajar**, para confirmar que en tu celular guarda bien.

No hace falta Play Store, ni conexión, ni volver a abrir esto desde claude.ai una vez instalado.

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

## Lectura automática de tarjetas (opcional)

En pestaña **Backup › Ajustes** podés activarla y pegar tu propia API key de Anthropic (se guarda solo en ese dispositivo). Solo va a funcionar si en ese momento tenés internet real (por ejemplo WiFi del hotel con VPN activa). Si no tenés conexión, la app no intenta nada raro: guarda la foto y te deja completar los campos vos.

## Notas técnicas

- Sin dependencias externas, sin CDN, sin build: es un único archivo HTML que corre en cualquier navegador moderno (Android, iOS, escritorio).
- Almacenamiento: IndexedDB para las fichas (sin límite práctico de tamaño) + `localStorage` para ajustes livianos (fecha del último backup, preferencias de OCR).
- Las fotos se comprimen automáticamente al cargarlas (tarjetas a 900px, fotos de producto a 700px, calidad ~70%) para no ocupar espacio de más.
