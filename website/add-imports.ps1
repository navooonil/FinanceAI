$import = "import { EASE_OUT_EXPO } from `"@/lib/motion`";"
$files = Get-ChildItem -Path 'components' -Recurse -Filter '*.tsx'
foreach ($file in $files) {
  $content = [System.IO.File]::ReadAllText($file.FullName)
  if ($content -match 'EASE_OUT_EXPO' -and $content -notmatch 'from "@/lib/motion"') {
    # Insert after the last existing import line
    $lines = $content -split "`n"
    $lastImportIdx = -1
    for ($i = 0; $i -lt $lines.Length; $i++) {
      if ($lines[$i] -match '^import ') { $lastImportIdx = $i }
    }
    if ($lastImportIdx -ge 0) {
      $linesList = New-Object System.Collections.Generic.List[string]
      $linesList.AddRange($lines)
      $linesList.Insert($lastImportIdx + 1, $import)
      $newContent = $linesList -join "`n"
      [System.IO.File]::WriteAllText($file.FullName, $newContent)
      Write-Host ('Added import to: ' + $file.Name)
    }
  }
}
Write-Host 'All done'
