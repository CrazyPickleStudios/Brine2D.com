#Requires -Version 5.1
<#
.SYNOPSIS
	Validates that documentation source files are valid UTF-8.

.DESCRIPTION
	Scans .md, .yml, .yaml, .py, .js, .css and .html files under the given
	root directory (default: current directory) for invalid UTF-8 byte
	sequences, such as raw Windows-1252 characters (smart quotes, em dashes)
	that were pasted from Word without re-encoding.

	This scans documentation and config files for invalid UTF-8 byte
	sequences, such as raw Windows-1252 characters (smart quotes, em dashes)
	that were pasted from Word without re-encoding.

	Run this locally before committing, or as a CI step, to catch issues
	before they reach mkdocs build and cause a fatal UnicodeDecodeError.

.PARAMETER Root
	The root directory to scan. Defaults to the current directory.

.EXAMPLE
	./scripts/check_utf8.ps1
	./scripts/check_utf8.ps1 -Root docs
#>
param(
	[string]$Root = "."
)

$extensions = @(".md", ".yml", ".yaml", ".py", ".js", ".css", ".html")
$ignoredDirs = @(".git", ".venv", "venv", "site", "node_modules", "__pycache__")

$utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)

$files = Get-ChildItem -Path $Root -Recurse -File | Where-Object {
	$pathParts = $_.FullName -split '[\\/]'
	($extensions -contains $_.Extension.ToLowerInvariant()) -and
	-not ($pathParts | Where-Object { $ignoredDirs -contains $_ })
}

$errors = New-Object System.Collections.Generic.List[string]

foreach ($file in $files) {
	$bytes = [System.IO.File]::ReadAllBytes($file.FullName)
	try {
		$utf8Strict.GetString($bytes) | Out-Null
	} catch {
		$badOffset = -1
		for ($i = 0; $i -lt $bytes.Length; $i++) {
			if ($bytes[$i] -gt 127) {
				try {
					$utf8Strict.GetString($bytes[$i..[Math]::Min($i + 3, $bytes.Length - 1)]) | Out-Null
				} catch {
					$badOffset = $i
					break
				}
			}
		}
		$hex = if ($badOffset -ge 0) { "0x{0:x2}" -f $bytes[$badOffset] } else { "unknown" }
		$errors.Add("$($file.FullName): invalid UTF-8 byte $hex at offset $badOffset")
	}
}

if ($errors.Count -gt 0) {
	Write-Host "UTF-8 validation failed for the following files:" -ForegroundColor Red
	foreach ($e in $errors) {
		Write-Host "  - $e" -ForegroundColor Red
	}
	Write-Host ""
	Write-Host "Tip: these are often raw Windows-1252 characters (smart quotes, em dashes) pasted from Word. Re-save the file as UTF-8, or replace the offending characters with their proper UTF-8 equivalents." -ForegroundColor Yellow
	exit 1
}

Write-Host "All checked files are valid UTF-8." -ForegroundColor Green
exit 0
