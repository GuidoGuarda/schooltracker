from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base

app = Flask(__name__)
Bootstrap(app)

# Configuração do Banco de Dados
import urllib.parse

user = 'root'
password = urllib.parse.quote_plus('senai@123')
host = 'localhost'
database = 'schooltracker'
connection_string = f'mysql+pymysql://{user}:{password}@{host}/{database}'

# Criar a engine e refletir o banco de dados existente
engine = create_engine(connection_string)
metadata = MetaData()
metadata.reflect(engine)

# Mapeamento automático das tabelas para classes Python
Base = automap_base(metadata=metadata)
Base.prepare()

# Acessando a tabela 'aluno' mapeada
Aluno = Base.classes.aluno

# Criar a sessão do SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route('/novoaluno', methods=['POST'])
def inserir_aluno():
    ra = request.form['ra']
    nome = request.form['nome']
    tempoestudo = request.form['tempoestudo']
    rendafamiliar = request.form['rendafamiliar']

    aluno = Aluno(ra=ra, nome=nome, tempoestudo=tempoestudo, rendafamiliar=rendafamiliar)

    try:
        session.add(aluno)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()

    return redirect(url_for('listar_alunos'))

@app.route('/alunos', methods=['GET'])
def listar_alunos():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    try:
        alunos_query = session.query(Aluno).order_by(Aluno.id)
        alunos_paginated = alunos_query.offset((page - 1) * per_page).limit(per_page).all()
        total_alunos = alunos_query.count()
        total_pages = (total_alunos + per_page - 1) // per_page 
    except:
        session.rollback()
        msg = "Erro ao tentar recuperar a lista de alunos"
        return render_template('index.html', msgbanco=msg)
    finally:
        session.close()

    return render_template('listaralunos.html', alunos=alunos_paginated, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=True)
