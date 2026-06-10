from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests

from services.database import get_api_credentials

BASE_URL = "https://api.portaldatransparencia.gov.br"
TIMEOUT = 30


def _headers():
    api_header, api_key = get_api_credentials()
    return {api_header: api_key}


def _clean_cpf(cpf: str) -> str:
    return "".join(c for c in cpf if c.isdigit())


def _mes_ano_atual() -> str:
    return datetime.now().strftime("%Y%m")


def _periodo_12_meses() -> tuple[str, str]:
    agora = datetime.now()
    return f"{agora.month:02d}/{agora.year - 1}", f"{agora.month:02d}/{agora.year}"


def _ano_atual() -> int:
    return datetime.now().year


def _has_list_data(data) -> bool:
    return isinstance(data, list) and len(data) > 0


def _has_pessoa_fisica_data(data) -> bool:
    if not isinstance(data, dict):
        return False
    flags = [
        k for k, v in data.items()
        if isinstance(v, bool) and v
    ]
    return len(flags) > 0 or bool(data.get("nome"))


def _fetch(path: str, params: dict) -> tuple[int, object]:
    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            params=params,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        if response.status_code == 204 or not response.text:
            return response.status_code, []
        if response.status_code != 200:
            return response.status_code, None
        return response.status_code, response.json()
    except requests.RequestException:
        return 0, None


