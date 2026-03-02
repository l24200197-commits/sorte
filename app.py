from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import os
import random
import csv
import io

def create_app():
    app = Flask(__name__)
    CORS(app)

    DATABASE_URL = os.environ.get("DATABASE_URL")

    def get_connection():
        if DATABASE_URL:
            import psycopg2
            return psycopg2.connect(DATABASE_URL)
        else:
            import sqlite3
            return sqlite3.connect("boletos_local.db")

    def init_db():
        conn = get_connection()
        cur = conn.cursor()

        is_postgres = DATABASE_URL is not None

        if is_postgres:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS boletos (
                id SERIAL PRIMARY KEY,
                numero INTEGER UNIQUE,
                estado VARCHAR(20) DEFAULT 'disponible',
                usuario VARCHAR(100)
            )
            """)
        else:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS boletos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero INTEGER UNIQUE,
                estado TEXT DEFAULT 'disponible',
                usuario TEXT
            )
            """)

        cur.execute("SELECT COUNT(*) FROM boletos")
        count = cur.fetchone()[0]

        if count == 0:
            for i in range(1, 81):
                if is_postgres:
                    cur.execute("INSERT INTO boletos (numero) VALUES (%s)", (i,))
                else:
                    cur.execute("INSERT INTO boletos (numero) VALUES (?)", (i,))

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

    # 🔥 API boletos CORREGIDA (devuelve objetos)
    @app.route('/api/boletos')
    def obtener_boletos():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT numero, estado FROM boletos ORDER BY numero")
        data = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify([
            {"numero": row[0], "estado": row[1]}
            for row in data
        ])

    @app.route('/api/aleatorio', methods=['POST'])
    def asignar_aleatorio():
        usuario = request.json.get("usuario")

        if not usuario:
            return jsonify({"error": "Nombre requerido"})

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT numero FROM boletos WHERE estado='disponible'")
        disponibles = cur.fetchall()

        if not disponibles:
            cur.close()
            conn.close()
            return jsonify({"error": "Boletos agotados"})

        numero = random.choice(disponibles)[0]

        is_postgres = DATABASE_URL is not None

        if is_postgres:
            cur.execute(
                "UPDATE boletos SET estado='vendido', usuario=%s WHERE numero=%s",
                (usuario, numero)
            )
        else:
            cur.execute(
                "UPDATE boletos SET estado='vendido', usuario=? WHERE numero=?",
                (usuario, numero)
            )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"numero": numero})

    @app.route('/api/exportar')
    def exportar():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT numero, usuario
            FROM boletos
            WHERE estado='vendido'
            ORDER BY numero
        """)

        vendidos = cur.fetchall()
        cur.close()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Numero", "Usuario"])

        for row in vendidos:
            writer.writerow(row)

        output.seek(0)

        return Response(
            output,
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                "attachment; filename=boletos_vendidos.csv"
            }
        )

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)