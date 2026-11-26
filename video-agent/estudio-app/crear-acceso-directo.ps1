# Crea el ícono "App Sundesign" en el Escritorio y en el menú Inicio.
param([string]$dir = $PSScriptRoot)
$py = (Get-Command pyw.exe -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source }
if (-not $py) { Write-Host "No encontre Python (pyw.exe / pythonw.exe)."; exit 1 }
# Windows a veces no muestra iconos guardados en Google Drive (G:): lo copiamos a la PC.
$icoLocal = Join-Path $env:LOCALAPPDATA 'SundesignApp'
New-Item -ItemType Directory -Force -Path $icoLocal | Out-Null
$ico = Join-Path $icoLocal 'icono.ico'
Copy-Item -Force (Join-Path $dir 'icono.ico') $ico
# Borra el icono viejo "Estudio de Reels" si existe.
foreach ($f in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
  Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $f 'Estudio de Reels.lnk')
}
$ws = New-Object -ComObject WScript.Shell
$destinos = @(
  (Join-Path ([Environment]::GetFolderPath('Desktop')) 'App Sundesign.lnk'),
  (Join-Path ([Environment]::GetFolderPath('Programs')) 'App Sundesign.lnk')
)
foreach ($d in $destinos) {
  $lnk = $ws.CreateShortcut($d)
  $lnk.TargetPath = $py
  $lnk.Arguments = '"' + (Join-Path $dir 'app.py') + '"'
  $lnk.WorkingDirectory = $dir
  $lnk.IconLocation = "$ico,0"
  $lnk.Description = 'App Sundesign - central de marketing'
  $lnk.Save()
}
Write-Host "Listo: icono creado en el Escritorio."
