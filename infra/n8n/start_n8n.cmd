@echo off
rem Arranca n8n con la API key de Anthropic cargada desde el .env del proyecto
rem (sin duplicar la key en ningun otro archivo)
for /f "usebackq tokens=1,* delims==" %%a in ("C:\Users\manup\projects\project-autopilot\.env") do (
  if "%%a"=="ANTHROPIC_API_KEY" set "ANTHROPIC_API_KEY=%%b"
)
set N8N_SECURE_COOKIE=false
echo n8n arrancando en http://localhost:5678 ...
n8n start
