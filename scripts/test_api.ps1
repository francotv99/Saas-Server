# Script de prueba para la API TaskFlow SaaS

Write-Host "=== TaskFlow SaaS API Test Script ===" -ForegroundColor Cyan
Write-Host ""

# 1. Registrar usuario y organización
Write-Host "1. Registrando usuario y organización..." -ForegroundColor Yellow
$registerBody = @{
    email = "test@gmail.com"
    password = "test123"
    full_name = "Franco Torres"
    organization_name = "Test Org"
    organization_slug = "test-org"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerBody
    
    Write-Host "✅ Registro exitoso!" -ForegroundColor Green
    Write-Host "Token: $($registerResponse.access_token)" -ForegroundColor Gray
    $token = $registerResponse.access_token
} catch {
    Write-Host "❌ Error en registro: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
    exit
}

Write-Host ""

# 2. Login
Write-Host "2. Haciendo login..." -ForegroundColor Yellow
$loginBody = @{
    email = "test@gmail.com"
    password = "test123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody
    
    Write-Host "✅ Login exitoso!" -ForegroundColor Green
    $token = $loginResponse.access_token
} catch {
    Write-Host "❌ Error en login: $($_.Exception.Message)" -ForegroundColor Red
    exit
}

Write-Host ""

# 3. Obtener información del usuario actual
Write-Host "3. Obteniendo información del usuario..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $userInfo = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
        -Method GET `
        -Headers $headers
    
    Write-Host "✅ Usuario obtenido:" -ForegroundColor Green
    $userInfo | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 4. Crear una tarea
Write-Host "4. Creando una tarea..." -ForegroundColor Yellow
$taskBody = @{
    title = "Mi primera tarea"
    description = "Esta es una tarea de prueba creada desde PowerShell"
    priority = "high"
    status = "todo"
} | ConvertTo-Json

try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $task = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks" `
        -Method POST `
        -ContentType "application/json" `
        -Headers $headers `
        -Body $taskBody
    
    Write-Host "✅ Tarea creada:" -ForegroundColor Green
    $task | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}

Write-Host ""

# 5. Listar tareas
Write-Host "5. Listando tareas..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $tasks = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks?page=1&page_size=10" `
        -Method GET `
        -Headers $headers
    
    Write-Host "✅ Tareas obtenidas:" -ForegroundColor Green
    Write-Host "Total: $($tasks.total), Página: $($tasks.page)" -ForegroundColor Gray
    $tasks.items | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Pruebas completadas ===" -ForegroundColor Cyan
