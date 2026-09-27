"""Testes locais com respostas simuladas, sem chamadas ao Gemini."""
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ.setdefault("GEMINI_API_KEY", "chave-apenas-para-testes")

from fastapi.testclient import TestClient
import main


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.session_id = "teste-resposta-estruturada"

    def tearDown(self):
        main.sessions.pop(self.session_id, None)

    def enviar(self, texto):
        session = SimpleNamespace(send_message=lambda message: SimpleNamespace(text=texto))
        with patch.dict(main.sessions, {self.session_id: session}):
            return self.client.post("/chat", json={
                "message": "Simular reembolso", "session_id": self.session_id
            })

    def test_estados_validos(self):
        from test_reembolso import despesa
        for ajustes, status, valor in [
            ({"valor": None}, "faltam_dados", None),
            ({}, "reembolsavel", 60),
            ({"comprovante": False}, "nao_reembolsavel", 0),
        ]:
            with self.subTest(status=status):
                response = self.enviar(despesa(**ajustes).model_dump_json())
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["status"], status)
                self.assertEqual(response.json()["valor_reembolsavel"], valor)

    def test_saida_invalida_retorna_502(self):
        for texto in [None, "", "texto sem JSON", "{}", json.dumps({
            "reply": "Recusado", "status": "nao_reembolsavel",
            "valor_reembolsavel": 60, "dados_faltantes": []
        }), json.dumps({
            "reply": "Faltam dados", "status": "faltam_dados",
            "valor_reembolsavel": 0, "dados_faltantes": ["data"]
        })]:
            with self.subTest(texto=texto):
                response = self.enviar(texto)
                self.assertEqual(response.status_code, 502)
                self.assertIn("formato inválido", response.json()["detail"])

    def test_mensagem_vazia_nao_chama_ia(self):
        with patch("main.client") as provider:
            response = self.client.post("/chat", json={"message": "   "})
            self.assertEqual(response.status_code, 422)
            provider.chats.create.assert_not_called()

    def test_503_seguido_de_sucesso(self):
        esperado = SimpleNamespace(text='resposta')
        session = Mock()
        session.send_message.side_effect = [main.errors.ServerError(503, {}), esperado]
        with patch.object(main.time, 'sleep') as sleep:
            self.assertIs(main.enviar_com_retentativa(session, 'mensagem'), esperado)
            sleep.assert_called_once_with(2)
        self.assertEqual(session.send_message.call_count, 2)

    def test_503_persistente_para_apos_duas_tentativas(self):
        session = Mock()
        session.send_message.side_effect = main.errors.ServerError(503, {})
        with patch.dict(main.sessions, {self.session_id: session}), patch.object(main.time, 'sleep'):
            response = self.client.post('/chat', json={
                'message': 'Simular', 'session_id': self.session_id
            })
        self.assertEqual(response.status_code, 503)
        self.assertEqual(session.send_message.call_count, 2)

    def test_429_e_timeout_nao_repetem(self):
        for erro, status in [(main.errors.ClientError(429, {}), 429),
                             (main.TimeoutException('demora'), 504)]:
            with self.subTest(status=status):
                session = Mock()
                session.send_message.side_effect = erro
                with patch.dict(main.sessions, {self.session_id: session}), patch.object(main.time, 'sleep') as sleep:
                    response = self.client.post('/chat', json={
                        'message': 'Simular', 'session_id': self.session_id
                    })
                self.assertEqual(response.status_code, status)
                self.assertEqual(session.send_message.call_count, 1)
                sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
