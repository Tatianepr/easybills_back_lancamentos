from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, jsonify
from urllib.parse import unquote
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc
from sqlalchemy import extract, cast, Integer
from model import Session
from logger import logger
from schemas.error import ErrorSchema
from schemas.lancamento import *
from flask_cors import CORS
from flask_cors import cross_origin

info = Info(title="Lançamentos", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

""" Gerando documentação
    são 3 os principais elementos : Tags, Rotas com padrões de respostas bem definidas e Schemas. 
"""

# definindo tags, uma para cada contexto
home_tag = Tag(name="Documentação das APIs",
               description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
lancamento_tag = Tag(
    name="Lançamento", description="Adição, visualização, edição e remoção de lançamentos da base, vinculadas a categorias.")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/lancamento', tags=[lancamento_tag],
          responses={"200": LancamentoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_lancamento(form: LancamentoSchema):
    """ 
    Adiciona um novo lançamento à base de dados e associa uma categoria existente.
    Retorna o ID  da categoria. 
    """

    categoria_id = form.categoria_id
    logger.debug(f"Adicionado despesas a categoria com ID #{categoria_id}")

    # criando conexão com a base
    session = Session()

    # verificando se existe a categoria cadastrada
    tipo_categoria = TipoCategoria(categoria_id)
 
    # verificar se a categoria escolhida tem o mesmo tipo informado no lançamento
    if tipo_categoria != form.tipo:
        error_msg = "O Tipo da categoria não é o mesmo do Lançamento :/"
        logger.warning(f"Erro - tipo diferentes - categoria: '{tipo_categoria}', tipo do lançamento: '{form.tipo}', {error_msg}")
        return {"mesage": error_msg}, 409
    try:
        lancamento = Lancamento(
            descricao=form.descricao,
            valor=form.valor,
            pago=form.pago,
            tipo=form.tipo,
            categoria_id=form.categoria_id,
            data_vencimento=form.data_vencimento)

        # adicionando o despesa a categoria.
        session.add(lancamento)
        session.commit()
        logger.debug(f"Adicionando lançamento: '{lancamento.descricao}'")

        return apresenta_lancamento(lancamento), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Lançamento de mesmo nome e vencimento já salvo na base :/"
        logger.warning(
            f"Erro ao adicionar lançamento '{lancamento.descricao}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(
            f"Erro ao adicionar lançamento '{lancamento.descricao}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/lancamentos', tags=[lancamento_tag],
         responses={"200": ListagemLancamentosSchema, "404": ErrorSchema})
def get_lancamentos():
    """
    Faz a busca por todos as despesas e receitas cadastradas.
    Retorna uma representação da listagem de despesas e receitas.
    """
    logger.debug(f"Coletando lançamentos ")

    # criando conexão com a base
    session = Session()
    lancamentos = session.query(Lancamento).all()

    if not lancamentos:
        # se não há lançamentos cadastrados
        return {"lancamentos": []}, 200
    else:
        logger.debug(f"%d lançamentos encontrados" % len(lancamentos))
        # retorna a representação da despesa
        return apresenta_lancamentos(lancamentos), 200


@app.get('/lancamento', tags=[lancamento_tag],
         responses={"200": LancamentoViewSchema, "404": ErrorSchema})
def get_lancamento(query: LancamentoBuscaSchema):
    """
    Faz a busca por uma lançamentos a partir do nome. 
    Retorna uma representação do lançamento encontrado.
    """
    lancamento_descricao = query.descricao
    logger.debug(f"Coletando dados sobre lançamento #{lancamento_descricao}")
    # criando conexão com a base
    session = Session()
    lancamento = session.query(Lancamento).filter(
        Lancamento.descricao == lancamento_descricao).first()

    if not lancamento:
        # se lançamento não foi encontrado
        error_msg = "Lançamento não encontrada na base :/"
        logger.warning(
            f"Erro ao buscar lançamento '{lancamento_descricao}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Despesa encontrada: '{lancamento_descricao}'")
        # retorna a representação da despesa
        return apresenta_lancamento(lancamento), 200

@app.get('/mensal', tags=[lancamento_tag],
         responses={"200": ListagemLancamentosSchema, "404": ErrorSchema})
def get_mensal(query: MensalBuscaSchema):
    """
    Faz a busca por lançamentos a partir do mês informado.
    """

    lancamento_mes = query.data_vencimento
    logger.debug(f"Coletando dados sobre lançamento #{lancamento_mes}")
    # criando conexão com a base
    session = Session()
    
    lancamentos = session.query(Lancamento).filter(
        extract('month', Lancamento.data_vencimento) ==  extract('month', lancamento_mes),
        cast(extract('year', Lancamento.data_vencimento), Integer) == cast(extract('year', lancamento_mes), Integer)).all()

    if not lancamentos:
        # se lançamento não foi encontrado
        error_msg = "Lançamento não encontrada na base :/"
        logger.warning(
            f"Erro ao buscar lançamento '{lancamento_mes}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Lançamentos encontrados: '{lancamento_mes}'")
        # retorna a representação da despesa
        return apresenta_lancamentos(lancamentos), 200
    
@app.get('/saldo', tags=[lancamento_tag], responses={"200": ControleViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def get_saldo():
    """
    Consolida os lançamentos totalizando os valores mensais

    Mostra os totais lançados no mês corrente

    """
    mes_corrente = datetime.now().date()
    logger.debug(f"Buscando lançamentos do mês '{mes_corrente}'")

    session = Session()
    lancamentos = session.query(Lancamento).filter(
        extract('month', Lancamento.data_vencimento) ==  extract('month', mes_corrente),
        cast(extract('year', Lancamento.data_vencimento), Integer) == cast(extract('year', mes_corrente), Integer)).all()
    
    if not lancamentos:
        # se lançamento não foi encontrado
        error_msg = "Lançamento não encontrada na base para o mês corrente :/"
        logger.warning(
            f"Erro ao buscar lançamento para o mês '{mes_corrente}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:

        despesas = [lancamento for lancamento in lancamentos if lancamento.tipo == "Despesa"]
        receitas = [lancamento for lancamento in lancamentos if lancamento.tipo == "Receita"]
        despesas_pagas = [lancamento for lancamento in despesas if lancamento.pago == True]
        despesas_nao_pagas = [lancamento for lancamento in despesas if lancamento.pago == False]
        despesas_nao_pagas_atrasadas = [lancamento for lancamento in despesas if lancamento.pago == False and lancamento.data_vencimento < mes_corrente]
        
        total_valor = sum(lancamento.valor for lancamento in lancamentos)
        total_despesas = sum(lancamento.valor for lancamento in despesas)
        total_receitas = sum(lancamento.valor for lancamento in receitas)
        saldo_pago = sum(lancamento.valor for lancamento in despesas_pagas)
        total_atrasadas = sum(lancamento.valor for lancamento in despesas_nao_pagas_atrasadas)
        total_a_vencer = (sum(lancamento.valor for lancamento in despesas_nao_pagas)) - total_atrasadas
        saldo_mes = total_receitas - saldo_pago

        valores = {
            "saldo_mes": saldo_mes,
            "saldo_pago": saldo_pago,
            "total_a_vencer": total_a_vencer,
            "total_atrasadas": total_atrasadas,
            "total_despesas": total_despesas,
            "total_receitas": total_receitas,
            "total_valor": total_valor}

        logger.debug(f"Valor encontrada na API #{total_valor}")
        return valores

@app.delete('/lancamento', tags=[lancamento_tag],
            responses={"200": LancamentoRetornoSchema, "404": ErrorSchema})
def del_lancamento(query: LancamentoDelPagaSchema):
    """
    Deleta um lançamento a partir do nome informado
    Retorna uma mensagem de confirmação da remoção.
    """
    lancamento_id= query.id
    print(lancamento_id)
    logger.debug(f"Deletando dados sobre lançamento #{lancamento_id}")

    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Lancamento).filter(
        Lancamento.id == lancamento_id).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado lançamento #{lancamento_id}")
        return {"mesage": "Lançamento removido", "id": lancamento_id}
    else:
        # se a lançamento não foi encontrada
        error_msg = "Lançamento não encontrado na base :/"
        logger.warning(
            f"Erro ao deletar lançamento #'{lancamento_id}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.put('/paga', tags=[lancamento_tag],
         responses={"200": LancamentoRetornoSchema, "404": ErrorSchema})
def paga_lancamento(query: LancamentoDelPagaSchema):
    """ 
    Atualiza o status de pagamento de uma lancamento a partir do nome informado. 
    """
    lancamento_id = query.id
    print(lancamento_id)
    logger.debug(f"Atualizando dados sobre despesa #{lancamento_id}")

    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    lancamento = session.query(Lancamento).filter(
        Lancamento.id == lancamento_id).first()

    if lancamento:
        lancamento.pago = not lancamento.pago
        session.commit()
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Atualizando lancamento #{lancamento_id}")
        return {"mesage": "Lançamento atualizado", "id": lancamento_id}
    else:
        # se o lancamento não foi encontrado
        error_msg = "Lançamento não encontrado na base :/"
        logger.warning(
            f"Erro ao atualizar lançamento #'{lancamento_id}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.put('/lancamento', tags=[lancamento_tag],
         responses={"200": LancamentoRetornoSchema, "404": ErrorSchema})
def edita_lancamento(query: LancamentoBuscaEdicaoSchema):
    """ 
    Atualiza um lançamnto a partir do nome informado. 
    API responsável por editar todos os campos do lançamento. 
    """
    
    lancamento_id = query.id
    lancamento_descricao = query.descricao
    lancamento_valor = query.valor
    lancamento_tipo = query.tipo
    lancamento_vencimento = query.data_vencimento
    lancamento_id_categoria = query.categoria_id

    logger.debug(f"Atualizando dados sobre lançamento #{lancamento_id}")

    # criando conexão com a base
    session = Session()

    # fazendo a edição de acordo com o ID do lançamento.
    lancamento = session.query(Lancamento).filter(
        Lancamento.id == lancamento_id).first()
    
    # retorna representação da despesa editada.
    if lancamento:
        lancamento_tipo = lancamento_tipo
        categoria_tipo = TipoCategoria(lancamento_id_categoria)

        if lancamento_tipo == categoria_tipo:
            lancamento.descricao = lancamento_descricao
            lancamento.valor = lancamento_valor
            lancamento.data_vencimento = lancamento_vencimento
            lancamento.categoria_id = lancamento_id_categoria

            session.commit()
            # retorna a representação da mensagem de confirmação
            logger.debug(f"Atualizando lançamento #{lancamento_id}")
            return {"mesage": "Lançamento atualizada com sucesso", "lancamento": apresenta_lancamento(lancamento)}, 200
        
        else:
            # se tipo da categoria não é o mesmo do lançamento
            error_msg = "O Tipo da categoria não é o mesmo do Lançamento :/"
            logger.warning(f"Erro - tipo diferentes - categoria: '{categoria_tipo}', tipo do lançamento: '{lancamento_tipo}', {error_msg}")
            return {"mesage": error_msg}, 409
    else:
        # se o produto não foi encontrado
        error_msg = "Lançamento não encontrado na base :/"
        logger.warning(
            f"Erro ao atualizar lançamento #'{lancamento_id}', {error_msg}")
        return {"mesage": error_msg}, 404

