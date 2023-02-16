from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreateMatchForm
from flask_gravatar import Gravatar
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from functools import wraps
from flask import abort
import os
import pandas as pd
from IPython.display import HTML
import plotly.express as px
import plotly.io as pio
import numpy as np
from plotly.offline import plot
from plotly.graph_objs import Scatter
from flask import Markup

pio.templates.default = "plotly_white"

data = pd.read_csv("t20-world-cup-22.csv")
login_manager = LoginManager()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new_users.db"
#Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "super secret key"
db = SQLAlchemy(app)
# login_manager.init_app(app)

##CREATE TABLE
class Userwc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)

db.create_all()


df = pd.read_csv("t20-world-cup-22.csv", index_col=False)
arr = []


def make_clickable(url, name):
    return '<a href="{}" rel="noopener noreferrer" target="_blank">{}</a>'.format(url, name)


links = ['https://2022.t20worldcup.com/video/2866929', 'https://2022.t20worldcup.com/video/2867782',
         'https://2022.t20worldcup.com/video/2869237', 'https://2022.t20worldcup.com/video/2869705',
         'https://2022.t20worldcup.com/video/2872860', 'https://2022.t20worldcup.com/video/2873203',
         'https://2022.t20worldcup.com/video/2874701', 'https://2022.t20worldcup.com/video/2875333', '',
         'https://2022.t20worldcup.com/video/2878787', 'https://2022.t20worldcup.com/video/2876885',
         'https://2022.t20worldcup.com/video/2877363', '', '', 'https://2022.t20worldcup.com/video/2879430',
         'https://2022.t20worldcup.com/video/2882736', 'https://2022.t20worldcup.com/video/2882978',
         'https://2022.t20worldcup.com/video/2883589', 'https://2022.t20worldcup.com/video/2885258',
         'https://2022.t20worldcup.com/video/2886225', 'https://2022.t20worldcup.com/video/2886530',
         'https://2022.t20worldcup.com/video/2887489', 'https://2022.t20worldcup.com/video/2887882',
         'https://2022.t20worldcup.com/video/2889101', 'https://2022.t20worldcup.com/video/2890159',
         'https://2022.t20worldcup.com/video/2890570', 'https://2022.t20worldcup.com/video/2891571',
         'https://2022.t20worldcup.com/video/2893962', 'https://2022.t20worldcup.com/video/2894158',
         'https://2022.t20worldcup.com/video/2894422', 'https://2022.t20worldcup.com/video/2899838',
         'https://2022.t20worldcup.com/video/2901048', 'https://2022.t20worldcup.com/video/2907679']
# df['highlights'] = df.apply(lambda x: make_clickable(x['links'], x['names']), axis=1)

for index, row in df.iterrows():
    winner = row["winner"]
    if row["won by"] == "Runs":
        runs = int(row["first innings score"] - row["second innings score"])

        arr.append(f"{winner} won by {runs} runs")
    elif row["won by"] == "Wickets":
        wickets_left = int(10 - row["second innings wickets"])

        arr.append(f"{winner} won by {wickets_left} wickets")
    else:
        arr.append("No Result")
df["Result"] = arr
df["Highlights"] = links
HTML(df.to_html(render_links=True, escape=False))

@app.route('/')
def home():
    # Every render_template has a logged_in variable set
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if Userwc.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            # print("You've already signed up with that email, log in instead!")
            # flash("You've already signed up with that email, log in instead!")
            return "User added already"
            # return redirect(url_for('login'))
        new_user = Userwc(
            email=request.form.get('email'),
            name=request.form['name'],
            password=request.form['password']
        )
        db.session.add(new_user)
        db.session.commit()
        # Log in and authenticate user after adding details to database
        return redirect(url_for('home'))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Finding user by email entered
        user = Userwc.query.filter_by(email=email).first()
        # Email does n't exist
        if not user:
            # flash("That email does not exist, please try again.")
            print("email bhul")
            return redirect(url_for('login'))
        # Password Incorrect
        elif not user.password == password:
            # flash("Password Incorrect, Please Try again.")
            print("password bhul")
            return redirect(url_for('login'))
        # email exists and password is correct for the given email
        else:
            return redirect(url_for('home'))

    return render_template("login.html")



