from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField
# from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Top-10-Movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# API fetched from environment Variable
# get your API "https://developer.themoviedb.org/docs"
TMDB_API = os.environ.get("TMDB_API")


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


@app.route("/", methods=['GET', 'POST'])
def home():
    # with app.app_context():
    all_movies = Movie.query.order_by(Movie.rating).all()

    # for i in range(len(all_movies)):
    #
    #     # This line gives each movie a new ranking reversed from their order in all_movies
    #     all_movies[i].ranking = len(all_movies) - i
    #     db.session.commit()
    return render_template('index.html', movies=all_movies)


@app.route("/edit", methods=['GET', 'POST'])
def edit_rating():
    if request.method == "POST":
        # UPDATE RECORD
        movie_id = request.form["id"]
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = request.form["rating"]
        movie_to_update.review = request.form["review"]
        db.session.commit()

        return redirect(url_for('home'))
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)
    return render_template("edit.html", movie=movie_selected)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        movie_title = request.form["title"]
        movie_search = requests.get('https://api.themoviedb.org/3/search/movie?',
                                    params={'api_key': TMDB_API, 'query': movie_title})

        search_result = movie_search.json()['results']
        print(search_result)
        return render_template("select.html", options=search_result)

    return render_template('add.html')


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    print(movie_api_id)
    if movie_api_id:
        movie_api_url = f"https://api.themoviedb.org/3/movie/{movie_api_id}"
        #     # The language parameter is optional, if you were making the website for a different audience
        #     # e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": TMDB_API,
                                                       "language": "en-US"})
        data = response.json()
        with app.app_context():
            new_movie = Movie(title=data['title'], year=data['release_date'].split("-")[0],
                              description=data['overview'],
                              rating=data['popularity'] / 10, ranking=data['vote_average'], review=data['tagline'],
                              img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
                              )
            db.session.add(new_movie)
            print(new_movie)
            db.session.commit()
            return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
