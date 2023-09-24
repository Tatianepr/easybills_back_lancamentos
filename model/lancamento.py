from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Float, ForeignKey, UniqueConstraint
from datetime import datetime, date
from typing import Union
from model import Base


class Lancamento(Base):
    __tablename__ = 'lancamentos'

    id = Column(Integer, primary_key=True)
    descricao = Column(String(140))
    valor = Column(Float)
    pago = Column(Boolean)
    tipo = Column(String(20))
    categoria_id = Column(Integer, nullable=False)
    data_vencimento = Column(Date)
    login = Column(String(10))
    data_insercao = Column(DateTime, default=datetime.now())
    
    # Adicione a restrição de unicidade composta nas colunas descricao, data_vencimento e login
    __table_args__ = (
        UniqueConstraint('descricao', 'data_vencimento', 'login', name='uq_descricao_data_vencimento_login'),
    )

    def __init__(self, descricao: str, valor: float, pago: Boolean, tipo: str, categoria_id: int, data_vencimento: Date,
                 login: str, data_insercao: Union[DateTime, None] = None):
        """
        Cria uma Despesa

        Arguments:
            descricao: nome da despesa.
            valor: valor esperado para da despesa
            pago: se lançamento está pago ou não
            tipo: se é uma Despesa ou Receita
            data_vencimento: vencimento da despesa
            data_insercao: data de quando a despesa foi inserida na base
            categoria: categoria no qual o lançamento faz parte
        """
        self.descricao = descricao
        self.valor = valor
        self.pago = pago
        self.tipo = tipo
        self.categoria_id = categoria_id
        self.data_vencimento = data_vencimento
        self.login = login

        # se não for informada, será o data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao
