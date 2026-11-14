import json
from datetime import date
from pathlib import Path

CAMINHO_CATALOGO = Path(__file__).parent / "dados" / "linhas_credito.json"

PRAZO_MAXIMO_MESES = 240

FUNCOES_AUTORIZADAS = {
    "buscar_perfil",
    "listar_linhas_compativeis",
    "simular_financiamento",
}


def _carregar_catalogo() -> dict:
    with open(CAMINHO_CATALOGO, encoding="utf-8") as arquivo:
        return json.load(arquivo)


CATALOGO = _carregar_catalogo()


def _perfil_confere(perfil: dict, nome: str) -> bool:
    return perfil["nome"].lower() == nome.lower()


def _linha_compativel(perfil: dict, linha: dict) -> bool:
    if not perfil.get("caf_ativo"):
        return False
    if linha["publico"] and perfil.get("categoria") not in linha["publico"]:
        return False
    finalidade = perfil.get("finalidade")
    if finalidade and finalidade not in linha["finalidades"]:
        return False
    return True


def _catalogo_vigente() -> bool:
    inicio = date.fromisoformat(CATALOGO["vigencia"]["inicio"])
    fim = date.fromisoformat(CATALOGO["vigencia"]["fim"])
    return inicio <= date.today() <= fim


def buscar_perfil(perfil: dict, nome: str) -> dict:
    if not _perfil_confere(perfil, nome):
        return {"sucesso": False, "erro": f"Produtor '{nome}' não encontrado."}
    return {"sucesso": True, "perfil": perfil}


def listar_linhas_compativeis(perfil: dict, nome: str) -> dict:
    if not _perfil_confere(perfil, nome):
        return {"sucesso": False, "erro": f"Produtor '{nome}' não encontrado."}

    valor = perfil.get("valor_desejado")
    linhas = []
    for linha in CATALOGO["linhas"]:
        if not _linha_compativel(perfil, linha):
            continue
        item = dict(linha)
        if valor:
            item["dentro_do_limite"] = valor <= linha["limite"]
        linhas.append(item)

    return {
        "sucesso": True,
        "produtor": perfil["nome"],
        "linhas": linhas,
        "vigencia": CATALOGO["vigencia"],
        "catalogo_vigente": _catalogo_vigente(),
        "fonte": CATALOGO["fonte"],
    }


def simular_financiamento(perfil: dict, valor: float, taxa_ano: float, prazo_meses: int) -> dict:
    valor = float(valor)
    taxa_ano = float(taxa_ano)
    prazo_meses = int(prazo_meses)

    if valor <= 0 or taxa_ano < 0 or not 1 <= prazo_meses <= PRAZO_MAXIMO_MESES:
        return {
            "sucesso": False,
            "erro": f"Informe valor positivo, taxa não negativa e prazo entre 1 e {PRAZO_MAXIMO_MESES} meses.",
        }

    taxa_mes = (1 + taxa_ano / 100) ** (1 / 12) - 1
    if taxa_mes == 0:
        parcela = valor / prazo_meses
    else:
        parcela = valor * taxa_mes / (1 - (1 + taxa_mes) ** -prazo_meses)
    total = parcela * prazo_meses

    return {
        "sucesso": True,
        "valor": valor,
        "taxa_ano": taxa_ano,
        "prazo_meses": prazo_meses,
        "parcela_mensal": round(parcela, 2),
        "total_pago": round(total, 2),
        "juros_totais": round(total - valor, 2),
        "aviso": "Estimativa sem carência, seguros ou tarifas. Confirme as condições no banco.",
    }


def executar_ferramenta(perfil: dict, nome_funcao: str, argumentos: dict) -> dict:
    if nome_funcao not in FUNCOES_AUTORIZADAS:
        return {"sucesso": False, "erro": f"Ferramenta '{nome_funcao}' não autorizada."}
    try:
        return globals()[nome_funcao](perfil, **argumentos)
    except (TypeError, ValueError, KeyError):
        return {"sucesso": False, "erro": "Argumentos inválidos para a ferramenta."}


def _declaracao(nome: str, descricao: str, propriedades: dict, obrigatorios: list) -> dict:
    return {
        "type": "function",
        "name": nome,
        "description": descricao,
        "parameters": {
            "type": "object",
            "properties": propriedades,
            "required": obrigatorios,
        },
    }


def criar_ferramentas() -> list:
    nome = {"nome": {"type": "string", "description": "Nome do produtor."}}
    return [
        _declaracao(
            "buscar_perfil",
            "Busca os dados cadastrados do produtor e da propriedade pelo nome.",
            nome,
            ["nome"],
        ),
        _declaracao(
            "listar_linhas_compativeis",
            "Lista as linhas de crédito compatíveis com o perfil do produtor, com limite, juros e vigência.",
            nome,
            ["nome"],
        ),
        _declaracao(
            "simular_financiamento",
            "Calcula parcela mensal e total pago de um financiamento. Use sempre que houver contas.",
            {
                "valor": {"type": "number", "description": "Valor financiado em reais."},
                "taxa_ano": {"type": "number", "description": "Taxa de juros ao ano, em percentual."},
                "prazo_meses": {"type": "integer", "description": "Prazo em meses."},
            },
            ["valor", "taxa_ano", "prazo_meses"],
        ),
    ]