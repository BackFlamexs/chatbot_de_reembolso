
import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ["GEMINI_API_KEY"] = "somente-demonstracao-local"
from fastapi.testclient import TestClient
import main


def demonstrar():
    with TestClient(main.app) as client, patch("main.client") as provider:
        print("DEMONSTRAÇÃO LOCAL: respostas do Gemini simuladas.")
        for titulo, corpo in [("Mensagem vazia", {"message": " "}),
                              ("Mensagem longa", {"message": "x" * 1001})]:
            resposta = client.post('/chat', json=corpo)
            print(titulo, resposta.status_code, resposta.json())
        cenarios = [
            ("Rate limit", main.errors.ClientError(429, {})),
            ("Timeout", main.TimeoutException("demora simulada")),
            ("Indisponibilidade", main.errors.ServerError(503, {})),
            ("Falha inesperada", RuntimeError("falha simulada")),
        ]
        for titulo, erro in cenarios:
            session = Mock()
            session.send_message.side_effect = erro
            provider.chats.create.return_value = session
            with patch.object(main.time, 'sleep'):
                resposta = client.post('/chat', json={"message": "Quero simular"})
            print(titulo, resposta.status_code, resposta.json(), "tentativas:", session.send_message.call_count)
        provider.chats.create.return_value.send_message.side_effect = None
        provider.chats.create.return_value.send_message.return_value = SimpleNamespace(text="JSON inválido")
        resposta = client.post('/chat', json={"message": "Quero simular"})
        print("Saída inválida", resposta.status_code, resposta.json())
        print("Rota inexistente", client.get('/inexistente').status_code)


if __name__ == '__main__':
    demonstrar()
