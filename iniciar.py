"""Inicializador para apresentacao no Windows e macOS."""

import argparse
import getpass
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

RAIZ = Path(__file__).resolve().parent
AMBIENTE = RAIZ / ".venv-apresentacao"


def preparar_ambiente():
    python = AMBIENTE / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        print("Preparando ambiente Python...", flush=True)
        subprocess.run([sys.executable, "-m", "venv", str(AMBIENTE)], check=True)
    requisitos = RAIZ / "requirements.txt"
    assinatura = hashlib.sha256(requisitos.read_bytes()).hexdigest()
    marcador = AMBIENTE / ".requirements-sha256"
    if not marcador.exists() or marcador.read_text() != assinatura:
        print("Instalando dependencias. A primeira abertura pode demorar...", flush=True)
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(requisitos)], check=True)
        marcador.write_text(assinatura)
    return python


def preparar_chave():
    arquivo = RAIZ / ".env"
    if not arquivo.exists():
        arquivo.write_text((RAIZ / ".env.example").read_text(encoding="utf-8-sig"), encoding="utf-8")
    texto = arquivo.read_text(encoding="utf-8-sig")
    chave = os.environ.get("GEMINI_API_KEY", "").strip()
    for linha in texto.splitlines():
        if not chave and linha.strip().startswith("GEMINI_API_KEY="):
            chave = linha.split("=", 1)[1].strip().strip("\"'")
    if chave and chave not in ("chave_api", "sua_chave_aqui"):
        return
    print("Informe sua chave Gemini. Ela sera salva no .env deste computador.")
    chave = getpass.getpass("Chave Gemini (entrada oculta): ").strip()
    if not chave or chave in ("chave_api", "sua_chave_aqui") or any(c.isspace() for c in chave):
        raise ValueError("Informe uma chave valida, sem espacos.")
    linhas = [linha for linha in texto.splitlines() if not linha.strip().startswith("GEMINI_API_KEY=")]
    arquivo.write_text("\n".join(linhas + ["GEMINI_API_KEY=" + chave]) + "\n", encoding="utf-8")
    os.environ["GEMINI_API_KEY"] = chave


def abrir_quando_pronto(processo, url):
    acesso = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(120):
        if processo.poll() is not None:
            return
        try:
            with acesso.open(url + "health", timeout=1) as resposta:
                if resposta.status == 200:
                    webbrowser.open(url)
                    return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(0.5)
    print("Acesse manualmente " + url, flush=True)


def main():
    parser = argparse.ArgumentParser(description="Abrir o chatbot para apresentacao.")
    parser.add_argument("--rede-local", action="store_true", help="Permitir acesso de dispositivos na mesma rede.")
    parser.add_argument("--porta", type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.porta <= 65535:
        parser.error("A porta deve estar entre 1 e 65535.")
    if sys.version_info < (3, 10):
        print("Instale Python 3.10 ou superior.")
        return 1
    processo = None
    try:
        host = "0.0.0.0" if args.rede_local else "127.0.0.1"
        with socket.socket() as teste:
            teste.bind((host, args.porta))
        preparar_chave()
        python = preparar_ambiente()
        url = f"http://127.0.0.1:{args.porta}/"
        print("\nAbrindo o Assistente de Reembolso: " + url, flush=True)
        print("Mantenha esta janela aberta. Pressione Ctrl+C para encerrar.", flush=True)
        if args.rede_local:
            print(f"Na mesma rede: http://IP-DO-COMPUTADOR:{args.porta}/ (veja o README).", flush=True)
        processo = subprocess.Popen(
            [str(python), "-m", "uvicorn", "main:app", "--host", host, "--port", str(args.porta)], cwd=str(RAIZ)
        )
        threading.Thread(target=abrir_quando_pronto, args=(processo, url), daemon=True).start()
        return processo.wait()
    except KeyboardInterrupt:
        print("\nEncerrando a apresentacao...")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as erro:
        print(f"\nFalha ao iniciar: {erro}")
        print("Confira README_APRESENTACAO.md. Se a porta estiver ocupada, use --porta 8001.")
        return 1
    finally:
        if processo is not None and processo.poll() is None:
            processo.terminate()
            try:
                processo.wait(timeout=5)
            except subprocess.TimeoutExpired:
                processo.kill()
                processo.wait()


if __name__ == "__main__":
    sys.exit(main())
