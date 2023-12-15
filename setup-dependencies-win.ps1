$dependencies = [ordered] @{
    'poppler' = @{
        url = 'https://github.com/oschwartz10612/poppler-windows/releases/download/v23.11.0-0/Release-23.11.0-0.zip';
        sha256 = '614BABE4F96263D351A047A0AD32AA5EEB23435A614E2696B5D70414FCEBC405';
        dest_dir = 'env/deps/poppler';
        dest_name = 'poppler.zip'
    };
    # Used to extract files from the tesseract installer.
    '7z' = @{
        url = 'https://github.com/peazip/PeaZip/releases/download/9.6.0/peazip_portable-9.6.0.WIN64.zip';
        sha256 = '654D0098C790D00B1AB1D7B4D6C59A854E4CCB30EEEB868906C98823FC44BEF3';
        dest_dir = 'env/deps/7z';
        dest_name = '7z.zip'
    };
    'tesseract' = @{
        url = 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe';
        sha256 = '79AF1F9153B8FF988BAFFAA164FC70799950078F887E2C93DC3FA7EFED674B21';
        dest_dir = 'env/deps/tesseract';
        dest_name = 'tesseract-setup.exe'
    };
    'tesseract-por' = @{
        url = 'https://github.com/tesseract-ocr/tessdata/raw/4.1.0/por.traineddata';
        sha256 = '016C6A371BB1E4C48FE521908CF3BA3D751FADE0AB846AD5D4086B563F5C528C';
        dest_dir = 'env/deps/tesseract/tessdata';
        dest_name = 'por.traineddata'
    }
}

$ErrorActionPreference = 'Stop'
$first = $True
$deps_counter = 0
$deps_total = $($dependencies.Count)

foreach ($dep in $dependencies.Keys) {
    $details = $dependencies[$dep]
    $dest_path = "$($details['dest_dir'])/$($details['dest_name'])"
    $deps_counter++

    if ($first) {
        $first = $False
    } else {
        Write-Output ''
    }

    if (Test-Path -Path $details['dest_dir']) {
        Write-Host "[$deps_counter/$deps_total] [$dep] Removing existing directory '$($details['dest_dir'])' ... " -NoNewline
        Remove-Item -Recurse $details['dest_dir'] -ErrorAction Stop
        Write-Output 'OK'
    }
    Write-Host "[$deps_counter/$deps_total] [$dep] Downloading file '$($details['dest_name'])' to '$($details['dest_dir'])' ... " -NoNewline
    New-Item -Force -Type Directory $details['dest_dir'] | Out-Null
    Invoke-WebRequest -Uri $details['url'] -OutFile $dest_path
    Write-Output 'OK'

    Write-Host "[$deps_counter/$deps_total] [$dep] Verifying integrity of '$($details['dest_name'])' ... " -NoNewline
    if ((Get-FileHash -Algorithm SHA256 $dest_path).Hash -ieq $details['sha256']) {
        Write-Output 'OK'
        $exists = $True
    } else {
        Write-Output 'FAILED'
        Write-Output "`nStopping."
        Exit 1
    }

    $ok = $Null
    if ($dep -ieq 'poppler') {
        Write-Host "[$deps_counter/$deps_total] [$dep] Extracting archive '$($details['dest_name'])' to '$($details['dest_dir'])' ... " -NoNewline
        & tar -C $details['dest_dir'] -f $dest_path --include='*/bin/*' -x --strip-components 3
        $ok = $LASTEXITCODE -eq 0
    }
    if ($dep -ieq '7z') {
        Write-Host "[$deps_counter/$deps_total] [$dep] Extracting archive '$($details['dest_name'])' to '$($details['dest_dir'])' ... " -NoNewline
        & tar -C $details['dest_dir'] -f $dest_path --include='*/7z.exe' --include='*/7z.dll' -x --strip-components 4
        if ($LASTEXITCODE -eq 0) {
            # Prepend 7z's dest dir to PATH
            $env:PATH = (Resolve-Path $details['dest_dir']).Path + [IO.Path]::PathSeparator + $env:PATH
            $ok = $True
        }
    }
    if ($dep -ieq 'tesseract') {
        Write-Host "[$deps_counter/$deps_total] [$dep] Extracting executable '$($details['dest_name'])' to '$($details['dest_dir'])' ... " -NoNewline
        & 7z x $dest_path "-o$($details['dest_dir'])" | Out-Null
        $ok = $LASTEXITCODE -eq 0
    }
    if ($ok -eq $True) {
        Write-Output 'OK'
        Remove-Item $dest_path
    } elseif ($ok -eq $False) {
        Write-Output 'FAILED'
        Write-Output "`nStopping."
        Exit 1
    }
}

Write-Output "`nDone."