@app.route('/schedule')
def schedule():
    new_df = df[["venue", "stage", "team1", "team2", "Result"]]
    pd.set_option('colheader_justify', 'center')  # FOR TABLE <th>

    html_string = '''
    <html>
      <head>
      <title>ICC t20 World Cup Schedule</title>
      <style> 
         bal
         {{
            width: 80%;
         }}
         table.a
          {{
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 3rem;
            font-family: sans-serif;
            width: 100%;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }}
         table
          {{
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 3rem;
            font-family: sans-serif;
            width: 100%;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }}
        tr {{
        
        background-color: #009879;;
        color: #ffffff;
        text-align: left;
        }}
        th {{
        background-color: green;;
        color: #ffffff;
        padding: 12px 15px;
        }}
        td {{
        padding: 12px 15px;
        }}
      </style>
      </head>
      <body>
        
        <div class="bal"> 
        <table class="a">
        <tr>
        <td>
        <img src="static/img/t20_logo.jpg" width=90%>
        </td>
        <td>
        <h1 align="center">Fixtures of T20 World Cup 2022</h1>
        </td>
        </table>
        </div>
        {table}
      </body>
    </html>.
    '''

    # OUTPUT AN HTML FILE
    with open('templates/schedule.html', 'w') as f:
        f.write(html_string.format(table=new_df.to_html()))

    return render_template("schedule.html")


@app.route('/<string:team1>vs<string:team2>')
def get_details_about_match(team1,team2):
    first_team = team1
    second_team = team2

    result = df.query(
        "(team1 == @first_team and team2 == @second_team) or team1 == @second_team and team2 == @first_team")
    seriees = list(result["Result"])
    team1 = list(result.get('team1'))[0]
    team2 = list(result.get('team2'))[0]
    stage = list
    if seriees[0] != "No Result" and list(result.get('stage'))[0] != 'Final' and list(result.get('stage'))[
        0] != 'Semi-final':

        venue = list(result.get('venue'))[0]
        toss_won = list(result.get('toss winner'))[0]
        decision = list(result.get('toss decision'))[0]
        team_won = list(result.get('winner'))[0]
        answer = f"{seriees[0]} . The match took place in {venue} . {toss_won} won the toss and chose to {decision} first." \
                 "It was a great performance from both sides but the winning team could adjust to the conditions " \
                 "better and " \
                 "emerged " \
                 "victorious at the end. "

        title = f"{team1} vs {team2}"
        team1 = "".join(team1.split())
        team2 = "".join(team2.split())

        html_string = '''
                <html>
                  <head>
                  <title>Super 12</title>
                  <style> 
                    body {
                    background-color : #00ffff;
                     }
                 div.text-article {
                    display: flex;
                    color: #000;
                    display: block;
                    width: 100%;
                    font-size: 4em;
                    font-size: 40px
        
                  }
        
        
                  div.text-article:first-letter {
                    color: green;
                    float:center;
                    font-weight: bold;
                    font-size: 60px;
                    font-size: 6rem;
                    line-height: 40px;
                    line-height: 4rem;
                    height:4rem;
                    text-transform: uppercase;
                  }
        
        
                  img.center {
                      display: block;
                      margin-left: auto;
                      margin-right: auto;
                      width: 40%;
                      height: 50%
                  }
                  h1 {
                  text-align: center;
                  font-size: 80px;
                  
                  }
                  p {
                  margin-left : 15%;
                  margin-right: 15%;
                  font-family: arial;
                  font-size: 50px;
                  color: white;
                  }

                  </style>
                  </head>
                  <body>
                     
                      <h1>{{title}}</h1>
                
                      <p align="center"> {{ answer }} </p>
                      <p align="right"><a href={{link}}>Watch the highlights</a></p>
                     
                    
                  </body>
                </html>.
                '''
        link = list(result["Highlights"])[0]
        print(type(link))
        with open(f'templates/{team1}vs{team2}.html', 'w') as f:
            f.write(html_string)
        return render_template(f"{team1}vs{team2}.html", answer=answer, link=link, title=title)
    elif seriees[0] != "No Result" and list(result.get('stage'))[0] != 'Semi-final':
        return redirect(url_for('final'))
    elif list(result.get('stage'))[0] == 'Semi-final':
        if team1 == "India" or "team2" == "India":
            return redirect(url_for('semi_final2'))
        else:
            return redirect(url_for('semi_final1'))


