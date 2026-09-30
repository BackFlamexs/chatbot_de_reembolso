#!/bin/bash
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then
    python3 iniciar.py "$@"
    resultado=$?
else
    echo "Instale Python 3.10 ou superior e tente novamente."
    resultado=1
fi
if [ "$resultado" -ne 0 ]; then
    echo "Consulte README_APRESENTACAO.md."
    read -r -p "Pressione Enter para fechar..."
fi
exit "$resultado"
