$ErrorActionPreference = 'Stop'

$requirements = @(
    @{ Name = 'Python'; Command = 'python'; Args = @('--version') },
    @{ Name = 'FFmpeg'; Command = 'ffmpeg'; Args = @('-version') },
    @{ Name = 'FFprobe'; Command = 'ffprobe'; Args = @('-version') },
    @{ Name = 'Blender'; Command = 'blender'; Args = @('--version') },
    @{ Name = 'Git'; Command = 'git'; Args = @('--version') }
)

$results = foreach ($requirement in $requirements) {
    $resolved = Get-Command $requirement.Command -ErrorAction SilentlyContinue
    if (-not $resolved) {
        [pscustomobject]@{ Tool = $requirement.Name; Status = 'ausente'; Version = ''; Path = '' }
        continue
    }

    $version = ''
    $status = 'disponivel'
    try {
        $output = & $resolved.Source @($requirement.Args) 2>&1 | Select-Object -First 1
        $version = [string]$output
        if ($LASTEXITCODE -ne 0 -and $requirement.Name -eq 'Python') {
            $status = 'atalho_sem_runtime'
        }
    }
    catch {
        $status = 'encontrado_mas_nao_executa'
        $version = $_.Exception.Message
    }

    [pscustomobject]@{
        Tool = $requirement.Name
        Status = $status
        Version = $version
        Path = $resolved.Source
    }
}

$results | Format-Table -AutoSize

if ($results.Status -contains 'ausente' -or
    $results.Status -contains 'atalho_sem_runtime' -or
    $results.Status -contains 'encontrado_mas_nao_executa') {
    Write-Host ''
    Write-Host 'Ambiente incompleto. Nenhuma instalacao ou alteracao foi executada.'
    exit 1
}

Write-Host ''
Write-Host 'Ferramentas basicas encontradas.'

