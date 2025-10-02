from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # Se houver atributos comuns a todas as classes,
    # eles seriam adicionados aqui
    pass


bootstrap = Bootstrap5()
db = SQLAlchemy(model_class=Base,
                disable_autonaming=True)
csrf = CSRFProtect()
