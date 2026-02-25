from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import random

def create_app():
    app = Flask(__name__)
    CORS(app)

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if not DATABASE_URL:
        raise Exception("DATABASE_URL no está configurada")

    def get_connection():
        return psycopg2.connect(DATABASE_URL)

    def init_db():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS boletos (
            id SERIAL PRIMARY KEY,
            numero INTEGER UNIQUE,
            estado VARCHAR(20) DEFAULT 'disponible',
            usuario VARCHAR(100)
        )
        """)

        cur.execute("SELECT COUNT(*) FROM boletos")
        count = cur.fetchone()[0]

        if count == 0:
            for i in range(1, 151):
                cur.execute("INSERT INTO boletos (numero) VALUES (%s)", (i,))

        conn.commit()
        cur.close()
        conn.close()

    init_db()

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/ganador')
    def ganador_page():
        return render_template('ganador.html')

    @app.route('/api/boletos')
    def obtener_boletos():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT numero, estado FROM boletos ORDER BY numero")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(data)

    @app.route('/api/aleatorio', methods=['POST'])
    def asignar_aleatorio():
        usuario = request.json.get("usuario")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT numero FROM boletos WHERE estado='disponible'")
        disponibles = cur.fetchall()

        if not disponibles:
            cur.close()
            conn.close()
            return jsonify({"error": "Boletos agotados"})

        numero = random.choice(disponibles)[0]

        cur.execute(
            "UPDATE boletos SET estado='vendido', usuario=%s WHERE numero=%s",
            (usuario, numero)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"numero": numero})

    @app.route('/api/ganador')
    def ganador():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT numero, usuario FROM boletos WHERE estado='vendido'")
        vendidos = cur.fetchall()

        if not vendidos:
            cur.close()
            conn.close()
            return jsonify({"error": "No hay boletos vendidos"})

        elegido = random.choice(vendidos)

        cur.close()
        conn.close()

        return jsonify({
            "numero": elegido[0],
            "usuario": elegido[1]
        })

    @app.route('/api/reset', methods=['POST'])
    def reset():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE boletos SET estado='disponible', usuario=NULL")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": "Boletos reiniciados"})

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)