
@REM  Eu criei esse arquivo para poder abrir o projeto mais rapidamente sem ter que rodar os comandos somente para facilitar a abertura do projeto no Mac e no Windows pois nao sabia se teria algum problema ao abrir o projeto na maquina do Senac


@echo off
setlocal
cd /d "%~dp0"
title Assistente de Reembolso
where py >nul 2>nul
if not errorlevel 1 (
    py -3 iniciar.py %*
) else (
    python iniciar.py %*
)
if errorlevel 1 (
    echo.
    echo Confira a mensagem acima e o README_APRESENTACAO.md.
    pause
)
endlocal
