from flask import Flask, jsonify, render_template, request
from flaskwebgui import FlaskUI

from services.api import buscar_por_cpf
from services.database import (
    get_api_key_masked,
    get_config,
    init_db,
    listar_consultas,
    obter_consulta,
    salvar_consulta,
    set_config,
)

app = Flask(__name__)
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/buscar", methods=["POST"])
def api_buscar():
    payload = request.get_json(silent=True) or {}
    cpf = payload.get("cpf", "")
    resultado = buscar_por_cpf(cpf)
    if resultado.get("erro"):
        return jsonify(resultado), 400

    consulta_id = salvar_consulta(resultado)
    resultado["consulta_id"] = consulta_id
    return jsonify(resultado)


@app.route("/api/configuracoes", methods=["GET"])
def api_get_config():
    return jsonify({
        "api_key_configurada": bool(get_config("api_key")),
        "api_key_mascarada": get_api_key_masked(),
        "api_header": get_config("api_header", "chave-api-dados"),
    })


@app.route("/api/configuracoes", methods=["POST"])
def api_save_config():
    payload = request.get_json(silent=True) or {}
    api_key = payload.get("api_key", "").strip()
    api_header = payload.get("api_header", "chave-api-dados").strip()

    if not api_key:
        return jsonify({"erro": "Informe a chave da API."}), 400

    set_config("api_key", api_key)
    set_config("api_header", api_header or "chave-api-dados")
    return jsonify({"sucesso": True, "api_key_mascarada": get_api_key_masked()})


@app.route("/api/historico")
def api_historico():
    return jsonify({"consultas": listar_consultas()})


@app.route("/api/historico/<int:consulta_id>")
def api_historico_detalhe(consulta_id):
    consulta = obter_consulta(consulta_id)
    if not consulta:
        return jsonify({"erro": "Consulta não encontrada."}), 404
    return jsonify(consulta)


if __name__ == "__main__":
    FlaskUI(
        app=app,
        server="flask",
        width=1280,
        height=860,
    ).run()
