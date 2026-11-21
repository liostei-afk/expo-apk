# Crea el ícono "Estudio de Reels" en el Escritorio y en el menú Inicio.
param([string]$dir = $PSScriptRoot)
$py = (Get-Command pyw.exe -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source }
if (-not $py) { Write-Host "No encontre Python (pyw.exe / pythonw.exe)."; exit 1 }
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
  $lnk.IconLocation = (Join-Path $dir 'icono.ico')
  $lnk.Description = 'Estudio de Reels - Sundesign Muebles'
  $lnk.Save()
}
Write-Host "Listo: icono creado en el Escritorio."
