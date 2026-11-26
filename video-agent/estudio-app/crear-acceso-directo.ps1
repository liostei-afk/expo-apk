# Crea el ícono "Estudio de Reels" en el Escritorio y en el menú Inicio.
param([string]$dir = $PSScriptRoot)
$py = (Get-Command pyw.exe -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source }
if (-not $py) { Write-Host "No encontre Python (pyw.exe / pythonw.exe)."; exit 1 }
# Windows a veces no muestra iconos guardados en Google Drive (G:): lo copiamos a la PC.
$icoLocal = Join-Path $env:LOCALAPPDATA 'SundesignApp'
New-Item -ItemType Directory -Force -Path $icoLocal | Out-Null
$ico = Join-Path $icoLocal 'icono.ico'
Copy-Item -Force (Join-Path $dir 'icono.ico') $ico
$ws = New-Object -ComObject WScript.Shell
$destinos = @(
  (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Estudio de Reels.lnk'),
  (Join-Path ([Environment]::GetFolderPath('Programs')) 'Estudio de Reels.lnk')
)
foreach ($d in $destinos) {
  $lnk = $ws.CreateShortcut($d)
  $lnk.TargetPath = $py
  $lnk.Arguments = '"' + (Join-Path $dir 'app.py') + '"'
  $lnk.WorkingDirectory = $dir
  $lnk.IconLocation = "$ico,0"
  $lnk.Description = 'Estudio de Reels - Sundesign Muebles'
  $lnk.Save()
}
Write-Host "Listo: icono creado en el Escritorio."
