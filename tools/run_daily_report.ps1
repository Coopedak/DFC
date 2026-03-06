$root = Split-Path $PSScriptRoot -Parent
python "$root\tools\update_montague_report.py"
