# Relacionamentos Many-to-Many

Este é um aplicativo didático de controle de estoque desenvolvido para demonstrar como implementar relacionamentos muitos-para-muitos (many-to-many) em SQLAlchemy, utilizando Flask como framework web.

## 📚 Objetivo

O principal objetivo desta aplicação é ensinar aos estudantes:
- Como criar e gerenciar relacionamentos many-to-many no SQLAlchemy
- Implementação de interface de usuário para manipular estas relações
- Gestão de produtos e categorias com associações múltiplas

## 🔧 Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

## 📦 Instalação

### 1. Criar o Ambiente Virtual

Se você ainda não possui um ambiente virtual configurado, crie um usando o seguinte comando:

**Windows:**
```bash
python -m venv .venv
```

**Linux/Mac:**
```bash
python3 -m venv .venv
```

### 2. Ativar o Ambiente Virtual

**Windows:**
```bash
.venv\Scripts\activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. Instalar as Dependências

Com o ambiente virtual ativado, instale os pacotes necessários:

```bash
pip install -r requirements.txt
```

## 🗄️ Configuração do Banco de Dados

### Aplicar as Migrações

As migrações já estão criadas no diretório `migrations/`. Para aplicá-las ao banco de dados, de dentro do diretório principal do projeto, execute:

```bash
alembic upgrade head
```

Este comando irá criar todas as tabelas necessárias no banco de dados, incluindo:
- Tabela de **produtos**
- Tabela de **categorias**
- Tabela de **junção** (relacionamento many-to-many)

## 🚀 Executando a Aplicação

Após instalar as dependências e aplicar as migrações, de dentro do diretório principal do projeto, execute a aplicação com:

```bash
flask run
```

ou

```bash
python -m flask run
```

A aplicação estará disponível em: `http://localhost:5000`

## 📂 Estrutura do Projeto

```
├── app/
│   ├── models/          # Modelos SQLAlchemy (Produto, Categoria, etc.)
│   ├── routes/          # Rotas Flask
│   ├── forms/           # Formulários WTForms
│   ├── templates/       # Templates HTML
│   └── static/          # Arquivos estáticos (CSS, imagens)
├── migrations/          # Migrações do banco de dados (Alembic)
├── instance/            # Arquivos de configuração local e banco de dados sqlite
├── requirements.txt     # Dependências do projeto
└── alembic.ini         # Configuração do Alembic
```

## 🎓 Conceitos Demonstrados

### Relacionamento Many-to-Many

Este projeto demonstra como:
1. Definir uma tabela de associação para relacionamento many-to-many
2. Configurar os relacionamentos nos modelos SQLAlchemy
3. Criar interfaces para adicionar/remover associações
4. Consultar dados relacionados através das associações

## 📝 Comandos Úteis do Alembic

- **Aplicar migrações:** `alembic upgrade head`
- **Reverter última migração:** `alembic downgrade -1`
- **Ver histórico de migrações:** `alembic history`
- **Ver status atual:** `alembic current`

## 📝 Notas Adicionais

- O arquivo de configuração do ambiente de desenvolvimento está em `instance/config.dev.json`
- Certifique-se de que o ambiente virtual está ativado antes de executar qualquer comando
- Para desativar o ambiente virtual, use o comando `deactivate`
