@echo off
REM Script de instalação para Windows

echo ================================================
echo    Codebase Analyst - Script de Instalacao
echo ================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python nao encontrado!
    echo Por favor, instale Python 3.9 ou superior.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

REM Verificar pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X pip nao encontrado!
    echo Por favor, instale pip.
    pause
    exit /b 1
)

echo [OK] pip encontrado
echo.

REM Perguntar sobre ambiente virtual
set /p CREATE_VENV="Deseja criar um ambiente virtual? (recomendado) [S/n]: "
if "%CREATE_VENV%"=="" set CREATE_VENV=S

if /i "%CREATE_VENV%"=="S" (
    echo.
    echo Criando ambiente virtual...
    python -m venv venv

    echo [OK] Ambiente virtual criado
    echo.
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
    echo [OK] Ambiente virtual ativado
)

echo.
echo Instalando pacote...
pip install -e .

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo    [OK] Instalacao concluida com sucesso!
    echo ================================================
    echo.
    echo Proximos passos:
    echo.
    echo 1. Configure sua OPENAI_API_KEY:
    echo    set OPENAI_API_KEY=sk-sua-chave-aqui
    echo.
    echo    Ou crie um arquivo .env:
    echo    copy .env.example .env
    echo    REM Edite o arquivo .env com sua chave
    echo.
    echo 2. Execute o comando:
    echo    codebase-analyst --help
    echo.
    echo 3. Analise um projeto:
    echo    codebase-analyst .\meu-projeto
    echo.

    if /i "%CREATE_VENV%"=="S" (
        echo Nota: Para usar o comando novamente, ative o ambiente virtual:
        echo    venv\Scripts\activate.bat
        echo.
    )
) else (
    echo.
    echo X Erro na instalacao!
    pause
    exit /b 1
)

pause
