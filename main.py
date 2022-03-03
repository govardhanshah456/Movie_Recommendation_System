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
        print("abc", l)
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
    session.pop('user', None)
    flash("Logged Out Successfully!")
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin1234':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['user'] = True
            flash("Logged In Successfully")
            return redirect(url_for('welcome'))
    return render_template('login.html', error=error)


@app.route("/welcome",methods=["GET","POST"])
def welcome():
    if 'user' in session and request.method=="POST":
        data = pd.read_csv("Added_movies.csv")
        data1 = pd.read_csv("Removed_movies.csv")
        data2 = pd.read_csv("Updated_movies.csv")
        l = list(data.values)
        m = list(data1.values)
        n = list(data2.values)
        return render_template("welcome.html", l=l, m=m, n=n)
    elif 'user' in session:
        data = pd.read_csv("Added_movies.csv")
        data1 = pd.read_csv("Removed_movies.csv")
        data2 = pd.read_csv("Updated_movies.csv")
        l = list(data.values)
        m = list(data1.values)
        n = list(data2.values)
        return render_template("welcome.html", l=l, m=m, n=n)
    flash("Session Expired")
    return redirect(url_for('login'))


def similarity_score(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


@app.route("/add", methods=["GET", "POST"])
def loggedin():
    error = None
    movie_added = None
    if request.method == "POST" and 'user' in session:
        # session["user"] = 'admin'
        moviename = request.form["moviename"]
        moviename = moviename.lower()
        actor1 = request.form["actor1"]
        actor2 = request.form["actor2"]
        actor3 = request.form["actor3"]
        directorname = request.form["directorname"]
        lang=request.form["lang"]
        lang=lang.lower()
        if lang=="yes":
            lang='en'
        elif lang=="no":
            lang='hi'
        else:
            flash("Enter Only Yes or No")
            return redirect(url_for('.add'))
        s = ""

        genre = request.form.getlist('optradio[]')
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
        dataset=pd.read_csv("final_dataset1.csv")
        print(moviename)
        print(directorname)
        dataset = dataset[(dataset.movie_title == moviename) & (dataset.director_name == directorname)]
        print(dataset)
        if dataset.empty:
            field_names = ['director_name', 'actor_1_name', 'actor_2_name', 'actor_3_name', 'genres', 'movie_title',
                           'comb']
            with open('final_dataset1.csv', 'a', newline=None) as ds:
                dict_writer = DictWriter(ds, fieldnames=field_names)
                dict_writer.writerow(dict)
                ds.close()
            df1 = pd.read_csv("final_dataset1.csv")
            df1.to_csv("final_dataset1.csv", index=False)
            movie_added = "Movie added successfully!"
            my_api_key = '04b9df5416d75be096abd805b24b47a1'
            title = moviename
            url = 'https://api.themoviedb.org/3/discover/movie?api_key='+my_api_key+'&with_text_query='+title+'&with_original_language='+lang
            data = requests.get(url)
            data = data.json()
            global x
            x = []
            for obj in data['results']:
                score = similarity_score(title, obj['title']);
                id = obj['id']
                x.append([score, id])
            x.sort()
            url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
                x[0][1])
            data = requests.get(url)
            data = data.json()
            poster_path = data['poster_path']
            if poster_path:
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                full_path="../static/notfound.jpg"
            field_names1 = ['Title', 'ImgURL']
            dict1 = {'Title': moviename, 'ImgURL': full_path}
            with open('Added_movies.csv', 'a') as ds:
                dict_writer = DictWriter(ds, fieldnames=field_names1)
                dict_writer.writerow(dict1)
                ds.close()
            df = pd.read_csv("Added_movies.csv")
            num_rows = df.count()[0]
            if num_rows > 5:
                df = df.iloc[1:, :]
            df = df.drop_duplicates()
            df.to_csv("Added_movies.csv", index=False)
            df1 = pd.read_csv("Removed_movies.csv")
            df1 = df1[df1.Title != moviename]
            df1.to_csv("Removed_movies.csv", index=False)
            flash("Movie Added Successfully!")
            return render_template("loggedin.html")
        else:
            flash("Movie Exists Already!")
            return render_template("loggedin.html")
    elif 'user' in session:
        return render_template("loggedin.html", error=None)
    flash("Session Expired!")
    return redirect(url_for('login'))


