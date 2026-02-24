from flask import Flask, render_template
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import Config

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)
    app.extensions['mysql'] = mysql

    CORS(app)

    from routes.boleto_routes import boleto_bp
    app.register_blueprint(boleto_bp)

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/ganador')
    def ganador_page():
        return render_template('ganador.html')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)