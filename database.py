from typing import Tuple
from psycopg2.extras import execute_values

Poll = Tuple[int, str, str]
Vote = Tuple[str, int]
PollWithOption = Tuple[int, str, str, int, str, int]
PollResults = Tuple[int, str, int, float]

CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls
(id SERIAL PRIMARY KEY, название TEXT, имя_создателя TEXT);"""
CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options
(id SERIAL PRIMARY KEY, текст_выбора TEXT, id_опроса INTEGER, FOREIGN KEY(id_опроса) REFERENCES polls (id));"""
CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes
(имя_пользователя TEXT, id_выбора INTEGER, FOREIGN KEY(id_выбора) REFERENCES options (id));"""


SELECT_ALL_POLLS = "SELECT * FROM polls;"
SELECT_POLL_WITH_OPTIONS = """SELECT * FROM polls
JOIN options ON polls.id = options.id_опроса
WHERE polls.id = %s;"""
SELECT_LATEST_POLL = """SELECT * FROM polls
JOIN options ON polls.id = options.id_опроса 
WHERE polls.id = (
    SELECT id FROM polls ORDER BY DESC LIMIT 1
);"""
SELECT_POLL_VOTE_DETAILS = "SELECT * FROM votes WHERE id_выбора = %s ORDER BY RANDOM() LIMIT 1;"
SELECT_VOTE_RESULTS = """SELECT 
    options.id_опроса, options.текст_выбора,
    COUNT(votes.id_выбора) AS количество_голосов,
    COUNT(votes.id_выбора) / SUM(COUNT(votes.id_выбора)) OVER() * 100.0 AS проценты
FROM options
LEFT JOIN votes ON options.id = votes.id_выбора
WHERE options.id_опроса = %s
GROUP BY options.id 
;"""

INSERT_POLLS_RETURN_ID = "INSERT INTO polls (название, имя_создателя) VALUES (%s, %s) RETURNING id;"
INSERT_OPTION = "INSERT INTO options (текст_выбора, id_опроса) VALUES %s;"
INSERT_VOTE = "INSERT INTO votes (имя_пользователя, id_выбора) VALUES (%s, %s);"


def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_POLLS)
            cursor.execute(CREATE_OPTIONS)
            cursor.execute(CREATE_VOTES)


def get_polls(connection) -> list[Poll]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_POLLS)
            return cursor.fetchall()


def get_latest_poll(connection) -> list[PollWithOption]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_LATEST_POLL)
            return cursor.fetchall()


def get_poll_details(connection, poll_id: int) -> list[PollWithOption]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_WITH_OPTIONS, (poll_id,))
            return cursor.fetchall()


def get_poll_and_vote_results(connection, poll_id: int) -> list[PollResults]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_VOTE_RESULTS, (poll_id,))
            return cursor.fetchall()


def get_random_poll_vote(connection, option_id: int) -> Vote:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_VOTE_DETAILS, (option_id,))
            return cursor.fetchone()


def create_poll(connection, title: str, owner: str, options: list[str]):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_POLLS_RETURN_ID, (title, owner))

            poll_id = cursor.fetchone()[0]
            option_values = [(option_text, poll_id) for option_text in options]

            execute_values(cursor, INSERT_OPTION, option_values)


def add_poll_vote(connection, username: str, option_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_VOTE, (username, option_id))