@app.route("/remove", methods=["GET", "POST"])
def remove():
    error = None
    if (request.method == "POST" and 'user' in session):
        moviename = request.form["moviename"]
        moviename = moviename.lower()
        directorname = request.form["director"]
        lang=request.form["lang"]
        lang=lang.lower()
        if lang=="yes":
            lang='en'
        elif lang=="no":
            lang='hi'
        else:
            flash("Enter Yes or No in Language")
            return redirect(url_for('remove'))
        print(directorname)
        dataset = pd.read_csv('final_dataset1.csv')
        # # if moviename not in dataset['movie_title'].unique():
        # df=pd.DataFrame(dataset)
        # df1=df.loc[df["comb"]==s1]
        # if df1.empty:
        df = dataset[dataset["movie_title"] == moviename]
        if df.shape[0]==0:
            flash("No Such Movie In Dataset!")
            return redirect(url_for('remove'))
        elif df.shape[0] > 1:
            print("inside")
            print(df)
            if directorname not in df["director_name"].unique():
                flash("No Such Movie Exist In Dataset!")
                return redirect(url_for('remove'))
            else:
                df = df[df["director_name"] == directorname]
                dataset = dataset.drop(
                    dataset[(dataset.movie_title == moviename) & (dataset.director_name == directorname)].index)
                dataset.to_csv("final_dataset1.csv",index=False)
                flash("Movie Deleted Successfully")
                return redirect(url_for('remove'))
        my_api_key = '04b9df5416d75be096abd805b24b47a1'
        title = moviename
        url = 'https://api.themoviedb.org/3/discover/movie?api_key=' + my_api_key + '&with_text_query=' + title + '&with_original_language=' + lang
        data = requests.get(url)
        data = data.json()
        global x
        x = []
        for obj in data['results']:
            score = similarity_score(title, obj['title']);
            id = obj['id']
            x.append([score, id])
        x.sort()
        url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
            x[0][1])
        data = requests.get(url)
        data = data.json()
        poster_path = data['poster_path']
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            full_path = "../static/notfound.jpg"
        field_names1 = ['Title', 'ImgURL']
        dict1 = {'Title': moviename, 'ImgURL': full_path}
        with open('Removed_movies.csv', 'a') as ds:
            dict_writer = DictWriter(ds, fieldnames=field_names1)
            dict_writer.writerow(dict1)
            ds.close()
        df = pd.read_csv("Removed_movies.csv")
        num_rows = df.count()[0]
        if num_rows > 5:
            df = df.iloc[1:, :]
        df = df.drop_duplicates()
        df.to_csv("Removed_movies.csv", index=False)
        df1 = pd.read_csv("Added_movies.csv")
        df1 = df1[df1.Title != moviename]
        df1.to_csv("Added_movies.csv", index=False)
        dataset.drop(dataset.loc[dataset['movie_title'] == moviename].index, inplace=True)
        dataset.to_csv("final_dataset1.csv", index=False)
        flash("Deleted Movie Successfully!")
        return redirect(url_for('remove'))
    elif 'user' in session:
        return render_template("remove.html", error=None)
    flash("Session Expired!")
    return redirect(url_for('login'))


@app.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "POST" and 'user' in session:
        moviename = request.form["moviename"]
        moviename = moviename.lower()
        director=request.form["directorname"]
        df = pd.read_csv("final_dataset1.csv")
        df1=df[(df.movie_title == moviename) & (df.director_name == director)]
        if df1.shape[0]==0:
            flash("No Such Movie Exist In Dataset!")
            return redirect(url_for('update'))
        df = df.loc[df["movie_title"] == moviename]
        actor1 = df["actor_1_name"].iloc[0]
        actor2 = df["actor_2_name"].iloc[0]
        actor3 = df["actor_3_name"].iloc[0]
        director = df["director_name"].iloc[0]
        genres = df["genres"].iloc[0]
        genres1 = genres
        genres = genres.split(" ")
        li = ["Crime", "Action", "Thriller", "Romance", "Sci-Fi", "Fantasy", "Documentary", "Comedy", "Drama", "Family",
              "Sports", "Adventure", "Horror", "Mystery"]
        new_li = list(set(li) - set(genres))
        print(genres)
        comb = df["comb"].iloc[0]
        # df = pd.read_csv("final_dataset1.csv")
        # df = df[df.movie_title != moviename]
        global movie
        movie = moviename
        global actor1_name
        actor1_name = actor1
        global actor2_name
        actor2_name = actor2
        global actor3_name
        actor3_name = actor3
        global director_name
        director_name = director
        global genres_of_movies
        genres_of_movies = genres1
        global combination
        combination = comb

        # df.column_name != whole string from the cell
        # now, all the rows with the column: Name and Value: "dog" will be deleted

        # df.to_csv("final_dataset1.csv", index=False)
        return render_template("update.html", moviename=moviename, actor1=actor1, actor2=actor2, actor3=actor3,
                               director=director, genres=genres, new_li=new_li)
    elif 'user' in session:
        return render_template("update_movie_search.html")
    flash("Session Expired!")
    return render_template("login.html", error=None)


