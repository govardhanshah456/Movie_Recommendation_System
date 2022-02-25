import csv, datetime
from csv import DictWriter, writer
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, url_for, redirect, session, flash
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from bs4 import BeautifulSoup
import urllib
from werkzeug.utils import redirect
import pickle
import requests

filename = 'model.pkl'
clf = pickle.load(open(filename, 'rb'))
vectorizer = pickle.load(open('transform.pkl', 'rb'))

def create_similarity():
    data = pd.read_csv('final_dataset1.csv')
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'])
    similarity = cosine_similarity(count_matrix)
    return data, similarity


def recommend_movies(movie):
    movie = movie.lower()
    print(movie)
    data, similarity_factor = create_similarity()
    if movie not in data['movie_title'].unique():
        print("jooo")
        return ('Sorry! This Movie is Not in Our Database!')
    else:
        i = data.loc[data['movie_title'] == movie].index[0]
        lst = list(enumerate(similarity_factor[i]))
        lst = sorted(lst, key=lambda x: x[1], reverse=True)
        lst = lst[1:11]
        l = []
        for i in range(len(lst)):
            a = lst[i][0]
            l.append(data['movie_title'][a])
        print("abc",l)
        return l


def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["', '')
    my_list[-1] = my_list[-1].replace('"]', '')
    return my_list


def convert_to_list_num(my_list):
    my_list = my_list.split(',')
    my_list[0] = my_list[0].replace("[", "")
    my_list[-1] = my_list[-1].replace("]", "")
    return my_list


app = Flask(__name__)
app.secret_key = 'abcde'
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(seconds=30)
    session.modified = True


@app.route("/admin")
def index():
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect(url_for('login'))
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin1234':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['user'] = 'admin'
            return redirect(url_for('welcome'))
    return render_template('login.html', error=error)

@app.route("/welcome")
def welcome():
    return render_template("welcome.html",error="Logged In Successfully")
@app.route("/add", methods=["GET", "POST"])
def loggedin():
    error = None
    movie_added = None
    if request.method == "POST":
        # session["user"] = 'admin'
        moviename = request.form["moviename"]
        moviename=moviename.lower()
        actor1 = request.form["actor1"]
        actor2 = request.form["actor2"]
        actor3 = request.form["actor3"]
        directorname = request.form["directorname"]
        s = ""
        genre = request.form.getlist('optradio')
        genre.sort()
        print(genre)
        for i in genre:
            s += i
            s += " "
        dataset = pd.read_csv('final_dataset1.csv')
        # # if moviename not in dataset['movie_title'].unique():
        # df=pd.DataFrame(dataset)
        # df1=df.loc[df["comb"]==s1]
        # if df1.empty:
        s1 = ""
        s1 += actor1
        s1 += " "
        s1 += actor2
        s1 += " "
        s1 += actor3
        s1 += " "
        s1 += directorname
        s1 += " "
        s1 += s
        # df1=pd.DataFrame(dataset)
        # df2=[directorname,actor1,actor2,actor3,s,moviename,s1]
        # df1=pd.concat(df2)
        dict = {"director_name": directorname, "actor_1_name": actor1, "actor_2_name": actor2, "actor_3_name": actor3,
                "genres": s, "movie_title": moviename, "comb": s1}
        # dataset.append(df2,ignore_index=True)
        # df2={"director_name":directorname,"actor_1_name":actor1,"actor_2_name":actor2,"actor_3_name":actor3,"genres":s,"movie_title":moviename,"comb":s1}
        # df.loc[len(df.index)]=df2
        # df.to_csv('2019_Movie_data.csv',index=False)
        df = pd.DataFrame(dataset)
        df1 = df.loc[df["comb"] == s1]
        if df1.empty:
            field_names = ['director_name', 'actor_1_name', 'actor_2_name', 'actor_3_name', 'genres', 'movie_title',
                           'comb']
            with open('final_dataset1.csv', 'a', newline=None) as ds:
                dict_writer = DictWriter(ds, fieldnames=field_names)
                dict_writer.writerow(dict)
                ds.close()
            print("genre:", df1)
            df1=pd.read_csv("final_dataset1.csv")
            df1.to_csv("final_dataset1.csv",index=False)
            movie_added = "Movie added successfully!"
            return render_template("loggedin.html", error=movie_added)
        else:
            error = 'Movie already exists.Please try adding another one!!'
            print(error)
            print("Movie already exist")
            return render_template("loggedin.html", error=error)
    return render_template("loggedin.html", error=None)


@app.route("/remove", methods=["GET", "POST"])
def remove():
    error = None
    if (request.method == "POST"):
        moviename = request.form["moviename"]
        moviename=moviename.lower()
        dataset = pd.read_csv('final_dataset1.csv')
        # # if moviename not in dataset['movie_title'].unique():
        # df=pd.DataFrame(dataset)
        # df1=df.loc[df["comb"]==s1]
        # if df1.empty:
        if moviename not in dataset["movie_title"].unique():
            return render_template("remove.html", error="No Such Movies In Dataset")
        dataset.drop(dataset.loc[dataset['movie_title'] == moviename].index, inplace=True)
        dataset.to_csv("final_dataset1.csv", index=False)
        return render_template("remove.html", error="Deleted Successfully")
    return render_template("remove.html", error=error)


@app.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "POST":
        moviename = request.form["moviename"]
        moviename=moviename.lower()
        df = pd.read_csv("final_dataset1.csv")
        if moviename not in df["movie_title"].unique():
            return render_template("update_movie_search.html", error="No Such Movie In Database")
        df = df.loc[df["movie_title"] == moviename]
        actor1 = df["actor_1_name"].iloc[0]
        actor2 = df["actor_2_name"].iloc[0]
        actor3 = df["actor_3_name"].iloc[0]
        director = df["director_name"].iloc[0]
        genres = df["genres"].iloc[0]
        genres1=genres
        genres = genres.split(" ")
        li = ["Crime", "Action", "Thriller", "Romance", "Sci-Fi", "Fantasy", "Documentary", "Comedy", "Drama", "Family",
              "Sports", "Adventure","Horror","Mystery"]
        new_li = list(set(li) - set(genres))
        print(genres)
        comb = df["comb"].iloc[0]
        # df = pd.read_csv("final_dataset1.csv")
        # df = df[df.movie_title != moviename]
        global movie
        movie=moviename
        global actor1_name
        actor1_name=actor1
        global actor2_name
        actor2_name=actor2
        global actor3_name
        actor3_name=actor3
        global director_name
        director_name=director
        global genres_of_movies
        genres_of_movies=genres1
        global combination
        combination=comb

        # df.column_name != whole string from the cell
        # now, all the rows with the column: Name and Value: "dog" will be deleted

        # df.to_csv("final_dataset1.csv", index=False)
        return render_template("update.html", moviename=moviename, actor1=actor1, actor2=actor2, actor3=actor3,
                               director=director, genres=genres, new_li=new_li)
    return render_template("update_movie_search.html", error=None)


@app.route("/update1", methods=["GET", "POST"])
def update1():
    if request.method == "POST":
        moviename = request.form["moviename"]
        moviename=moviename.lower()
        actor1 = request.form["actor1"]
        actor2 = request.form["actor2"]
        actor3 = request.form["actor3"]
        directorname = request.form["directorname"]
        s = ""
        genre = request.form.getlist('optradio')
        j=0
        x=len(genre)-1
        for i in genre:
            j+=1
            s += i
            if j<=x:
                s += " "
        dataset = pd.read_csv('final_dataset1.csv')
        # # if moviename not in dataset['movie_title'].unique():
        # df=pd.DataFrame(dataset)
        # df1=df.loc[df["comb"]==s1]
        # if df1.empty:
        s1 = ""
        s1 += actor1
        s1 += " "
        s1 += actor2
        s1 += " "
        s1 += actor3
        s1 += " "
        s1 += directorname
        s1 += " "
        s1 += s
        data=pd.read_csv("final_dataset1.csv")
        findL = [director_name,actor1_name ,actor2_name,actor3_name,genres_of_movies,movie,combination]
        replaceL = [directorname,actor1, actor2, actor3,s,moviename,s1]
        data=data.replace(findL,replaceL)
        data.to_csv("final_dataset1.csv",index=False)
        return render_template("update.html", error="Movie Updated")
    return render_template("update.html", error=None)


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/similarity', methods=["POST"])
def similarity():
    movie = request.form['name']
    print(movie)
    recommend1 = recommend_movies(movie)
    print(recommend1)
    if isinstance(recommend1, str):
        return recommend_movies
    else:
        m_str = "---".join(recommend1)
        return m_str


@app.route('/recommend', methods=["POST"])
def recommend():
    title = request.form['title']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)
    cast_ids = cast_ids.split(',')
    cast_ids[0] = cast_ids[0].replace("[", "")
    cast_ids[-1] = cast_ids[-1].replace("]", "")
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"', '\"')
    movie_cards = {
        rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))
    }
    casts = {
        cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))
    }
    cast_details = {
        cast_names[i]: [cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in
        range(len(cast_places))
    }
    url = 'https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_result = soup.find_all("div", {"class": "text show-more__control"})
    reviews = []
    sentiment = []
    for i in soup_result:
        if i.string:
            reviews.append(i.string)
            List = np.array([i.string])
            vector = vectorizer.transform(List)
            val = clf.predict(vector)
            sentiment.append('Positive' if val else 'Negative')
            movie_reviews = {reviews[i]: sentiment[i] for i in range(len(reviews))}
    return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                           vote_count=vote_count, release_date=release_date, runtime=runtime, status=status,
                           genres=genres,
                           movie_cards=movie_cards, reviews=movie_reviews, casts=casts, cast_details=cast_details)


if __name__ == '__main__':
    app.run(debug=True)
