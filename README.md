# 🚀 API RESTful de Gerenciamento de Tarefas com Flask e MongoDB

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/Framework-Flask-brightgreen.svg?style=flat-square)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-MongoDB-orange.svg?style=flat-square)](https://www.mongodb.com/)

Uma API RESTful elegante e eficiente para gerenciar suas tarefas diárias, construída com Python, Flask e MongoDB. Simplifique sua organização pessoal com esta solução robusta e fácil de usar!

Vídeo de demonstração: https://www.loom.com/share/ea5f8d0b779542938a8918f312da1c39

## ✨ Funcionalidades Principais

Esta API oferece os seguintes endpoints para gerenciar suas tarefas:

- **Criar Tarefa (POST /tasks):** Adicione novas tarefas à sua lista com título, descrição, status e proprietário.
- **Listar Tarefas (GET /tasks):** Visualize todas as suas tarefas, com a opção de filtrar por status para focar no que é mais importante.
- **Obter Tarefa por ID (GET /tasks/\<task_id\>):** Acesse rapidamente os detalhes de uma tarefa específica utilizando seu identificador único.
- **Atualizar Tarefa (PUT /tasks/\<task_id\>):** Mantenha suas tarefas atualizadas, marcando-as como concluídas ou pendentes.
- **Deletar Tarefa (DELETE /tasks/\<task_id\>):** Remova tarefas que não são mais necessárias, mantendo sua lista organizada.

## 🛠️ Requisitos Técnicos

Antes de começar, certifique-se de ter o seguinte instalado:

- **[Python](https://www.python.org/downloads/) 3.8 ou superior:** A linguagem de programação principal.
- **[MongoDB](https://www.mongodb.com/try/download/community):** Banco de dados NoSQL (local ou [MongoDB Atlas](https://www.mongodb.com/atlas/database) na nuvem).

## 🚀 Como Executar a Aplicação Localmente

Siga estes passos simples para ter a API rodando em sua máquina:

1.  **Clone o Repositório:**

    ```bash
    git clone [URL do seu repositório]
    cd [nome do repositório]
    ```

2.  **Crie um Ambiente Virtual (Recomendado):**

    Isole as dependências do projeto para evitar conflitos com outras instalações Python.

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Linux/macOS
    venv\Scripts\activate  # No Windows
    ```

3.  **Instale as Dependências:**

    Instale todas as bibliotecas Python necessárias listadas no arquivo `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o MongoDB:**

    *   Certifique-se de que o MongoDB esteja instalado e rodando.
    *   **URI de Conexão:**  Abra o arquivo `app.py` e localize a linha:

        ```python
        app.config["MONGO_URI"] = "mongodb://localhost:27017/task_api_db"
        ```

        Modifique esta URI se sua instância do MongoDB estiver rodando em um endereço ou porta diferente, ou se você estiver usando o MongoDB Atlas. Se estiver rodando localmente com as configurações padrão, a URI padrão já deve funcionar.

5.  **Execute a Aplicação Flask:**

    Inicie o servidor Flask para rodar a API.

    ```bash
    flask run
    ```

    A API estará acessível em `http://127.0.0.1:5000/`.

## 🐳 Executando com Docker (Opcional)

Para executar a API utilizando Docker, siga os passos abaixo:

1.  **Construa a Imagem Docker:**

    No terminal, navegue até a raiz do seu projeto (onde o `Dockerfile` está localizado) e execute o seguinte comando para construir a imagem Docker. Dê um nome à sua imagem, por exemplo, `task-api-image`.

    ```bash
    docker build -t task-api-image .
    ```

2.  **Execute o Contêiner Docker:**

    Para executar a API em um contêiner Docker, você precisa garantir que o contêiner possa se conectar ao seu servidor MongoDB. Se o MongoDB estiver rodando localmente na sua máquina host, você pode usar `host.docker.internal` para se referir ao endereço da sua máquina host dentro do contêiner.  Execute o seguinte comando para rodar o contêiner, mapeando a porta 80 do contêiner para a porta 5000 da sua máquina host (você pode ajustar as portas conforme necessário).

    ```bash
    docker run -p 5000:80 -e MONGO_URI="mongodb://host.docker.internal:27017/task_api_db" task-api-image
    ```

    **Exemplo de como modificar o `app.py` para ler `MONGO_URI` da variável de ambiente:**
    
    Para permitir que sua aplicação Flask utilize a variável de ambiente `MONGO_URI` configurada no Docker (ou externamente), você precisa modificar o arquivo `app.py` para ler essa variável. Veja o exemplo abaixo:

    ```python

    import os # Importe a biblioteca 'os'
    
    from flask import Flask
    from flask_pymongo import PyMongo
    
    app = Flask(__name__)
    
    # Tenta obter MONGO_URI da variável de ambiente, se não existir, usa um valor padrão
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/task_api_db")
    mongo = PyMongo(app)
    db = mongo.db

    ```

    **Explicação dos parâmetros do `docker run`:**

    *   `-p 5000:80`: Mapeia a porta 80 do contêiner para a porta 5000 da sua máquina host. Você poderá acessar a API em `http://localhost:5000`.
    *   `-e MONGO_URI="mongodb://host.docker.internal:27017/task_api_db"`: Define uma variável de ambiente `MONGO_URI` dentro do contêiner. Isso é crucial para configurar a conexão com o MongoDB. `host.docker.internal` é usado para conectar ao MongoDB rodando na máquina host. Se seu MongoDB estiver em outro lugar (ex: MongoDB Atlas), substitua `mongodb://host.docker.internal:27017/task_api_db` pela sua URI de conexão correta.
    *   `task-api-image`: O nome da imagem Docker que você construiu no passo anterior.

    Após executar este comando, a API estará acessível através de `http://localhost:5000`.

## 🧪 Executando os Testes Unitários

Para garantir a qualidade e o funcionamento correto da API, testes unitários foram implementados usando `pytest`. Siga os passos abaixo para executar os testes e verificar se tudo está funcionando como esperado:

1.  **Certifique-se de ter o Ambiente Preparado:**

    Primeiramente, você precisa ter o ambiente de desenvolvimento configurado. Isso significa que você deve ter seguido os passos de "Como Executar a Aplicação Localmente" até o passo 3, que inclui:
    *   Clonar o repositório
    *   Criar e ativar um ambiente virtual (recomendado)
    *   Instalar as dependências do projeto (com `pip install -r requirements.txt`)

2.  **Navegue até o Diretório Raiz do Projeto:**

    Abra um terminal e utilize o comando `cd` para ir para o diretório principal do seu projeto `task_api`. Este é o diretório onde você encontra o arquivo `app.py`, a pasta `tests/` e o arquivo `requirements.txt`.

3.  **Execute o Comando `pytest`:**

    Com o terminal aberto no diretório raiz do projeto, execute o comando simples:

    ```bash
    pytest
    ```

    `pytest` é inteligente o suficiente para descobrir automaticamente os arquivos de teste (geralmente na pasta `tests/` e com nomes começando com `test_` ou terminando em `_test`) e executar as funções de teste dentro deles.

4.  **Analise o Resultado dos Testes:**

    Após a execução do comando `pytest`, você verá um relatório no terminal. Este relatório informará se os testes passaram ou falharam.

    *   **Testes Passando:** Se todos os testes estiverem passando, você verá uma saída semelhante a:

        ```
        ============================= test session starts ==============================
        ...
        ============================== <N> passed in <tempo>s ===============================
        ```

        Onde `<N>` é o número de testes executados e `passed` indica que todos foram bem-sucedidos. Parabéns! Sua API está funcionando corretamente, de acordo com os testes unitários.

    *   **Testes Falhando:** Se algum teste falhar, a saída será diferente e indicará os testes que falharam, juntamente com informações sobre a falha (traceback, asserção que falhou, etc.).  Examine cuidadosamente a saída para entender o motivo da falha e corrija o código ou os testes conforme necessário.

5.  **Interpretação e Ações:**

    *   **Todos os testes passam:** Isso é o ideal! Significa que as funcionalidades básicas da sua API estão funcionando conforme o esperado, e você pode ter mais confiança em prosseguir com o desenvolvimento ou deployment.
    *   **Testes falham:**  Não se preocupe, testes falhando são parte do processo de desenvolvimento. Use as informações fornecidas pelo `pytest` para depurar e corrigir o código. Pode ser que você tenha encontrado um bug no código da API ou um erro nos próprios testes.

    Executar os testes unitários regularmente é uma prática fundamental para garantir a qualidade do código e evitar regressões ao longo do tempo.
