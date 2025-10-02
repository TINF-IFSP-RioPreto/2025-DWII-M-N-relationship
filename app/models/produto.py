import io
import uuid
from base64 import b64decode

from PIL import Image

from sqlalchemy import Boolean, DECIMAL, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules import db
from app.models.base_mixin import BasicRepositoryMixin, TimeStampMixin


class Produto(db.Model, BasicRepositoryMixin, TimeStampMixin):
    __tablename__ = 'produtos'
    id = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = mapped_column(String(100), nullable=False, index=True)
    preco = mapped_column(DECIMAL(10, 2), default=0.00, nullable=False)
    estoque = mapped_column(Integer, default=0)
    ativo = mapped_column(Boolean, default=True, nullable=False)
    possui_foto = mapped_column(Boolean, default=False, nullable=False)
    foto_base64 = mapped_column(Text, default=None, nullable=True)
    foto_mime = mapped_column(String(64), nullable=True, default=None)

    categorias = relationship('Categoria',
                              secondary='produto_categoria',
                              back_populates='lista_de_produtos')

    @property
    def imagem(self):
        if not self.possui_foto:
            from PIL import ImageDraw, ImageFont

            saida = io.BytesIO()
            entrada = Image.new('RGB', (480, 480), (128, 128, 128))

            # Adicionar texto "Produto sem foto"
            draw = ImageDraw.Draw(entrada)
            texto = "Produto sem foto"

            # Tentar usar fonte padrão, ou fallback para fonte básica
            try:
                fonte = ImageFont.truetype("arial.ttf", 32)
            except:
                fonte = ImageFont.load_default()

            # Calcular posição centralizada do texto
            bbox = draw.textbbox((0, 0), texto, font=fonte)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            posicao = ((480 - text_width) / 2, (480 - text_height) / 2)

            # Desenhar o texto em branco
            draw.text(posicao, texto, fill=(255, 255, 255), font=fonte)

            formato = "PNG"
            entrada.save(saida, format=formato)
            conteudo = saida.getvalue()
            tipo = 'image/png'
        else:
            conteudo = b64decode(self.foto_base64)
            tipo = self.foto_mime
        return conteudo, tipo


    def thumbnail(self, size: int = 128):
        if not self.possui_foto:
            from PIL import ImageDraw, ImageFont

            saida = io.BytesIO()
            entrada = Image.new('RGB', (size, size), (128, 128, 128))

            # Adicionar texto "Produto sem foto"
            draw = ImageDraw.Draw(entrada)
            texto = "Produto\nsem foto"

            # Tentar usar fonte padrão, ou fallback para fonte básica
            try:
                # Ajustar tamanho da fonte baseado no tamanho da thumbnail
                tamanho_fonte = max(10, int(size / 8))
                fonte = ImageFont.truetype("arial.ttf", tamanho_fonte)
            except:
                fonte = ImageFont.load_default()

            # Calcular posição centralizada do texto
            bbox = draw.textbbox((0, 0), texto, font=fonte, align='center')
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            posicao = ((size - text_width) / 2, (size - text_height) / 2)

            # Desenhar o texto em branco
            draw.text(posicao, texto, fill=(255, 255, 255), font=fonte, align='center')

            formato = "PNG"
            entrada.save(saida, format=formato)
            conteudo = saida.getvalue()
            tipo = 'image/png'
        else:
            arquivo = io.BytesIO(b64decode(self.foto_base64))
            saida = io.BytesIO()
            entrada = Image.open(arquivo)
            formato = entrada.format
            (largura, altura) = entrada.size
            fator = min(size/largura, size/altura)
            novo_tamanho = (int(largura * fator), int(altura * fator))
            entrada.thumbnail(novo_tamanho)
            entrada.save(saida, format=formato)
            conteudo = saida.getvalue()
            tipo = self.foto_mime
        return conteudo, tipo
