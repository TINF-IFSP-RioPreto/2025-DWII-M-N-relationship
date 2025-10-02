import json
import logging
import os
import sys

from flask import Flask, render_template


def create_app(config_filename: str = 'config.dev.json') -> Flask:
    from app.models.categoria import Categoria
    from app.models.produto import Produto
    from app.models.juncoes import ProdutoCategoria
    from app.utils import as_localtime, existe_esquema
    from .modules import bootstrap, csrf, db
    # Desativar as mensagens do servidor HTTP
    # https://stackoverflow.com/a/18379764
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    # Mudar o formato das mensagens de log
    logging.basicConfig(
            format='[%(asctime)s | %(levelname)-7s | '
                   '%(filename)s:%(funcName)s():%(lineno)04s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
    )

    app = Flask(__name__,
                instance_relative_config=True,
                static_folder='static',
                template_folder='templates')

    app.logger.setLevel(logging.DEBUG)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.logger.debug("Configurando a aplicação a partir do arquivo '%s'", config_filename)
    try:
        app.config.from_file(config_filename, load=json.load)
    except FileNotFoundError:
        app.logger.critical("O arquivo de configuração '%s' não existe", config_filename)
        sys.exit(1)

    app.logger.debug("Registrando as extensões")
    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        if not existe_esquema(app):
            app.logger.critical("É necessário fazer a migração/upgrade do banco")
            sys.exit(1)

        if Categoria.is_empty():
            categorias = ["Bebidas", "Carnes", "Padaria",
                          "Laticínios", "Hortifruti"]
            for c in categorias:
                categoria = Categoria()
                categoria.nome = c
                db.session.add(categoria)
            db.session.commit()

    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.jinja2',
                               title="Página principal")

    app.logger.debug("Registrando as blueprints")
    from app.routes.categoria import bp as categoria_bp
    from app.routes.produto import bp as produto_bp
    app.register_blueprint(categoria_bp)
    app.register_blueprint(produto_bp)

    # Formatando as datas para horário local
    # https://stackoverflow.com/q/65359968
    app.logger.debug("Registrando filtros no Jinja2")
    app.jinja_env.filters['as_localtime'] = as_localtime

    return app
