from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import random
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    DB_NAME = "boletos.db"

    # Crear base si no existe
    def init_db():
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS boletos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER UNIQUE,
            estado TEXT DEFAULT 'disponible',
            usuario TEXT
        )
        """)

        # Insertar números si no existen
        cur.execute("SELECT COUNT(*) FROM boletos")
        count = cur.fetchone()[0]

        if count == 0:
            for i in range(1, 151):
                cur.execute("INSERT INTO boletos (numero) VALUES (?)", (i,))
        
        conn.commit()
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
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT numero, estado FROM boletos ORDER BY numero")
        data = cur.fetchall()
        conn.close()
        return jsonify(data)

    @app.route('/api/aleatorio', methods=['POST'])
    def asignar_aleatorio():
        usuario = request.json.get("usuario")

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("SELECT numero FROM boletos WHERE estado='disponible'")
        disponibles = cur.fetchall()

        if not disponibles:
            conn.close()
            return jsonify({"error": "Boletos agotados"})

        numero = random.choice(disponibles)[0]

        cur.execute(
            "UPDATE boletos SET estado='vendido', usuario=? WHERE numero=?",
            (usuario, numero)
        )

        conn.commit()
        conn.close()

        return jsonify({"numero": numero})

    @app.route('/api/ganador')
    def ganador():
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("SELECT numero, usuario FROM boletos WHERE estado='vendido'")
        vendidos = cur.fetchall()

        if not vendidos:
            conn.close()
            return jsonify({"error": "No hay boletos vendidos"})

        elegido = random.choice(vendidos)
        conn.close()

        return jsonify({
            "numero": elegido[0],
            "usuario": elegido[1]
        })

    @app.route('/api/reset', methods=['POST'])
    def reset():
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("UPDATE boletos SET estado='disponible', usuario=NULL")
        conn.commit()
        conn.close()
        return jsonify({"success": "Boletos reiniciados"})

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)