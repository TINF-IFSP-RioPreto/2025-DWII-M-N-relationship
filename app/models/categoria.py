import uuid
from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_mixin import (BasicRepositoryMixin,
                                   TimeStampMixin)
from app.modules import db


class Categoria(db.Model, BasicRepositoryMixin, TimeStampMixin):
    __tablename__ = 'categorias'
    id: Mapped[Uuid] = mapped_column(Uuid(as_uuid=True),
                                     primary_key=True,
                                     default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(128),
                                      nullable=False)

    lista_de_produtos = relationship('Produto',
                                     secondary='produto_categoria',
                                     back_populates='categorias',
                                     lazy='select')
