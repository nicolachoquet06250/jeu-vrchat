Add-Type -AssemblyName System.Drawing
$textureDir = Join-Path $PSScriptRoot '..\..\Assets\Billiard_Nocturne\Textures'
$bitmap = New-Object System.Drawing.Bitmap 1024,1024
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$cream = [System.Drawing.Color]::FromArgb(248,244,227)
$whiteBrush = New-Object System.Drawing.SolidBrush $cream
$inkBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(18,22,25))
$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center
$palette = @('#F6E23B','#234CAE','#B92827','#713994','#E77C20','#167C57','#782B28','#151C22')
for ($ball = 0; $ball -lt 16; $ball++) {
    $tileX = ($ball % 4) * 256
    $tileY = [math]::Floor($ball / 4) * 256
    $graphics.FillRectangle($whiteBrush,$tileX,$tileY,256,256)
    if ($ball -eq 0) { continue }
    $color = [System.Drawing.ColorTranslator]::FromHtml($palette[($ball-1)%8])
    $brush = New-Object System.Drawing.SolidBrush $color
    if ($ball -lt 9) { $graphics.FillRectangle($brush,$tileX,$tileY,256,256) }
    else { $graphics.FillRectangle($brush,$tileX,($tileY+85),256,86) }
    foreach ($offset in @(64,192)) {
        $graphics.FillEllipse($whiteBrush,($tileX+$offset-21),($tileY+88),42,80)
        $fontSize = if ($ball -gt 9) { 25 } else { 34 }
        $font = New-Object System.Drawing.Font 'Arial',$fontSize,([System.Drawing.FontStyle]::Bold),([System.Drawing.GraphicsUnit]::Pixel)
        $rectangle = New-Object System.Drawing.RectangleF ($tileX+$offset-24),($tileY+88),48,80
        $graphics.DrawString([string]$ball,$font,$inkBrush,$rectangle,$format)
        $font.Dispose()
    }
    $brush.Dispose()
}
$bitmap.Save((Join-Path $textureDir 'Balls_BaseColor.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
$whiteBrush.Dispose()
$inkBrush.Dispose()
$format.Dispose()
