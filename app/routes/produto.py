from base64 import b64encode

from flask import abort, Blueprint, flash, redirect, render_template, request, Response, url_for
from werkzeug.exceptions import NotFound

from app.forms.produto import ProdutoForm
from app.models.categoria import Categoria
from app.models.produto import Produto
from app.modules import db

bp = Blueprint('produto', __name__, url_prefix="/produto")


@bp.route('/add', methods=['GET', 'POST'])
def add():
    if Categoria.is_empty():
        flash("Impossível adicionar produto. Adcione pelo menos uma categoria",
              category='warning')
        return redirect(url_for('categoria.add'))

    form = ProdutoForm()
    form.submit.label.text = "Adicionar produto"
    categorias = db.session.execute(db.select(Categoria).order_by(Categoria.nome)).scalars()
    form.categorias.choices = [(str(i.id), i.nome) for i in categorias]
    if form.validate_on_submit():
        produto = Produto(nome=form.nome.data, preco=form.preco.data,
                          ativo=form.ativo.data, estoque=form.estoque.data)
        if form.foto.data:
            produto.possui_foto = True
            produto.foto_base64 = (b64encode(request.files[form.foto.name].read()).
                                   decode('ascii'))
            produto.foto_mime = request.files[form.foto.name].mimetype
        else:
            produto.possui_foto = False
            produto.foto_base64 = None
            produto.foto_mime = None

        db.session.add(produto)

        # Add selected categories to the product
        for categoria_id in form.categorias.data:
            categoria = Categoria.get_by_id(categoria_id)
            if categoria:
                produto.categorias.append(categoria)

        db.session.commit()
        flash("Produto adicionado!")
        return redirect(url_for('produto.lista'))

    return render_template('produto/add.jinja2', form=form,
                           title="Adicionar novo produto")


@bp.route('/edit/<uuid:produto_id>', methods=['GET', 'POST'])
def edit(produto_id):
    produto = Produto.get_by_id(produto_id)
    if produto is None:
        flash("Produto inexistente", category='danger')
        return redirect(url_for('produto.lista'))

    form = ProdutoForm(obj=produto)
    form.submit.label.text = "Alterar produto"
    categorias = db.session.execute(db.select(Categoria).order_by(Categoria.nome)).scalars()
    form.categorias.choices = [(str(i.id), i.nome) for i in categorias]
    if form.validate_on_submit():
        produto.nome = form.nome.data
        produto.preco = form.preco.data
        produto.estoque = form.estoque.data
        produto.ativo = form.ativo.data

        if form.removerfoto.data:
            produto.possui_foto = False
            produto.foto_mime = None
            produto.foto_base64 = None
        elif form.foto.data:
            produto.possui_foto = True
            produto.foto_base64 = (b64encode(request.files[form.foto.name].read()).
                                   decode('ascii'))
            produto.foto_mime = request.files[form.foto.name].mimetype

        # Update categories
        produto.categorias.clear()
        for categoria_id in form.categorias.data:
            categoria = Categoria.get_by_id(categoria_id)
            if categoria:
                produto.categorias.append(categoria)

        db.session.commit()
        flash("Produto alterado", category='success')
        return redirect(url_for('produto.lista'))

    # Pre-select current categories
    form.categorias.data = [str(c.id) for c in produto.categorias]
    return render_template('produto/edit.jinja2', form=form,
                           title="Alterar um produto",
                           produto=produto)


@bp.route('/delete/<uuid:produto_id>', methods=['GET'])
def delete(produto_id):
    produto = Produto.get_by_id(produto_id)
    if produto is None:
        flash("Produto inexistente", category='danger')
        return redirect(url_for('produto.lista'))

    db.session.delete(produto)
    db.session.commit()
    flash("Produto removido!", category='success')
    return redirect(url_for('produto.lista'))