@app.route('/final')
def final():
    result = df.query("stage == 'Final'")
    team1 = list(result.get('team1'))[0]
    team2 = list(result.get('team2'))[0]
    seriees = list(result["Result"])
    venue = list(result.get('venue'))[0]
    toss_won = list(result.get('toss winner'))[0]
    decision = list(result.get('toss decision'))[0]
    team_won = list(result.get('winner'))[0]
    most_score = list(result.get('highest score'))[0]
    top_score = list(result.get('top scorer'))[0]
    best_bowler = list(result.get('best bowler'))[0]
    bowling_figure = list(result.get('best bowling figure'))[0]
    player_of_the_match = list(result.get('player of the match'))[0]
    if team_won == toss_won:

        answer = f"The final match took place in {venue} . {toss_won} won the toss and chose to {decision} first ." \
                 f"The decision to {decision} proved very beneficial and took a major role in the game. " \
                 f"{seriees[0]}. {top_score} scored {most_score} with brilliant timming and proved costly to the bowler. " \
                 "It was a great performance from both sides but the winning team could adjust to the conditions " \
                 "better and " \
                 "emerged " \
                 "victorious at the end ."
    else:

        answer = f"The final match took place in {venue} . {toss_won} won the toss and chose to {decision} first ." \
                 f"The decision to {decision} proved hard to the losing team and played a important part in the match. " \
                 f"{seriees[0]}. {top_score} scored {most_score} with brilliant timming and proved costly to the bowler. " \
                 "It was a great performance from both sides but the winning team could adjust to the conditions " \
                 "better and " \
                 "emerged " \
                 "victorious at the end ."
    title = f"{team1} vs {team2}"
    team1 = "".join(team1.split())
    team2 = "".join(team2.split())

    html_string = '''
                    <html>
                      <head>
                      <title>Final Showdown</title>
                      <style> 
                        body {
                        background-color : #00ffff;
                         }
                     div.text-article {
                        display: flex;
                        color: #000;
                        display: block;
                        width: 100%;
                        font-size: 4em;
                        font-size: 40px

                      }


                      div.text-article:first-letter {
                        color: green;
                        float:center;
                        font-weight: bold;
                        font-size: 60px;
                        font-size: 6rem;
                        line-height: 40px;
                        line-height: 4rem;
                        height:4rem;
                        text-transform: uppercase;
                      }


                      img.center {
                          display: block;
                          margin-left: auto;
                          margin-right: auto;
                          width: 40%;
                          height: 50%
                      }
                      h1 {
                      text-align: center;
                      font-size: 80px;

                      }
                      p {
                      margin-left : 15%;
                      margin-right: 15%;
                      font-family: arial;
                      font-size: 50px;
                      color: white;
                      }

                      </style>
                      </head>
                      <body>

                          <h1>{{title}}</h1>

                          <p align="center"> {{ answer }} </p>
                          <p align="right"><a href={{link}}>Watch the highlights</a></p>


                      </body>
                    </html>.
                    '''
    link = list(result["Highlights"])[0]
    with open('templates/Final.html', 'w') as f:
        f.write(html_string)
    return render_template("Final.html", answer=answer, link=link,title=title)


