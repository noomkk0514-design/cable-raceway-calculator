# Generates the PWA icons (same cable cross-section as the header mark).
# Usage: powershell -File tools/make_icons.ps1 pwa/icons
param([string]$Out = "pwa/icons")
Add-Type -AssemblyName System.Drawing
$Out = (Resolve-Path $Out).Path

function New-Icon([int]$size, [double]$scale, [bool]$rounded, [string]$file) {
  $bmp = New-Object System.Drawing.Bitmap $size, $size
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = 'AntiAlias'
  $bg = [System.Drawing.Color]::FromArgb(24,35,45)
  if ($rounded) {
    $r = [int]($size * 0.22); $p = New-Object System.Drawing.Drawing2D.GraphicsPath
    $p.AddArc(0,0,2*$r,2*$r,180,90); $p.AddArc($size-2*$r-1,0,2*$r,2*$r,270,90)
    $p.AddArc($size-2*$r-1,$size-2*$r-1,2*$r,2*$r,0,90); $p.AddArc(0,$size-2*$r-1,2*$r,2*$r,90,90); $p.CloseFigure()
    $g.FillPath((New-Object System.Drawing.SolidBrush $bg), $p)
  } else { $g.Clear($bg) }
  $c = $size / 2; $u = $size * $scale / 44
  $ring = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(154,168,181)), ([single](2.5*$u))
  $cu = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(180,84,42))
  $core = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(233,165,127))
  $g.DrawEllipse($ring, [single]($c-20*$u), [single]($c-20*$u), [single](40*$u), [single](40*$u))
  foreach ($pt in @(@(15.5,17),@(28.5,17),@(22,28.5))) {
    $x = $c + ($pt[0]-22)*$u; $y = $c + ($pt[1]-22)*$u
    $g.FillEllipse($cu, [single]($x-6*$u), [single]($y-6*$u), [single](12*$u), [single](12*$u))
    $g.FillEllipse($core, [single]($x-3*$u), [single]($y-3*$u), [single](6*$u), [single](6*$u))
  }
  $bmp.Save((Join-Path $Out $file), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}
New-Icon 192 0.78 $true  "icon-192.png"
New-Icon 512 0.78 $true  "icon-512.png"
New-Icon 512 0.62 $false "icon-maskable-512.png"   # inside the 80% maskable safe zone
New-Icon 180 0.74 $false "apple-touch-icon.png"
"icons ok"