def _build_services(cpf: str) -> list[dict]:
    mes_ano = _mes_ano_atual()
    mes_inicio, mes_fim = _periodo_12_meses()
    ano = _ano_atual()

    return [
        {
            "id": "pessoa-fisica",
            "nome": "Pessoa Física",
            "categoria": "Cadastro",
            "descricao": "Resumo de vínculos e benefícios vinculados ao CPF",
            "path": "/api-de-dados/pessoa-fisica",
            "params": {"cpf": cpf},
            "positivo": _has_pessoa_fisica_data,
        },
        {
            "id": "servidores",
            "nome": "Servidores",
            "categoria": "Servidores Públicos",
            "descricao": "Servidores do Poder Executivo Federal",
            "path": "/api-de-dados/servidores",
            "params": {"cpf": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "servidores-remuneracao",
            "nome": "Remuneração de Servidores",
            "categoria": "Servidores Públicos",
            "descricao": f"Remuneração referente a {mes_ano[:4]}/{mes_ano[4:]}",
            "path": "/api-de-dados/servidores/remuneracao",
            "params": {"cpf": cpf, "mesAno": mes_ano, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "peps",
            "nome": "PEPs",
            "categoria": "Servidores Públicos",
            "descricao": "Pessoas Expostas Politicamente",
            "path": "/api-de-dados/peps",
            "params": {"cpf": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "viagens",
            "nome": "Viagens a Serviço",
            "categoria": "Viagens",
            "descricao": "Viagens realizadas a serviço",
            "path": "/api-de-dados/viagens-por-cpf",
            "params": {"cpf": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "contratos",
            "nome": "Contratos",
            "categoria": "Contratos",
            "descricao": "Contratos do Poder Executivo Federal",
            "path": "/api-de-dados/contratos/cpf-cnpj",
            "params": {"cpfCnpj": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "permissionarios",
            "nome": "Imóveis Funcionais",
            "categoria": "Patrimônio",
            "descricao": "Ocupantes de imóveis funcionais",
            "path": "/api-de-dados/permissionarios",
            "params": {"cpfOcupante": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "cartoes",
            "nome": "Cartões de Pagamento",
            "categoria": "Despesas",
            "descricao": "Gastos por cartão de pagamento governamental",
            "path": "/api-de-dados/cartoes",
            "params": {"cpfPortador": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "recursos-recebidos",
            "nome": "Recursos Recebidos",
            "categoria": "Despesas",
            "descricao": f"Recursos recebidos de {mes_inicio} a {mes_fim}",
            "path": "/api-de-dados/despesas/recursos-recebidos",
            "params": {
                "codigoFavorecido": cpf,
                "mesAnoInicio": mes_inicio,
                "mesAnoFim": mes_fim,
                "pagina": 1,
            },
            "positivo": _has_list_data,
        },
        {
            "id": "documentos-empenho",
            "nome": "Empenhos",
            "categoria": "Despesas",
            "descricao": f"Empenhos emitidos em {ano}",
            "path": "/api-de-dados/despesas/documentos-por-favorecido",
            "params": {"codigoPessoa": cpf, "fase": 1, "ano": ano, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "documentos-liquidacao",
            "nome": "Liquidações",
            "categoria": "Despesas",
            "descricao": f"Liquidações emitidas em {ano}",
            "path": "/api-de-dados/despesas/documentos-por-favorecido",
            "params": {"codigoPessoa": cpf, "fase": 2, "ano": ano, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "documentos-pagamento",
            "nome": "Pagamentos",
            "categoria": "Despesas",
            "descricao": f"Pagamentos emitidos em {ano}",
            "path": "/api-de-dados/despesas/documentos-por-favorecido",
            "params": {"codigoPessoa": cpf, "fase": 3, "ano": ano, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "ceis",
            "nome": "CEIS",
            "categoria": "Sanções",
            "descricao": "Cadastro de Empresas Inidôneas e Suspensas",
            "path": "/api-de-dados/ceis",
            "params": {"codigoSancionado": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "cnep",
            "nome": "CNEP",
            "categoria": "Sanções",
            "descricao": "Cadastro Nacional de Empresas Punidas",
            "path": "/api-de-dados/cnep",
            "params": {"codigoSancionado": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "ceaf",
            "nome": "CEAF",
            "categoria": "Sanções",
            "descricao": "Cadastro de Expulsões da Administração Federal",
            "path": "/api-de-dados/ceaf",
            "params": {"cpfSancionado": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "bolsa-familia",
            "nome": "Bolsa Família",
            "categoria": "Benefícios",
            "descricao": "Parcelas disponibilizadas pelo Bolsa Família",
            "path": "/api-de-dados/bolsa-familia-disponivel-por-cpf-ou-nis",
            "params": {"codigo": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "auxilio-emergencial",
            "nome": "Auxílio Emergencial",
            "categoria": "Benefícios",
            "descricao": "Registros de auxílio emergencial",
            "path": "/api-de-dados/auxilio-emergencial-por-cpf-ou-nis",
            "params": {"codigoBeneficiario": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "bpc",
            "nome": "BPC",
            "categoria": "Benefícios",
            "descricao": "Benefício de Prestação Continuada",
            "path": "/api-de-dados/bpc-por-cpf-ou-nis",
            "params": {"codigo": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "seguro-defeso",
            "nome": "Seguro Defeso",
            "categoria": "Benefícios",
            "descricao": "Registros do Seguro Defeso",
            "path": "/api-de-dados/seguro-defeso-codigo",
            "params": {"codigo": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "garantia-safra",
            "nome": "Garantia-Safra",
            "categoria": "Benefícios",
            "descricao": "Registros do programa Garantia-Safra",
            "path": "/api-de-dados/safra-codigo-por-cpf-ou-nis",
            "params": {"codigo": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
        {
            "id": "peti",
            "nome": "PETI",
            "categoria": "Benefícios",
            "descricao": "Programa de Erradicação do Trabalho Infantil",
            "path": "/api-de-dados/peti-por-cpf-ou-nis",
            "params": {"codigo": cpf, "pagina": 1},
            "positivo": _has_list_data,
        },
    ]


def _consultar_servico(servico: dict) -> dict:
    status, data = _fetch(servico["path"], servico["params"])
    positivo = servico["positivo"](data) if data is not None else False
    total = len(data) if isinstance(data, list) else (1 if positivo and isinstance(data, dict) else 0)

    return {
        "id": servico["id"],
        "nome": servico["nome"],
        "categoria": servico["categoria"],
        "descricao": servico["descricao"],
        "positivo": positivo,
        "total": total,
        "dados": data if positivo else None,
        "status": status,
    }


def buscar_por_cpf(cpf: str) -> dict:
    cpf_limpo = _clean_cpf(cpf)

    if len(cpf_limpo) != 11:
        return {"erro": "CPF inválido. Informe 11 dígitos.", "resultados": []}

    _, api_key = get_api_credentials()
    if not api_key:
        return {"erro": "Chave da API não configurada. Acesse Configurações.", "resultados": []}

    servicos = _build_services(cpf_limpo)
    resultados = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_consultar_servico, s): s for s in servicos}
        for future in as_completed(futures):
            resultados.append(future.result())

    resultados.sort(key=lambda r: (r["categoria"], r["nome"]))
    positivos = [r for r in resultados if r["positivo"]]

    pessoa = next((r for r in resultados if r["id"] == "pessoa-fisica"), None)
    nome = pessoa["dados"].get("nome", "") if pessoa and pessoa["dados"] else ""

    categorias = len({r["categoria"] for r in positivos})
    total_registros = sum(r.get("total", 0) for r in positivos)

    return {
        "cpf": cpf_limpo,
        "cpf_mascarado": f"***.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-**",
        "nome": nome,
        "total_servicos": len(servicos),
        "total_positivos": len(positivos),
        "total_registros": total_registros,
        "categorias": categorias,
        "consultado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "resultados": positivos,
    }