@app.route('/semi_final1')
def semi_final1():
    team1 = "New Zealand"
    team2 = "Pakistan"
    pd.set_option('colheader_justify', 'center')
    result = df.query(
        "(team1 == @team1 and team2 == @team2) or team1 == @team2 and team2 == @team1")
    seriees = list(result["Result"])

    venue = list(result.get('venue'))[0]
    toss_won = list(result.get('toss winner'))[0]
    decision = list(result.get('toss decision'))[0]
    team_won = list(result.get('winner'))[0]
    answer = f"{seriees[0]} . The Semi-Finale match took place in {venue} . {toss_won} won the toss and chose to {decision} first." \
             "It was a great performance from both sides but the winning team could adjust to the conditions " \
             "better and " \
             "emerged " \
             "victorious at the end. "

    title = f"{team1} vs {team2}"
    team1 = "".join(team1.split())
    team2 = "".join(team2.split())

    html_string = '''
                <html>
                  <head>
                  <title>Semi Finale 1</title>
                  <style> 
                    body {
                    background-color : #00ffff;
                     }
                 div.text-article {
                    display: flex;
                    color: #000;
                    display: block;
                    width: 100%;
                    font-size: 4em;
                    font-size: 40px

                  }


                  div.text-article:first-letter {
                    color: green;
                    float:center;
                    font-weight: bold;
                    font-size: 60px;
                    font-size: 6rem;
                    line-height: 40px;
                    line-height: 4rem;
                    height:4rem;
                    text-transform: uppercase;
                  }


                  img.center {
                      display: block;
                      margin-left: auto;
                      margin-right: auto;
                      width: 40%;
                      height: 50%
                  }
                  h1 {
                  text-align: center;
                  font-size: 80px;

                  }
                  p {
                  margin-left : 15%;
                  margin-right: 15%;
                  font-family: arial;
                  font-size: 3rem;
                  color: white;
                  }

                  </style>
                  </head>
                  <body>

                      <h1>{{title}}</h1>

                      <p align="center"> {{ answer }} </p>
                      <p align="right"><a href={{link}}>Watch the highlights</a></p>


                  </body>
                </html>.
                '''
    link = list(result["Highlights"])[0]
    print(type(link))
    with open(f'templates/Semi-final1.html', 'w') as f:
        f.write(html_string)
    return render_template(f"Semi-final1.html", answer=answer, link=link, title=title)


@app.route('/semi_final2')
def semi_final2():
    team1 = "England"
    team2 = "India"
    pd.set_option('colheader_justify', 'center')
    result = df.query(
        "(team1 == @team1 and team2 == @team2) or team1 == @team2 and team2 == @team1")
    seriees = list(result["Result"])

    venue = list(result.get('venue'))[0]
    toss_won = list(result.get('toss winner'))[0]
    decision = list(result.get('toss decision'))[0]
    team_won = list(result.get('winner'))[0]
    answer = f"{seriees[0]} . The Semi-Finale match took place in {venue} . {toss_won} won the toss and chose to {decision} first." \
             "It was a great performance from both sides but the winning team could adjust to the conditions " \
             "better and " \
             "emerged " \
             "victorious at the end. "

    title = f"{team1} vs {team2}"
    team1 = "".join(team1.split())
    team2 = "".join(team2.split())

    html_string = '''
                <html>
                  <head>
                  <title>Semi Finale 1</title>
                  <style> 
                    body {
                    background-color : #00ffff;
                     }
                 div.text-article {
                    display: flex;
                    color: #000;
                    display: block;
                    width: 100%;
                    font-size: 4em;
                    font-size: 40px

                  }


                  div.text-article:first-letter {
                    color: green;
                    float:center;
                    font-weight: bold;
                    font-size: 60px;
                    font-size: 6rem;
                    line-height: 40px;
                    line-height: 4rem;
                    height:4rem;
                    text-transform: uppercase;
                  }


                  img.center {
                      display: block;
                      margin-left: auto;
                      margin-right: auto;
                      width: 40%;
                      height: 50%
                  }
                  h1 {
                  text-align: center;
                  font-size: 80px;

                  }
                  p {
                  margin-left : 15%;
                  margin-right: 15%;
                  font-family: arial;
                  font-size: 3rem;
                  color: white;
                  }

                  </style>
                  </head>
                  <body>

                      <h1>{{title}}</h1>

                      <p align="center"> {{ answer }} </p>
                      <p align="right"><a href={{link}}>Watch the highlights</a></p>


                  </body>
                </html>.
                '''
    link = list(result["Highlights"])[0]
    print(type(link))
    with open(f'templates/Semi-final2.html', 'w') as f:
        f.write(html_string)
    return render_template(f"Semi-final2.html", answer=answer, link=link, title=title)