@bp.route('/lista', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
def lista():
    import uuid
    from flask import session

    page = request.args.get('page', type=int, default=1)

    # Obter tamanho da página (pp = per page)
    pp_param = request.args.get('pp', default='25')
    if pp_param == 'all':
        pp = 'all'
    else:
        try:
            pp = int(pp_param)
        except (ValueError, TypeError):
            pp = 25

    # Obter todas as categorias para o filtro
    todas_categorias = db.session.execute(
        db.select(Categoria).order_by(Categoria.nome)).scalars().all()

    # Obter IDs das categorias selecionadas do POST ou da sessão
    if request.method == 'POST':
        categorias_selecionadas = request.form.getlist('cat')
        # Salvar na sessão para usar na paginação
        session['categorias_filtro'] = categorias_selecionadas
    else:
        # Recuperar da sessão ou usar todas por padrão
        categorias_selecionadas = session.get('categorias_filtro',
                                              [str(c.id) for c in todas_categorias])

    # Se nenhuma categoria foi selecionada, selecionar todas por padrão
    if not categorias_selecionadas:
        categorias_selecionadas = [str(c.id) for c in todas_categorias]

    # Construir query com filtro de categoria
    from app.models.juncoes import ProdutoCategoria
    sentenca = db.select(Produto).order_by(Produto.nome)

    # Só aplicar filtro se nem todas as categorias estão selecionadas
    todas_cat_ids = set(str(c.id) for c in todas_categorias)
    cat_selecionadas_set = set(categorias_selecionadas)

    if cat_selecionadas_set and cat_selecionadas_set != todas_cat_ids:
        # Converter strings para UUIDs
        categorias_uuid = []
        for cat_id in categorias_selecionadas:
            try:
                categorias_uuid.append(uuid.UUID(cat_id))
            except (ValueError, AttributeError):
                continue

        # Filtrar produtos que têm pelo menos uma das categorias selecionadas
        if categorias_uuid:
            sentenca = sentenca.join(ProdutoCategoria).filter(
                    ProdutoCategoria.categoria_id.in_(categorias_uuid)
            ).distinct()

    # Paginar ou obter todos os resultados
    if pp == 'all':
        # Obter todos os resultados sem paginação
        produtos = db.session.execute(sentenca).scalars().all()

        # Criar um objeto que simula paginação para manter compatibilidade com o template
        class AllResults:
            def __init__(self, items):
                self.items = items
                self.total = len(items)
                self.first = 1 if items else 0
                self.last = len(items)
                self.has_prev = False
                self.has_next = False
                self.page = 1
                self.pages = 1
                self.per_page = len(items)

            def __iter__(self):
                return iter(self.items)

            def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
                # Retorna apenas a página 1 já que todos os itens estão em uma única página
                return [1]

        rset = AllResults(produtos)
    else:
        try:
            rset = db.paginate(sentenca, page=page, per_page=pp, error_out=True)
        except NotFound:
            flash(f"Não temos produtos na página {page}. Apresentando página 1")
            page = 1
            rset = db.paginate(sentenca, page=page, per_page=pp, error_out=False)

    return render_template('produto/lista.jinja2',
                           title="Lista de produtos",
                           rset=rset,
                           page=page,
                           pp=pp,
                           todas_categorias=todas_categorias,
                           categorias_selecionadas=categorias_selecionadas)


@bp.route('/imagem/<uuid:id_produto>', methods=['GET'])
def imagem(id_produto):
    produto = Produto.get_by_id(id_produto)
    if produto is None:
        return abort(404)
    conteudo, tipo = produto.imagem
    return Response(conteudo, mimetype=tipo)


@bp.route('/thumbnail/<uuid:id_produto>/<int:size>', methods=['GET'])
@bp.route('/thumbnail/<uuid:id_produto>', methods=['GET'])
def thumbnail(id_produto, size=128):
    produto = Produto.get_by_id(id_produto)
    if produto is None:
        return abort(404)
    conteudo, tipo = produto.thumbnail(size)
    return Response(conteudo, mimetype=tipo)
