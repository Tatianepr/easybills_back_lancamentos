# Minha API

Este é o MVP da sprint 03 do curso de **Engenharia de Software** da **PUC-Rio**

O objetivo aqui é disponibilizar o projeto de backend, onde foi desenvolvido um controle simples de despesas e receitas.

Linkendin: https://www.linkedin.com/in/tatianepr/



## Principais APIs

1) DELETE - /lancamento
2) GET - /lancamento
3) POST -/lancamento
4) PUT - /lancamento 
5) GET - /lancamentos
6) GET - /mensal
7) PATCH - /paga
8) GET - /saldo


## Arquitetura do projeto

Foi desenvolvido um frontend em REACT que chama os dois componentes conforme esquema abaixo, ambos escritos em Python.

<img scr="arquitetura.jpg">


## Como executar 


Será necessário ter todas as libs python listadas no `requirements.txt` instaladas.
Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).

PAra criar um ambiente virtual: 

```
python -m virtualenv env
.\env\Scripts\activate

```

Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.
```
pip install -r requirements.txt
```

Para executar a API  basta executar:

```
flask run --host 0.0.0.0 --port 5001
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor
automaticamente após uma mudança no código fonte. 

```
flask run --host 0.0.0.0 --port 5001 --reload
```

Abra o [http://localhost:5000/#/](http://localhost:5001/#/) no navegador para verificar o status da API em execução.


## Como executar através do Docker

Certifique-se de ter o [Docker](https://docs.docker.com/engine/install/) instalado e em execução em sua máquina.

Navegue até o diretório que contém o Dockerfile e o requirements.txt no terminal.
Execute **como administrador** o seguinte comando para construir a imagem Docker:

```
$ docker build -t lancamentos .
```

Uma vez criada a imagem, para executar o container basta executar, **como administrador**, seguinte o comando:

```
$ docker run -p 5001:5001 lancamentos
```

Uma vez executando, para acessar a API, basta abrir o [http://localhost:5001/#/](http://localhost:5001/#/) no navegador.