@app.route("/update1", methods=["GET", "POST"])
def update1():
    if 'user' not in session:
        flash("Session Expired!")
        return redirect(url_for('login'))
    elif request.method == "POST" and 'user' in session:
        moviename = request.form["moviename"]
        moviename = moviename.lower()
        actor1 = request.form["actor1"]
        actor2 = request.form["actor2"]
        actor3 = request.form["actor3"]
        directorname = request.form["directorname"]
        dataset=pd.read_csv("final_dataset1.csv")
        dataset=dataset[(dataset.movie_title == moviename) & (dataset.director_name == directorname)]
        if dataset.shape[0]>0:
            flash("Movie Already Exist In Dataset")
            return redirect(url_for('update'))
        lang=request.form["lang"]
        lang = lang.lower()
        if lang == "yes":
            lang = 'en'
        elif lang == "no":
            lang = 'hi'
        else:
            flash("Enter Yes or No in Language")
            return redirect(url_for('remove'))
        s = ""
        genre = request.form.getlist('optradio[]')
        j = 0
        z = len(genre) - 1
        for i in genre:
            j += 1
            s += i
            if j <= z:
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
        data = pd.read_csv("final_dataset1.csv")
        findL = [director_name, actor1_name, actor2_name, actor3_name, genres_of_movies, movie, combination]
        replaceL = [directorname, actor1, actor2, actor3, s, moviename, s1]
        data = data.replace(findL, replaceL)
        data.to_csv("final_dataset1.csv", index=False)
        my_api_key = '04b9df5416d75be096abd805b24b47a1'
        title = moviename
        url = 'https://api.themoviedb.org/3/discover/movie?api_key=' + my_api_key + '&with_text_query=' + title + '&with_original_language=' + lang
        data = requests.get(url)
        data = data.json()
        global x
        x = []
        for obj in data['results']:
            score = similarity_score(title, obj['title']);
            id = obj['id']
            x.append([score, id])
        x.sort()
        url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
            x[0][1])
        data = requests.get(url)
        data = data.json()
        poster_path = data['poster_path']
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            full_path = "../static/notfound.jpg"
        field_names1 = ['Title', 'ImgURL']
        dict1 = {'Title': moviename, 'ImgURL': full_path}
        with open('Updated_movies.csv', 'a') as ds:
            dict_writer = DictWriter(ds, fieldnames=field_names1)
            dict_writer.writerow(dict1)
            ds.close()
        df = pd.read_csv("Updated_movies.csv")
        num_rows = df.count()[0]
        if num_rows > 5:
            df = df.iloc[1:, :]
        df = df.drop_duplicates()
        df.to_csv("Updated_movies.csv", index=False)
        flash("Movie Updated Successfully!")
        return redirect(url_for('update'))
    elif 'user' in session:
        return render_template("update_movie_search.html", error=None)


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
    global movie_reviews
    movie_reviews = {reviews[i]: sentiment[i] for i in range(len(reviews))}
    if movie_reviews is None:
        movie_reviews = {}
    return render_template('recommend.html', title=title, poster=poster, overview=overview, vote_average=vote_average,
                           vote_count=vote_count, release_date=release_date, runtime=runtime, status=status,
                           genres=genres,
                           movie_cards=movie_cards, reviews=movie_reviews, casts=casts, cast_details=cast_details)


if __name__ == '__main__':
    app.run(debug=True)
