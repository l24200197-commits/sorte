from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import psycopg2
import os
import random
import csv
import io

def create_app():
    app = Flask(__name__)
    CORS(app)

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if not DATABASE_URL:
        raise Exception("DATABASE_URL no configurada")

    def get_connection():
        return psycopg2.connect(DATABASE_URL)

    # 🔹 Crear tabla y cargar 80 números si está vacía
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
            for i in range(1, 81):
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

    # 🔹 Obtener todos los boletos
    @app.route('/api/boletos')
    def obtener_boletos():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT numero, estado FROM boletos ORDER BY numero")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(data)

    # 🔹 Asignar número aleatorio
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

        cur.execute(
            "UPDATE boletos SET estado='vendido', usuario=%s WHERE numero=%s",
            (usuario, numero)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"numero": numero})

    # 🔹 Elegir ganador
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

    # 🔹 Resetear boletos
    @app.route('/api/reset', methods=['POST'])
    def reset():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE boletos SET estado='disponible', usuario=NULL")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": "Boletos reiniciados"})

    # 🔹 Descargar CSV de boletos vendidos
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