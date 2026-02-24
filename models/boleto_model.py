from flask import current_app
import random

class BoletoModel:

    @staticmethod
    def obtener_todos():
        mysql = current_app.extensions['mysql']
        cur = mysql.connection.cursor()
        cur.execute("SELECT numero, estado FROM boletos ORDER BY numero ASC")
        data = cur.fetchall()
        cur.close()
        return data

    @staticmethod
    def comprar(numero, usuario):
        mysql = current_app.extensions['mysql']
        cur = mysql.connection.cursor()

        # Validar rango
        if not numero or int(numero) < 1 or int(numero) > 150:
            return {"error": "Número inválido"}

        # Verificar si existe
        cur.execute("SELECT estado FROM boletos WHERE numero = %s", (numero,))
        estado = cur.fetchone()

        if not estado:
            cur.close()
            return {"error": "Número no existe"}

        if estado[0] == 'vendido':
            cur.close()
            return {"error": "Número ya vendido"}

        # Actualizar
        cur.execute("""
            UPDATE boletos 
            SET estado='vendido', usuario=%s, fecha_compra=NOW()
            WHERE numero=%s
        """, (usuario, numero))

        mysql.connection.commit()
        cur.close()

        return {"success": f"Número {numero} asignado"}

    @staticmethod
    def asignar_aleatorio(usuario):
        mysql = current_app.extensions['mysql']
        cur = mysql.connection.cursor()

        # Obtener disponibles
        cur.execute("SELECT numero FROM boletos WHERE estado='disponible'")
        disponibles = cur.fetchall()

        if not disponibles:
            cur.close()
            return {"error": "Boletos agotados"}

        numero = random.choice(disponibles)[0]

        # Actualizar
        cur.execute("""
            UPDATE boletos 
            SET estado='vendido', usuario=%s, fecha_compra=NOW()
            WHERE numero=%s
        """, (usuario, numero))

        mysql.connection.commit()
        cur.close()

        return {
            "success": f"Número {numero} asignado",
            "numero": numero
        }