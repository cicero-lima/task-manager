# task_api/app.py
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from pydantic import BaseModel, ValidationError
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)

# Ativa CORS pra toda a aplicação
CORS(app)

# Configuração do MongoDB
app.config["MONGO_URI"] = "mongodb+srv://r7loaded1:NWKsEhLwNvYKzs94@cluster0.efqkyeq.mongodb.net/tasks?retryWrites=true&w=majority&appName=Cluster0"  # Substitua pela sua URI do MongoDB
mongo = PyMongo(app)
db = mongo.db


# Modelos Pydantic para validação
class TaskCreate(BaseModel):
    title: str
    description: str
    status: str
    owner: str

    @classmethod
    def validate_status(cls, status: str) -> str:
        valid_statuses = ["done", "in_progress", "pending"]
        if status not in valid_statuses:
            raise ValueError(f"Status inválido. Deve ser um de: {valid_statuses}")
        return status

    @classmethod
    def parse_obj(cls, obj):
        try:
            return super().parse_obj(obj)
        except ValidationError as e:
            raise ValueError(e.errors())


class TaskUpdate(BaseModel):
    done: bool


def format_task(task):
    """Formata uma tarefa para o formato de resposta da API."""
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "owner": task["owner"],
        "creation_date": task["creation_date"]
    }


@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Endpoint para criar uma nova tarefa.

    Recebe um JSON com os dados da tarefa (title, description, status, owner)
    e armazena no banco de dados MongoDB.

    Retorna:
        JSON com a tarefa criada e código HTTP 201 (Created) em caso de sucesso.
        JSON com mensagem de erro e código HTTP 400 (Bad Request) em caso de falha na validação.
    """
    data = request.get_json()
    if not data:
        return jsonify({"message": "Dados da tarefa não fornecidos"}), 400

    try:
        task_data = TaskCreate.parse_obj(data)
        task_data.status = TaskCreate.validate_status(task_data.status) # Validação extra do status

        task_dict = task_data.dict()
        task_dict["creation_date"] = datetime.utcnow() # Adiciona a data de criação
        task_id = db.tasks.insert_one(task_dict).inserted_id
        task = db.tasks.find_one({"_id": task_id})

        return jsonify(format_task(task)), 201

    except ValueError as ve:
        return jsonify({"message": "Erro de validação", "errors": str(ve)}), 400
    except Exception as e:
        return jsonify({"message": "Erro ao criar tarefa", "error": str(e)}), 500


@app.route('/tasks', methods=['GET'])
def list_tasks():
    """
    Endpoint para listar todas as tarefas existentes.

    Permite filtrar tarefas por status através do parâmetro de query 'status'.
    Também ordena as tarefas por data de criação (mais recentes primeiro).

    Retorna:
        JSON com a lista de tarefas e código HTTP 200 (OK) em caso de sucesso.
    """
    status_filter = request.args.get('status')
    query = {}
    if status_filter:
        query['status'] = status_filter

    tasks = list(db.tasks.find(query).sort("creation_date", -1)) # Ordena por data de criação decrescente
    formatted_tasks = [format_task(task) for task in tasks]
    return jsonify(formatted_tasks), 200


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """
    Endpoint para obter os dados de uma tarefa específica.

    Recebe o ID da tarefa como parâmetro na URL.

    Retorna:
        JSON com os dados da tarefa e código HTTP 200 (OK) se a tarefa for encontrada.
        JSON com mensagem de erro e código HTTP 404 (Not Found) se a tarefa não for encontrada.
    """
    try:
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if task:
            return jsonify(format_task(task)), 200
        else:
            return jsonify({"message": "Tarefa não encontrada"}), 404
    except Exception: # Captura erros de ObjectId inválido também
        return jsonify({"message": "Tarefa não encontrada"}), 404


@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Endpoint para atualizar os dados de uma tarefa específica.

    Recebe o ID da tarefa como parâmetro na URL e um JSON no body com os dados a serem atualizados.
    Atualmente permite apenas atualizar o status 'done' para true ou false.

    Retorna:
        JSON com a tarefa atualizada e código HTTP 200 (OK) em caso de sucesso.
        JSON com mensagem de erro e código HTTP 400 (Bad Request) se os dados de atualização forem inválidos.
        JSON com mensagem de erro e código HTTP 404 (Not Found) se a tarefa não for encontrada.
    """
    try:
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return jsonify({"message": "Tarefa não encontrada"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"message": "Dados para atualização não fornecidos"}), 400

        try:
            update_data = TaskUpdate.parse_obj(data)
            db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": "done" if update_data.done else "pending"}}) # Simplificação para atualizar status baseado em 'done'
            updated_task = db.tasks.find_one({"_id": ObjectId(task_id)})
            return jsonify(format_task(updated_task)), 200

        except ValueError as ve:
            return jsonify({"message": "Erro de validação nos dados de atualização", "errors": str(ve)}), 400

    except Exception: # Captura erros de ObjectId inválido também
        return jsonify({"message": "Tarefa não encontrada"}), 404


@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Endpoint para deletar uma tarefa específica.

    Recebe o ID da tarefa como parâmetro na URL.

    Retorna:
        Código HTTP 204 (No Content) em caso de sucesso (tarefa deletada).
        JSON com mensagem de erro e código HTTP 404 (Not Found) se a tarefa não for encontrada.
    """
    try:
        result = db.tasks.delete_one({"_id": ObjectId(task_id)})
        if result.deleted_count > 0:
            return '', 204  # No Content - Deletado com sucesso
        else:
            return jsonify({"message": "Tarefa não encontrada"}), 404
    except Exception: # Captura erros de ObjectId inválido também
        return jsonify({"message": "Tarefa não encontrada"}), 404


