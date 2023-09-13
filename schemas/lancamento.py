# pydantic - framework para geração de documentação das APIs
# serve também para validar requisições enviadas
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from model.lancamento import Lancamento
import requests
import json
from logger import logger

# aqui está exemplificado o uso de schemas para definir um formato de uma requisição.

def NomeCategoria(id_categoria: int):
    categoria_id = id_categoria

    try:
        request = requests.get(f"http://127.0.0.1:5000/categoriaID?id={categoria_id}")
        logger.debug(f"Retorno do json #{request.status_code}")

    except requests.exceptions.ConnectionError:
        return "Serviço Indisponível"

    if request.status_code!=200:
        error_msg = "Sem categoria"
        logger.warning(
            f"Erro ao adicionar lançamento para a categoria '{categoria_id}', {error_msg}")
        return error_msg
    else:
        categoria = json.loads(request.content)
        nome_categoria = categoria['nome']
        logger.debug(f"Nome de Categoria encontrada na API #{nome_categoria}")
        return nome_categoria

def TipoCategoria(id_categoria: int):
    categoria_id = id_categoria

    try:
        request = requests.get(f"http://127.0.0.1:5000/categoriaID?id={categoria_id}")
        logger.debug(f"Retorno do json #{request.status_code}")

    except requests.exceptions.ConnectionError:
        return "Serviço Indisponível"

    if request.status_code!=200:
        error_msg = "Sem categoria"
        logger.warning(
            f"Erro ao adicionar lançamento para a categoria '{categoria_id}', {error_msg}")
        return error_msg
    else:
        categoria = json.loads(request.content)
        tipo_categoria = categoria['tipo']
        logger.debug(f"Nome de Categoria encontrada na API #{tipo_categoria}")
        return tipo_categoria
    
class LancamentoSchema(BaseModel):
    """ Define como um novo lançamento a ser inserido deve ser representada
        define um modelo de dados e como será comunicado com o cliente
    """
    descricao: str = "Inglês"
    valor: float = 460.50
    pago: bool = False
    tipo: str = "Despesa"
    data_vencimento: date = datetime.now().date()
    categoria_id: int = 1

class LancamentoDelPagaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a deleção. Que será
        feita apenas com base no ID do lançamento.
    """
    id: int = 1

class LancamentoBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome da despesa.
    """
    descricao: str = "Inglês"

class MensalBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca mensal.
    """
    data_vencimento: date = datetime.now().date()

class LancamentoBuscaEdicaoSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca para edição da despesa. 
    """
    id: int = 1
    descricao: str = "Inglês"
    valor: float = 700
    #pago: bool = False
    tipo: str = "Despesa"
    data_vencimento: date = datetime.now().date()
    categoria_id: int = 1

class LancamentoViewSchema(BaseModel):
    """ Define como uma despesa será retornada: despesa + comentários.
    """
    id: int = 1
    descricao: str = "Inglês"
    valor: float = 700
    pago: bool = False
    tipo: str = "Despesa"
    data_vencimento: date = datetime.now().date()
    categoria_id: int = 1
    categoria_nome: str = "Educação"



class ListagemLancamentosSchema(BaseModel):
    """ Define como uma listagem de produtos será retornada.
    """
    despesas: List[LancamentoViewSchema]


def apresenta_lancamentos(despesas):
    """ Retorna uma representação da despesa seguindo o schema definido em
        DespesaViewSchema.
    """
    result = []
    for Despesa in despesas:
        result.append({
            "id":Despesa.id,
            "descricao": Despesa.descricao,
            "valor": Despesa.valor,
            "pago": Despesa.pago,
            "tipo": Despesa.tipo,
            "data_vencimento": Despesa.data_vencimento.strftime('%d/%m/%Y'),
            "categoria_id": Despesa.categoria_id,
            "categoria_nome": NomeCategoria(Despesa.categoria_id)
        })

    return {"despesas": result}

class LancamentoRetornoSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str = "mensagem"
    descricao: str = "Inglês"

class ControleViewSchema(BaseModel):
    saldo_mes: float = 5000.00
    saldo_pago: float = 1180.00
    total_a_vencer: float = 2800.50
    total_atrasadas: float = 240.00
    total_despesas: float = 240.00
    total_receitas: float = 240.00
    total_valor: float = 240.00

def apresenta_lancamento(lancamento: Lancamento):
    """ Retorna uma representação da despesa seguindo o schema definido em
        ProdutoViewSchema.
    """
    return {
            "id": lancamento.id,
            "descricao": lancamento.descricao,
            "valor": lancamento.valor,
            "pago": lancamento.pago,
            "tipo": lancamento.tipo,
            "data_vencimento": lancamento.data_vencimento.strftime('%d/%m/%Y'),
            "categoria_id": lancamento.categoria_id,
            "categoria_nome": NomeCategoria(lancamento.categoria_id)
    }
