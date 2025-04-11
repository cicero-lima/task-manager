# tests/test_app.py
import pytest
import json
import sys
import os
from pymongo import MongoClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db  # Importe a app e db do seu arquivo app.py

TEST_MONGO_URI = "mongodb+srv://r7loaded1:NWKsEhLwNvYKzs94@cluster0.efqkyeq.mongodb.net/test_tasks?retryWrites=true&w=majority&appName=Cluster0"

@pytest.fixture(scope="function") 
def client():
    """Fixture para criar um cliente Flask para testes."""
    app.config['MONGO_URI'] = TEST_MONGO_URI  # Configura a URI para o banco de teste
    testing_client = app.test_client()

    # Garante que o banco de dados de teste está limpo BEFORE EACH TEST FUNCTION
    with app.app_context():
        tasks_collection = db.tasks
        tasks_collection.delete_many({}) # Limpa a coleção de tarefas

    yield testing_client  # Retorna o cliente para os testes

    # Limpa o banco de dados de teste AFTER EACH TEST FUNCTION (and also after module in original code - which is fine)
    with app.app_context():
        tasks_collection = db.tasks
        tasks_collection.delete_many({}) # Limpa novamente after the test function

def test_db_initialization(client):
    """Simple test to check if db is initialized."""
    with app.app_context():
        assert db is not None, "db is None - flask-pymongo not initialized"
        assert hasattr(db, 'tasks'), "db.tasks attribute not found"
        
def test_create_task(client):
    """Testa a criação de uma nova tarefa."""
    response = client.post(
        '/tasks',
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "pending",
            "owner": "Test User"
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data.decode('utf-8'))
    assert data['title'] == "Test Task"
    assert data['status'] == "pending"
    assert 'id' in data

def test_create_task_invalid_status(client):
    """Testa a criação de tarefa com status inválido."""
    response = client.post(
        '/tasks',
        json={
            "title": "Invalid Status Task",
            "description": "Test Description",
            "status": "invalid_status",
            "owner": "Test User"
        }
    )
    assert response.status_code == 400
    data = json.loads(response.data.decode('utf-8'))
    assert "Status inválido" in data['errors']

def test_get_tasks_empty(client):
    """Testa a listagem de tarefas quando não há tarefas cadastradas."""
    response = client.get('/tasks')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data == []

def test_get_tasks_with_tasks(client):
    """Testa a listagem de tarefas quando existem tarefas cadastradas."""
    # Cria algumas tarefas de teste
    task1_payload = {"title": "Task 1", "description": "Desc 1", "status": "pending", "owner": "User 1"}
    task2_payload = {"title": "Task 2", "description": "Desc 2", "status": "done", "owner": "User 2"}
    client.post('/tasks', json=task1_payload)
    client.post('/tasks', json=task2_payload)

    response = client.get('/tasks')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data) == 2
    assert data[0]['title'] == "Task 2" # Verifica ordenação por data de criação (o último criado vem primeiro)
    assert data[1]['title'] == "Task 1"

def test_get_tasks_filter_by_status(client):
    """Testa a listagem de tarefas filtrando por status."""
    # Cria algumas tarefas de teste com diferentes status
    client.post('/tasks', json={"title": "Task Pending", "description": "Desc", "status": "pending", "owner": "User"})
    client.post('/tasks', json={"title": "Task Done", "description": "Desc", "status": "done", "owner": "User"})
    client.post('/tasks', json={"title": "Task In Progress", "description": "Desc", "status": "in_progress", "owner": "User"})

    response = client.get('/tasks?status=done')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert len(data) == 1
    assert data[0]['status'] == "done"
    assert data[0]['title'] == "Task Done"

def test_get_task_by_id(client):
    """Testa a obtenção de uma tarefa específica por ID."""
    # Cria uma tarefa para testar a busca
    create_response = client.post(
        '/tasks',
        json={"title": "Task to Get", "description": "Desc", "status": "pending", "owner": "User"}
    )
    task_data = json.loads(create_response.data.decode('utf-8'))
    task_id = task_data['id']

    response = client.get(f'/tasks/{task_id}')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['id'] == task_id
    assert data['title'] == "Task to Get"

def test_get_task_not_found(client):
    """Testa a obtenção de tarefa com ID inexistente."""
    response = client.get('/tasks/non_existent_id') # 'non_existent_id' não é um ObjectId válido, deve retornar 404
    assert response.status_code == 404
    data = json.loads(response.data.decode('utf-8'))
    assert "Tarefa não encontrada" in data['message']

def test_update_task(client):
    """Testa a atualização de uma tarefa."""
    # Cria uma tarefa para ser atualizada
    create_response = client.post(
        '/tasks',
        json={"title": "Task to Update", "description": "Desc", "status": "pending", "owner": "User"}
    )
    task_data = json.loads(create_response.data.decode('utf-8'))
    task_id = task_data['id']

    update_response = client.put(f'/tasks/{task_id}', json={"done": True})
    assert update_response.status_code == 200
    updated_data = json.loads(update_response.data.decode('utf-8'))
    assert updated_data['id'] == task_id
    assert updated_data['status'] == "done"

    # Verifica se realmente foi atualizado no banco
    get_response = client.get(f'/tasks/{task_id}')
    get_task_data = json.loads(get_response.data.decode('utf-8'))
    assert get_task_data['status'] == "done"


def test_update_task_not_found(client):
    """Testa a atualização de tarefa com ID inexistente."""
    response = client.put('/tasks/non_existent_id', json={"done": True})
    assert response.status_code == 404
    data = json.loads(response.data.decode('utf-8'))
    assert "Tarefa não encontrada" in data['message']

def test_delete_task(client):
    """Testa a deleção de uma tarefa."""
    # Cria uma tarefa para ser deletada
    create_response = client.post(
        '/tasks',
        json={"title": "Task to Delete", "description": "Desc", "status": "pending", "owner": "User"}
    )
    task_data = json.loads(create_response.data.decode('utf-8'))
    task_id = task_data['id']

    delete_response = client.delete(f'/tasks/{task_id}')
    assert delete_response.status_code == 204

    # Verifica se realmente foi deletado
    get_response = client.get(f'/tasks/{task_id}')
    assert get_response.status_code == 404
    get_task_data = json.loads(get_response.data.decode('utf-8'))
    assert "Tarefa não encontrada" in get_task_data['message']

def test_delete_task_not_found(client):
    """Testa a deleção de tarefa com ID inexistente."""
    response = client.delete('/tasks/non_existent_id')
    assert response.status_code == 404
    data = json.loads(response.data.decode('utf-8'))
    assert "Tarefa não encontrada" in data['message']