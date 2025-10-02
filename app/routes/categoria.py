import sqlalchemy as sa
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.forms.categoria import EditCategoriaForm, NovoCategoriaForm
from app.models.categoria import Categoria
from app.modules import db

bp = Blueprint('categoria', __name__, url_prefix='/categoria')


@bp.route('/', methods=['GET'])
def lista():
    sentenca = sa.select(Categoria).order_by(Categoria.nome)
    rset = db.session.execute(sentenca).scalars()

    return render_template('categoria/lista.jinja2',
                           rset=rset)


@bp.route('/add', methods=['GET', 'POST'])
def add():
    form = NovoCategoriaForm()
    if form.validate_on_submit():
        categoria = Categoria()
        categoria.nome = form.nome.data
        db.session.add(categoria)
        db.session.commit()
        flash(f"Categoria '{form.nome.data}' adicionada")
        return redirect(url_for('categoria.lista'))

    return render_template('categoria/add_edit.jinja2',
                           title="Nova categoria",
                           form=form)


@bp.route('/edit/<uuid:id_categoria>', methods=['GET', 'POST'])
def edit(id_categoria):
    categoria = Categoria.get_by_id(id_categoria)
    if categoria is None:
        flash("Categoria inexistente", category='warning')
        return redirect(url_for('categoria.lista'))

    form = EditCategoriaForm(request.values, obj=categoria)
    if form.validate_on_submit():
        categoria.nome = form.nome.data
        db.session.commit()
        flash("Categoria alterada", category='success')
        return redirect(url_for('categoria.lista'))

    # Get 5 random products with this category
    import random
    random_produtos = random.sample(categoria.lista_de_produtos,
                                    min(5,
                                        len(categoria.lista_de_produtos))) if \
        categoria.lista_de_produtos else []

    return render_template('categoria/add_edit.jinja2',
                           title="Alterar categoria",
                           form=form,
                           categoria=categoria,
                           total_produtos=len(categoria.lista_de_produtos),
                           random_produtos=random_produtos)


@bp.route('/del/<uuid:id_categoria>', methods=['GET', 'POST'])
def remove(id_categoria):
    categoria = Categoria.get_by_id(id_categoria)
    if categoria is None:
        flash("Categoria inexistente", category='warning')
        return redirect(url_for('categoria.lista'))

    # Check if any product would be left without categories
    produtos_com_unica_categoria = []
    for produto in categoria.lista_de_produtos:
        if len(produto.categorias) == 1:
            produtos_com_unica_categoria.append(produto.nome)

    if produtos_com_unica_categoria:
        flash(
            f"Não é possível remover esta categoria. Os seguintes produtos ficariam sem "
            f"categoria: {', '.join(produtos_com_unica_categoria)}",
            category='danger')
        return redirect(url_for('categoria.lista'))

    db.session.delete(categoria)
    db.session.commit()
    flash("Categoria removida", category='success')
    return redirect(url_for('categoria.lista'))
