from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Films, User 
from utils import authorized_required


app = Flask(__name__)

app.secret_key = '123'

DATABASE_URL = "postgresql://fortex:123@0.0.0.0:5432/mydatabase"



engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
db_session = Session()
films = db_session.query(Films).all()

# @app.route('/')
# def main():
#     return render_template('index.html', films=films)


@app.route('/', methods=['GET'], endpoint='search')
@authorized_required
def search():
    search_query = request.args.get('search_query', '')
    selected_year = request.args.get('year', '')
    selected_genre = request.args.get('genre', '')
    genres = db_session.query(Films.type).distinct().all()
    genres = [genre[0] for genre in genres]

    query = db_session.query(Films)

    if search_query:
        query = query.filter(Films.title.ilike(f'%{search_query}%'))
    
    if selected_year:
        query = query.filter(Films.release_year == selected_year)

    if selected_genre:
        query = query.filter(Films.type == selected_genre)

    films = query.all()

    years = db_session.query(Films.release_year).distinct().all()
    years = [year[0] for year in years]

    return render_template('search.html', films=films, years=years, genres=genres, search_query=search_query, selected_year=selected_year, selected_genre=selected_genre)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        
        if not login or not password:
            return "Логин и пароль не могут быть пустыми.", 400
      
        new_user = User(login=login, password=password)

        session.add(new_user)
        session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        user = db_session.query(User).filter_by(login=login).first()

        if user:
            if user.password == password:
                session['user_id'] = user.id  
                session['username'] = user.login 
                return redirect(url_for('search'))
            else:
                return "Неверный логин или пароль", 401 
        else:
            return "Пользователь не найден", 404 

    return render_template('login.html')




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
