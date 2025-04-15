from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

#Pega a variável de ambiente e converte para JSON
FBKEY = json.loads(os.getenv('CONFIG_FIREBASE'))

cred = credentials.Certificate(FBKEY)
firebase_admin.initialize_app(cred)

#Conectando com o Firestore da Firebase
db = firestore.client()


# ---------- ROTA PRINCIPAL DE TESTE ----------
@app.route('/')
def index():
    return 'Sistema da Academia', 200


# ------ MÉTODO GET - CONSULTA DE ALUNOS -------
@app.route('/alunos', methods=['GET'])
def verAluno():
    alunos = []
    lista = db.collection('alunos').stream()

    for item in lista:
        alunos.append(item.to_dict())

    if not alunos:
        return jsonify({'message':'Erro! Nenhum aluno encontrado!'}), 404


# ------ MÉTODO GET - LISTA DE ALUNOS -------
@app.route('/alunos/lista', methods=['GET'])
def listaAluno():
    alunos = []
    lista = db.collection('alunos').stream()

    for item in lista:
        alunos.append(item.to_dict())

    if alunos:
        return jsonify(alunos), 200
    else:
        return jsonify({'message':'Erro! Nenhum aluno encontrado!'}), 404


# -------- MÉTODO GET - ALUNO POR ID --------
@app.route('/alunos/<id>', methods=['GET'])
def buscar(id):
    doc_ref = db.collection('alunos').document(id)
    doc = doc_ref.get().to_dict()

    if doc:
        return jsonify(doc), 200
    else:
        return jsonify({'message':'Erro! Aluno não encontrado!'}), 404


# ------- MÉTODO POST - ADICIONAR ALUNO -------
@app.route('/alunos', methods=['POST'])
def adicionarAluno():
    dados = request.json

    if "nome" not in dados or "cpf" not in dados:
        return jsonify({'message':'Erro. Os campos de Nome e CPF são obrigatórios.'}), 400

    # Contador
    counter_ref = db.collection('controle_id').document('contador')
    counter_doc = counter_ref.get().to_dict()
    ultimo_id = counter_doc.get('id')
    novo_id = int(ultimo_id) + 1
    counter_ref.update({'id': novo_id}) #atualização da coleção

    doc_ref= db.collection('alunos').document(str(novo_id))
    doc_ref.set({
        'id': novo_id,
        'nome': dados['nome'],
        'cpf': dados['cpf'],
        'status': True
    })

    return jsonify({'message':'Aluno cadastrado com sucesso!'}), 201


# -------- MÉTODO PUT - ALTERAR ALUNO -------
@app.route('/alunos/<id>', methods=['PUT'])
def alterarAluno(id):
    dados = request.json

    if "nome" not in dados or "cpf" not in dados:
        return jsonify({'mensagem':'Erro. Os campos de Nome e CPF são obrigatórios.'}), 400

    doc_ref = db.collection('alunos').document(id)
    doc = doc_ref.get()

    if doc.exists:
        doc_ref.update({
            'nome': dados['nome'],
            'cpf': dados['cpf'],
            'status': dados['status']
        })
        return jsonify({'message':'Aluno alterado com sucesso.'}), 201
    else:
        return jsonify({'message':'Erro. Aluno não encontrado.'}), 404


# ------- MÉTODO DELETE - EXCLUIR ALUNO -------
@app.route('/alunos/<id>', methods=['DELETE'])
def deletarAluno(id):
    doc_ref = db.collection('riddles').document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({'message':'Erro. Aluno não encontrado.'}), 404

    doc_ref.delete()
    return jsonify({'message':'Aluno deletado com sucesso!'})

if __name__ == '__main__':
    app.run()