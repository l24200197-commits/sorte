from flask import Blueprint, jsonify, request, current_app
from models.boleto_model import BoletoModel
import random

boleto_bp = Blueprint('boleto_bp', __name__, url_prefix='/api')


@boleto_bp.route('/boletos', methods=['GET'])
def obtener_boletos():
    data = BoletoModel.obtener_todos()
    return jsonify(data)


@boleto_bp.route('/aleatorio', methods=['POST'])
def aleatorio():
    data = request.json
    usuario = data.get("usuario")
    return jsonify(BoletoModel.asignar_aleatorio(usuario))


@boleto_bp.route('/ganador', methods=['GET'])
def ganador():
    mysql = current_app.extensions['mysql']
    cur = mysql.connection.cursor()

    cur.execute("SELECT numero, usuario FROM boletos WHERE estado='vendido'")
    vendidos = cur.fetchall()

    if not vendidos:
        cur.close()
        return jsonify({"error": "No hay boletos vendidos"})

    elegido = random.choice(vendidos)

    cur.close()

    return jsonify({
        "numero": elegido[0],
        "usuario": elegido[1]
    })