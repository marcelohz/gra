import csv
import json
import os
import sqlite3
import sys

from flask import Flask

app = Flask(__name__)

print(sys.argv[0])

# db_file = r'.\gra.db'
db_file = ':memory:'
csv_file = os.path.join(os.path.dirname(sys.argv[0]), 'movielist (2).csv')
conn = None


def query_db(query, args=(), one=False):
    global conn
    cur = conn.cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.close()
    return (r[0] if r else None) if one else r


def create_db():
    if os.path.exists(db_file):
        os.remove(db_file)
    global conn
    conn = sqlite3.connect(db_file, check_same_thread=False)
    conn.execute("""
            create table award (
            id          integer primary key autoincrement,
            year        integer,
            title       text,
            studios     text,
            winner      integer
            );
    """)
    conn.execute("""
            create table producer (
            id          integer primary key autoincrement,
            name        text,
            award_id    integer,
            FOREIGN KEY(award_id) REFERENCES award(id) 
            )
    """)
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        movies = csv.reader(csvfile, delimiter=';')
        next(movies)
        for year, title, studios, producers_raw, winner_raw in movies:
            winner = 1 if winner_raw == 'yes' else 0
            cursor = conn.cursor()
            cursor.execute('insert into award(year, title, studios, winner) values (?, ?, ?, ?)',
                           (year, title, studios, winner))
            last_id = cursor.lastrowid
            cursor.close()

            #  fix some problems and typos
            # producers_raw = producers_raw.replace('Robbinsand', 'Robbins and')
            # producers_raw = producers_raw.replace('Sid and Marty', 'Sid & Marty')  # avoid splitting
            # producers_raw = producers_raw.replace('Michael DeLuca', 'Michael De Luca')  # imdb.com/name/nm0006894/
            # producers_raw = producers_raw.replace('Norm Golightly', 'Norman Golightly')
            # producers_raw = producers_raw.replace('Rick Alvares', 'Rick Alvarez')  # imdb.com/name/nm0023315/

            producers_raw = producers_raw.replace(', and', ', ').replace(' and ', ', ')
            producers = producers_raw.split(',')
            for producer in producers:
                conn.execute('insert into producer(name, award_id) values(? ,?)', (producer.strip(), last_id))
    conn.commit()


def find_interval(minimum_interval):
    if minimum_interval:
        sql = """with crude as (select (lag(year) over (partition by name order by year)) as previousWin,
                year as followingWin, name, year - (lag(year) over (partition by name order by year)) as interval
                from award inner join producer on award.id = producer.award_id where winner = 1)
                select name as producer, interval, previousWin, followingWin from crude
                where interval is not null and (interval = (select min(interval) from crude)) order by name"""
    else:
        sql = """with crude as (select (lag(year) over (partition by name order by year)) as previousWin,
                year as followingWin, name, year - (lag(year) over (partition by name order by year)) as interval
                from award inner join producer on award.id = producer.award_id where winner = 1)
                select name as producer, interval, previousWin, followingWin from crude
                where interval is not null and (interval = (select max(interval) from crude)) order by name"""
    rows = query_db(sql)
    return rows


@app.route('/awards/year/<year>')
def awards_year(year):
    sql = """select year, title, studios,  group_concat(name, ', ') as producers,
                case when winner = 1 then 'Yes' else 'No' end as winner
                from award inner join producer on producer.award_id = award.id
                where year = ? group by year, title, studios, winner order by winner desc, title"""
    rows = query_db(sql, (year,))
    return json.dumps(rows, indent=4)


@app.route('/awards/studio/<studio>')
def awards_studio(studio):
    sql = """select year, title, studios,  group_concat(name, ', ') as producers,
                case when winner = 1 then 'Yes' else 'No' end as winner
                from award inner join producer on producer.award_id = award.id
                where studios like ? group by year, title, studios, winner order by year, title"""
    rows = query_db(sql, (studio,))
    return json.dumps(rows, indent=4)


@app.route('/awards/producer/<producer>')
def awards_producer(producer):
    sql = """with base as (select year, title, studios,  group_concat(name, ', ') as producers, winner
                    from award inner join producer on producer.award_id = award.id
                    group by year, title, studios, winner)
                    select year, title, studios, producers, case when winner = 1 then 'Yes' else 'No' end as winner
    				from base where producers like ? order by year, title"""
    rows = query_db(sql, ('%' + producer + '%',))
    return json.dumps(rows, indent=4)


@app.route('/awards/winner/<year>')
def awards_winner(year):
    sql = """select year, title, studios,  group_concat(name, ', ') as producers
                from award inner join producer on producer.award_id = award.id
                where winner = 1 and year = ? group by year, title, studios, winner order by year, title"""
    rows = query_db(sql, (year,))
    return json.dumps(rows, indent=4)


@app.route('/awards/winners')
def awards_winners():
    sql = """select year, title, studios,  group_concat(name, ', ') as producers
                from award inner join producer on producer.award_id = award.id
                where winner = 1 group by year, title, studios, winner order by year, title"""
    rows = query_db(sql)
    return json.dumps(rows, indent=4)


@app.route('/awards/min_max')
def min_max():
    ints = {'min': find_interval(True), 'max': find_interval(False)}
    return json.dumps(ints, indent=4)


@app.route('/')
def root():
    return r"We're in the pipe, five by five.<br>- Corporal Ferro, Aliens (1986)"


create_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0')

