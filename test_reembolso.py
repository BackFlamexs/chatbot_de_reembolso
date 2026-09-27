import unittest
from pydantic import ValidationError
from reembolso import DadosDespesa, decidir


def despesa(**ajustes):
    dados = dict(intencao="simular", data="2026-09-25", valor=80,
                 tipo="almoco", comprovante=True, contexto="viagem_trabalho",
                 tem_alcool=False, valor_alcool=0, ja_reembolsado_no_dia=0)
    dados.update(ajustes)
    return DadosDespesa.model_validate(dados)


class RegrasTests(unittest.TestCase):
    def test_alcool_desconhecido_exige_resposta(self):
        resultado = decidir(despesa(tem_alcool=None, valor_alcool=None))
        self.assertEqual(resultado["status"], "faltam_dados")
        self.assertIn("houve consumo de álcool", resultado["dados_faltantes"])
        self.assertIsNone(resultado["valor_reembolsavel"])

    def test_texto_descreve_apenas_desconto_real(self):
        self.assertNotIn("álcool", decidir(despesa())["reply"])
        com_alcool = decidir(despesa(tem_alcool=True, valor_alcool=30))
        self.assertIn("Foram excluídos R$ 30,00", com_alcool["reply"])
        self.assertEqual(com_alcool["valor_reembolsavel"], 50)
        saldo_esgotado = decidir(despesa(ja_reembolsado_no_dia=60))
        self.assertNotIn("álcool", saldo_esgotado["reply"])

    def test_valores_e_limites(self):
        for ajustes, esperado in [({}, 60), ({"valor": 42.35}, 42.35),
                                  ({"tipo": "lanche"}, 25),
                                  ({"tipo": "jantar", "ja_reembolsado_no_dia": 45}, 15),
                                  ({"tem_alcool": True, "valor_alcool": 30, "valor": 50}, 20),
                                  ({"ja_reembolsado_no_dia": 59.90}, 0.10)]:
            with self.subTest(ajustes=ajustes):
                self.assertEqual(decidir(despesa(**ajustes))["valor_reembolsavel"], esperado)

    def test_recusas(self):
        for ajustes in [{"comprovante": False}, {"data": "2026-09-26"},
                        {"contexto": "outro"}, {"tipo": "outro"},
                        {"ja_reembolsado_no_dia": 60},
                        {"tem_alcool": True, "valor_alcool": 80}]:
            with self.subTest(ajustes=ajustes):
                resultado = decidir(despesa(**ajustes))
                self.assertEqual(resultado["status"], "nao_reembolsavel")
                self.assertEqual(resultado["valor_reembolsavel"], 0)

    def test_desconhecidos_nao_sao_presumidos(self):
        for campo in ["data", "valor", "tipo", "comprovante", "contexto",
                      "tem_alcool", "ja_reembolsado_no_dia"]:
            with self.subTest(campo=campo):
                resultado = decidir(despesa(**{campo: None}))
                self.assertEqual(resultado["status"], "faltam_dados")
                self.assertIsNone(resultado["valor_reembolsavel"])
                self.assertTrue(resultado["dados_faltantes"])

    def test_inconsistencias_pedem_correcao(self):
        for ajustes in [{"tem_alcool": True, "valor_alcool": None},
                        {"tem_alcool": True, "valor_alcool": 90},
                        {"valor_alcool": 20}, {"valor": 0}, {"valor": 1.234}]:
            self.assertEqual(decidir(despesa(**ajustes))["status"], "faltam_dados")

    def test_dados_invalidos_sao_rejeitados(self):
        for ajustes in [{"data": "2026-02-30"}, {"valor": -1}, {"valor": float("inf")},
                        {"valor": float("nan")}, {"status": "reembolsavel"}]:
            with self.assertRaises(ValidationError):
                despesa(**ajustes)

    def test_correcao_e_simulacao_nao_consumem_saldo(self):
        self.assertEqual(decidir(despesa())["valor_reembolsavel"], 60)
        self.assertEqual(decidir(despesa())["valor_reembolsavel"], 60)
        self.assertEqual(decidir(despesa(comprovante=False))["valor_reembolsavel"], 0)


if __name__ == "__main__":
    unittest.main()
