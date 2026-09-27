from datetime import date
from decimal import Decimal, localcontext
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DadosDespesa(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intencao: Literal["simular", "orientacao"]
    data: date | None
    valor: float | None = Field(ge=0, allow_inf_nan=False)
    tipo: Literal["almoco", "jantar", "lanche", "outro"] | None
    comprovante: bool | None
    contexto: Literal["viagem_trabalho", "home_office_aprovado", "outro"] | None
    tem_alcool: bool | None = Field(description="null se não informado; false somente com negação explícita de consumo; true se o usuário informar consumo de álcool.")
    valor_alcool: float | None = Field(ge=0, allow_inf_nan=False)
    ja_reembolsado_no_dia: float | None = Field(ge=0, allow_inf_nan=False)


def decidir(dados: DadosDespesa) -> dict:
    """O modelo não fornece status, valor aprovado ou texto de decisão."""
    def resposta(status, texto, valor=None, faltantes=None):
        return dict(reply="Simulação: " + texto, status=status,
                    valor_reembolsavel=valor, dados_faltantes=faltantes or [])

    def recusar(texto):
        return resposta("nao_reembolsavel", texto, 0)

    if dados.intencao == "orientacao":
        return resposta("faltam_dados", "Posso simular reembolso de alimentação em viagem a trabalho ou home office aprovado, de segunda a sexta, com comprovante. O teto é R$ 60 para almoço/jantar e R$ 25 para lanches; álcool não é reembolsável. Para outras políticas, consulte o RH.")
    if dados.comprovante is False:
        return recusar("Despesas sem comprovante não são reembolsáveis.")
    if dados.data is not None and dados.data.weekday() >= 5:
        return recusar("A despesa ocorreu no fim de semana e não é reembolsável.")
    if dados.contexto == "outro":
        return recusar("A despesa precisa ocorrer em viagem a trabalho ou home office aprovado.")
    if dados.tipo == "outro":
        return recusar("Somente almoço, jantar e lanche são contemplados.")

    campos = {
        "data": "data da despesa", "valor": "valor gasto",
        "tipo": "tipo de refeição", "comprovante": "possui comprovante",
        "contexto": "contexto de trabalho", "tem_alcool": "houve consumo de álcool",
        "ja_reembolsado_no_dia": "valor já reembolsado no dia para esse limite (ou zero)",
    }
    faltantes = [nome for campo, nome in campos.items() if getattr(dados, campo) is None]
    if dados.tem_alcool and dados.valor_alcool is None:
        faltantes.append("valor gasto com álcool")
    if dados.valor == 0:
        faltantes.append("valor da despesa maior que zero")
    if dados.valor_alcool is not None and dados.valor is not None and dados.valor_alcool > dados.valor:
        faltantes.append("corrigir valor do álcool: não pode superar o total")
    if dados.tem_alcool is False and dados.valor_alcool not in (None, 0):
        faltantes.append("corrigir informações contraditórias sobre álcool")
    if faltantes:
        return resposta("faltam_dados", "Informe: " + "; ".join(faltantes) + ".", faltantes=faltantes)

    valores = [dados.valor, dados.ja_reembolsado_no_dia, dados.valor_alcool or 0]
    with localcontext() as contexto:
        contexto.prec = 330
        casas_invalidas = any(Decimal(str(v)) != Decimal(str(v)).quantize(Decimal("0.01")) for v in valores)
    if casas_invalidas:
        return resposta("faltam_dados", "Informe valores com no máximo duas casas decimais.", faltantes=["valores monetários com até duas casas decimais"])
    total, usado, alcool = (Decimal(str(v)) for v in valores)
    limite = Decimal("25") if dados.tipo == "lanche" else Decimal("60")
    saldo = max(Decimal("0"), limite - usado)
    aprovado = min(total - alcool, saldo)
    if aprovado == 0:
        if saldo == 0:
            return recusar("O limite diário já foi utilizado integralmente.")
        return recusar("O valor informado corresponde integralmente a bebidas alcoólicas, que não são reembolsáveis.")
    moeda = lambda valor: f"{valor:.2f}".replace(".", ",")
    detalhe_alcool = f" Foram excluídos R$ {moeda(alcool)} de bebidas alcoólicas." if alcool > 0 else ""
    return resposta("reembolsavel", f"Valor reembolsável: R$ {moeda(aprovado)}. Limite diário: R$ {moeda(limite)}; saldo disponível antes desta despesa: R$ {moeda(saldo)}.{detalhe_alcool} Esta simulação não registra um pagamento.", float(aprovado))
