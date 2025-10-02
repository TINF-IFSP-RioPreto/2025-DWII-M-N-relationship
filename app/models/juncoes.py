from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.modules import db


class ProdutoCategoria(db.Model):
    __tablename__ = 'produto_categoria'
    produto_id: Mapped[Uuid] = mapped_column(Uuid(as_uuid=True),
                                              ForeignKey('produtos.id'),
                                              primary_key=True)
    categoria_id: Mapped[Uuid] = mapped_column(Uuid(as_uuid=True),
                                                ForeignKey('categorias.id'),
                                                primary_key=True)