@app.route("/get_best_player")
def get_tournament_best_player():
    # OUTPUT AN HTML FILE
    return render_template("best-player.html")


@app.route("/get_best_batsman")
def get_best_batsman():
    pio.templates.default = "plotly_white"

    df = pd.read_csv("t20-world-cup-22.csv")
    # print(df.head(10))
    # Number of teams in team1,team2S
    print(np.unique(df[["team1", "team2"]].values))
    # Top scorer in T20 world cup
    figure = px.bar(df,
                    x=df["top scorer"],
                    y=df["highest score"],
                    color=df["highest score"],
                    title="Top Scorers in t20 World Cup 2022")
    figure.show()
    return render_template("best-batsman.html")


@app.route("/get_best_bowler")
def get_best_bowler():

    return render_template("best-bowler.html")


@app.route("/get_most_runs_by_a_batsman")
def get_most_scored_batsman():
    most_runs = 0

    for index, row in df.iterrows():
        if row["highest score"] and (row["highest score"]) > most_runs:
            most_runs = int(row["highest score"])
            batsman = row["top scorer"]
    score = 0
    batsmen = {}
    for index, row in df.iterrows():

        try:

            score = int(row["highest score"])

        except:
            score = 0
        batsman = row["top scorer"]

        if batsman not in batsmen and type(batsman) == str:
            batsmen[batsman] = score


        elif batsman in batsmen:
            batsmen[batsman] = max(score, batsmen[batsman])

    return jsonify({"batsman":batsman,"score":score})

# @app.route("/get_best_wicket_stats")
def get_best_wicket_stats():
    max_wickets = 0
    calender = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "July": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                "Nov": 11, "Dec": 12}
    bowlers = {}
    for index, row in df.iterrows():

        try:

            wickets = int(row["best bowling figure"][0:2])
        except TypeError:
            wickets = wickets
        except:
            wickets = calender[row["best bowling figure"][0:3]]

        if wickets > max_wickets:

            max_wickets = wickets
            player = row["best bowler"]
            if player not in bowlers:
                bowlers[player] = max_wickets
            if player in bowlers:
                if bowlers[player] > max_wickets:
                    bowlers[player] = max_wickets
    print(bowlers)

@app.route("/my_team/<string:name>/")
def get_all_matches_played(name):
    team = name
    result = df.query("team1 == @team or team2 == @team")
    result_df = result[["venue", "stage", "team1", "team2", "Result"]]
    pd.set_option('colheader_justify', 'center')  # FOR TABLE <th>

    html_string = '''
        <html>
          <head>
          <title>Matches played by your country</title>
          <style> 
             bal
             {{
                width: 80%;
             }}
             table.a
              {{
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 3rem;
                font-family: sans-serif;
                width: 100%;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }}
             table
              {{
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 3rem;
                font-family: sans-serif;
                width: 100%;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }}
            tr {{

            background-color: #009879;;
            color: #ffffff;
            text-align: left;
            }}
            th {{
            background-color: green;;
            color: #ffffff;
            padding: 12px 15px;
            }}
            td {{
            padding: 12px 15px;
            }}
          </style>
          </head>
          <body>

            <div class="bal"> 
            <table class="a">
            <tr>
            <td>
            <img src="static/img/t20_logo.jpg" width=90%>
            </td>
            <td>
            <h1 align="center">Fixtures of Your Team</h1>
            </td>
            </table>
            </div>
            {table}
          </body>
        </html>.
        '''

    # OUTPUT AN HTML FILE
    with open(f'templates/scheduleteam{name}.html', 'w') as f:
        f.write(html_string.format(table=result_df.to_html()))

    return render_template(f"scheduleteam{name}.html")

@app.route('/about')
def about():
    return redirect('https://en.wikipedia.org/wiki/2022_ICC_Men%27s_T20_World_Cup')

@app.route('/venues')
def venues():
    return redirect('https://2022.t20worldcup.com/venues')
@app.route('/logout')
def logout():
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
