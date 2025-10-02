from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms.fields.choices import SelectMultipleField
from wtforms.fields.numeric import DecimalField, IntegerField
from wtforms.fields.simple import BooleanField, FileField, StringField, SubmitField
from wtforms.validators import InputRequired, Length, NumberRange, ValidationError
from wtforms.widgets import CheckboxInput, html_params
from markupsafe import Markup


def at_least_one(form, field):
    if not field.data or len(field.data) == 0:
        raise ValidationError("Selecione pelo menos uma categoria")


class DivListWidget:
    """Processa uma lista de campos como um conjunto de divs ao invés de ul/li"""
    def __init__(self, prefix_label=True):
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f'<div {html_params(**kwargs)}>']
        for subfield in field:
            html.append(f'<div class="form-check">{subfield(class_="form-check-input")} {subfield.label(class_="form-check-label")}</div>')
        html.append("</div>")
        return Markup("".join(html))


class ProdutoForm(FlaskForm):
    nome = StringField(label="Nome do produto",
                       validators=[InputRequired(message="É obrigatório definir o nome do produto"),
                                   Length(max=100, message="O produto pode ter até 100 caracteres")])
    preco = DecimalField(label="Preço", places=2,
                         validators=[InputRequired(message="É obrigatório definir o preço"),
                                     NumberRange(min=0.00, message="Os preços devem ser positivos")])
    estoque = IntegerField(label="Estoque",
                           validators=[InputRequired(message="É preciso definir o estoque"),
                                       NumberRange(min=0, message="O estoque precisa ser positivo")])
    ativo = BooleanField(label="Ativo?")
    foto = FileField(label="Foto do produto",
                     validators=[FileAllowed(['jpg', 'png'], message="Apenas arquivos JPG ou PNG")])
    categorias = SelectMultipleField(label="Categorias do produto",
                                     widget=DivListWidget(prefix_label=False),
                                     option_widget=CheckboxInput(),
                                     validators=[at_least_one],
                                     coerce=str)
    removerfoto = BooleanField(label="Remover a foto atual?",
                               default=False)
    submit = SubmitField()
