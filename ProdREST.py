import argparse
import os
from flask import Flask, jsonify, request
import json
import requests
import threading
import time

app = Flask(__name__)


# Função para carregar produtos de um ficheiroo JSON
def load_produtos(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


# Caminho do script e do ficheiroo JSON
script_dir = os.path.dirname(os.path.abspath(__file__))
produtos_file_path = os.path.join(script_dir, 'produtos.json')

# Carregar lista inicial de produtos
produtos = load_produtos(produtos_file_path)


# Rota para listar categorias
@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = list(produtos.keys())
    return jsonify(categorias), 200


# Rota para listar produtos de uma categoria específica
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    categoria = request.args.get('categoria')
    if categoria in produtos:
        return jsonify(produtos[categoria]), 200
    else:
        return jsonify({"erro": "Categoria Inexistente"}), 404


# Rota para comprar uma quantidade de um produto específico
@app.route('/comprar/<produto>/<int:quantidade>', methods=['GET'])
def comprar_produto(produto, quantidade):
    for categoria, items in produtos.items():
        for item in items:
            if item['nome'].lower() == produto.lower():
                if item['quantidade'] >= quantidade:
                    item['quantidade'] -= quantidade
                    return jsonify({"mensagem": "Produtos comprados"}), 200
                else:
                    return jsonify({"erro": "Quantidade indisponível"}), 404
    return jsonify({"erro": "Produto inexistente"}), 404


# Função para registar o produtor no Gestor de Fornecedores
def registar_no_gestor(ip, porta, nome):
    url = "http://193.136.11.170:5001/produtor"
    data = {
        "ip": ip,
        "porta": porta,
        "nome": nome
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print("Novo produtor registado com sucesso.")
        elif response.status_code == 200:
            print("Informações do produtor atualizadas com sucesso.")
        else:
            print(f"Erro ao registar produtor: {response.status_code} - {response.text}")
    except requests.ConnectionError:
        print("Erro: Não foi possível conectar ao Gestor de Produtores.")


# Função para registar periodicamente o produtor REST a cada 5 minutos
def iniciar_registo_periodico(ip, porta, nome, intervalo=300):
    def registar_periodicamente():
        while True:
            registar_no_gestor(ip, porta, nome)
            time.sleep(intervalo)  # Espera 5 minutos (300 segundos)

    # Iniciar o thread para registo periódico
    thread = threading.Thread(target=registar_periodicamente, daemon=True)
    thread.start()


if __name__ == "__main__":
    # Argumentos de linha de comando para definir a porta
    parser = argparse.ArgumentParser(description='Start the producer server.')
    parser.add_argument('--port', type=int, default=5006, help='Port number to run the producer server on.')
    args = parser.parse_args()

    host = "10.8.0.9"
    port = args.port
    nome = "ProdREST Gonçalo"

    # Converter 'localhost' para '127.0.0.1' para validação do IP
    ip = "127.0.0.1" if host == "localhost" else host

    # registar o produtor e iniciar o registo periódico
    registar_no_gestor(ip, port, nome)
    iniciar_registo_periodico(ip, port, nome)

    # Iniciar o servidor Flask
    app.run(host=host, port=port, debug=True)