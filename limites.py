from starlette.responses import JSONResponse


class LimiteCorpo:
    """Limita o corpo antes de interpretar JSON, inclusive sem Content-Length."""

    def __init__(self, app, max_bytes=16_384):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in ("POST", "PUT", "PATCH"):
            return await self.app(scope, receive, send)
        partes = []
        tamanho = 0
        while True:
            evento = await receive()
            if evento["type"] == "http.disconnect":
                return
            corpo = evento.get("body", b"")
            tamanho += len(corpo)
            if tamanho > self.max_bytes:
                resposta = JSONResponse(status_code=413, content={"detail": "Requisição muito grande. O limite é 16 KB."})
                return await resposta(scope, receive, send)
            partes.append(corpo)
            if not evento.get("more_body", False):
                break
        entregue = False

        async def receber():
            nonlocal entregue
            if not entregue:
                entregue = True
                return {"type": "http.request", "body": b"".join(partes), "more_body": False}
            return await receive()

        await self.app(scope, receber, send)
