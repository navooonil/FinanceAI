$pattern = '\[0\.16, 1, 0\.3, 1\]'
$replace = 'EASE_OUT_EXPO'
$files = Get-ChildItem -Path 'components' -Recurse -Filter '*.tsx'
foreach ($file in $files) {
  $content = [System.IO.File]::ReadAllText($file.FullName)
  if ($content -match $pattern) {
    $newContent = [System.Text.RegularExpressions.Regex]::Replace($content, $pattern, $replace)
    [System.IO.File]::WriteAllText($file.FullName, $newContent)
    Write-Host ('Fixed: ' + $file.Name)
  }
}
Write-Host 'All done'
