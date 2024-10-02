from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from functools import wraps
from datetime import datetime
from conexao import ConexaoSingleton

app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'sua_chave_secreta'  # Defina uma chave secreta para usar a sessão

conexao_instance = ConexaoSingleton()
engine = conexao_instance.get_engine()

metadata = MetaData()
metadata.reflect(engine)

# Mapeamento automático das tabelas para classes Python
Base = automap_base(metadata=metadata)
Base.prepare()

Aluno = Base.classes.aluno
DiarioBordo = Base.classes.diariobordo

# Criar a sessão do SQLAlchemy
Session = sessionmaker(bind=engine)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login'))  # Redireciona para o login do admin
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ra = request.form['ra']
        session_db = Session()  # Criar uma nova sessão para esta operação
        try:
            aluno = session_db.query(Aluno).filter(Aluno.ra == ra).one_or_none()
            if aluno:
                return redirect(url_for('detalhe_aluno', ra=aluno.ra))
            else:
                mensagem = "RA não encontrado!"
                return render_template("home.html", mensagem=mensagem, active_page='index')
        except Exception as e:
            session_db.rollback()
            return render_template("home.html", mensagem="Erro ao tentar fazer login.", active_page='index')
        finally:
            session_db.close()
    
    return render_template("home.html", mensagem="", active_page='index')

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html", active_page='cadastro')

@app.route("/quemsomos")
def quem_somos():
    return render_template("quemsomos.html", active_page='quemsomos')

@app.route('/novoaluno', methods=['POST'])
def inserir_aluno():
    session_db = Session()  # Criar uma nova sessão
    ra = request.form['ra']
    nome = request.form['nome']
    tempoestudo = request.form['tempoestudo']
    rendafamiliar = request.form['rendafamiliar']

    aluno = Aluno(ra=ra, nome=nome, tempoestudo=tempoestudo, rendafamiliar=rendafamiliar)

    try:
        session_db.add(aluno)
        session_db.commit()
    except:
        session_db.rollback()
    finally:
        session_db.close()

    return redirect(url_for('index'))

@app.route('/alunos', methods=['GET'])
@admin_required
def listar_alunos():
    session_db = Session()  # Criar uma nova sessão
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')

    try:
        alunos_query = session_db.query(Aluno).filter(
            (Aluno.nome.like(f'%{search_query}%')) | (Aluno.ra.like(f'%{search_query}%'))
        ).order_by(Aluno.id)

        alunos_paginated = alunos_query.offset((page - 1) * per_page).limit(per_page).all()
        total_alunos = alunos_query.count()
        total_pages = (total_alunos + per_page - 1) // per_page 
    except:
        session_db.rollback()
        msg = "Erro ao tentar recuperar a lista de alunos"
        return render_template('index.html', msgbanco=msg, active_page='listar_alunos')
    finally:
        session_db.close()

    return render_template('listaralunos.html', alunos=alunos_paginated, page=page, total_pages=total_pages, search=search_query, active_page='listar_alunos')

@app.route('/excluir_aluno/<int:ra>', methods=['POST'])
@admin_required
def excluir_aluno(ra):
    session_db = Session()  # Criar uma nova sessão
    aluno = session_db.query(Aluno).filter_by(ra=ra).first()
    if aluno:
        try:
            session_db.delete(aluno)
            session_db.commit()
        except:
            session_db.rollback()
        finally:
            session_db.close()
    return redirect(url_for('listar_alunos'))

@app.route('/atualizar_aluno/<int:ra>', methods=['GET', 'POST'])
@admin_required
def atualizar_aluno(ra):
    session_db = Session()  # Criar uma nova sessão
    aluno = session_db.query(Aluno).filter_by(ra=ra).first()
    if request.method == 'POST':
        aluno.nome = request.form['nome']
        aluno.tempoestudo = request.form['tempoestudo']
        aluno.rendafamiliar = request.form['rendafamiliar']

        try:
            session_db.commit()
        except:
            session_db.rollback()
        finally:
            session_db.close()
        return redirect(url_for('listar_alunos'))

    return render_template('atualizaraluno.html', aluno=aluno, active_page='listar_alunos')

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        ADMIN_USERNAME = 'admin'
        ADMIN_PASSWORD = '123'

        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_id'] = username  # Armazena o nome do usuário na sessão
            return redirect(url_for('listar_alunos'))
        else:
            mensagem = "Credenciais inválidas!"
            return render_template("admin.html", mensagem=mensagem, active_page='admin')

    return render_template("admin.html", mensagem="", active_page='admin')

@app.route('/adicionar_diario/<string:ra>', methods=['POST'])  # Adicionando o RA na rota
def adicionar_diario(ra):
    session_db = Session()  # Criar uma nova sessão
    try:
        # Criar um novo diário de bordo
        novo_diario = DiarioBordo(
            texto=request.form['texto'],
            datahora=datetime.now(),
            fk_Aluno_id=session_db.query(Aluno).filter(Aluno.ra == ra).one().id  # Obter o id do aluno com base no RA
        )
        session_db.add(novo_diario)
        session_db.commit()
        # Redirecionar para a página de detalhes do aluno usando o RA
        return redirect(url_for('detalhe_aluno', ra=ra))  # Usando ra aqui
    except Exception as e:
        session_db.rollback()
        print(f"Erro ao adicionar diário: {e}")  # Captura de erro
        return "Erro ao adicionar diário", 500
    finally:
        session_db.close()

@app.route('/aluno/<string:ra>', methods=['GET'])  # O RA é uma string
def detalhe_aluno(ra):
    session_db = Session()  # Criar uma nova sessão
    try:
        # Filtrar pelo RA
        aluno = session_db.query(Aluno).filter(Aluno.ra == ra).one_or_none()
        # Consulta para diários com base no id do aluno
        diariobordo = session_db.query(DiarioBordo).filter(DiarioBordo.fk_Aluno_id == aluno.id).all() if aluno else []  # Verifica se aluno existe
        if aluno is None:
            return "Aluno não encontrado", 404
    except Exception as e:
        session_db.rollback()
        print(f"Erro ao buscar o aluno: {e}")  # Captura de erro
        return "Erro ao buscar o aluno", 500
    finally:
        session_db.close()

    return render_template('detalhealuno.html', aluno=aluno, diariobordo=diariobordo, active_page='listar_alunos')  # Passando os diários para o template

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove o usuário da sessão
    return redirect(url_for('admin_login'))  # Redireciona para a página de login do admin

if __name__ == "__main__":
    app.run(debug=True)
