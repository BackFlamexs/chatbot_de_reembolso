# Como rodar

Com Python instalado, abra o PowerShell na pasta do `main.py` e execute:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

No `.env`, coloque sua chave do Gemini:

```dotenv
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.1-flash-lite
```

Inicie o servidor:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Abra http://127.0.0.1:8000/ no navegador.

Rotas: `GET /health` (status), `POST /chat` (mensagem) e `POST /reset?session_id=ID` (limpar conversa). Para testar: http://127.0.0.1:8000/docs.
