$exclude = @("venv", "maestro.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "maestro.zip" -Force