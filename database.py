from typing import Tuple
from connection_pool import get_cursor


Poll = Tuple[int, str, str]
Option = Tuple[int, str, int]
Vote = Tuple[str, int]

CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls
(id SERIAL PRIMARY KEY, название TEXT, имя_создателя TEXT);"""
CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options
(id SERIAL PRIMARY KEY, текст_выбора TEXT, id_опроса INTEGER, FOREIGN KEY(id_опроса) REFERENCES polls (id));"""
CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes
(имя_пользователя TEXT, id_выбора INTEGER, временная_метка_голосования INTEGER, FOREIGN KEY(id_выбора) 
REFERENCES options (id));"""

SELECT_POLL = "SELECT * FROM polls WHERE id = %s"
SELECT_ALL_POLLS = "SELECT * FROM polls;"
SELECT_POLL_OPTIONS = "SELECT * FROM options WHERE id_опроса = %s;"
SELECT_LATEST_POLL = """SELECT * FROM polls
WHERE polls.id = (
    SELECT id FROM polls ORDER BY DESC LIMIT 1
);"""

SELECT_OPTION = "SELECT * FROM options WHERE id = %s;"
SELECT_VOTES_FOR_OPTION = "SELECT * FROM votes WHERE id_выбора = %s"


INSERT_POLLS_RETURN_ID = "INSERT INTO polls (название, имя_создателя) VALUES (%s, %s) RETURNING id;"
INSERT_OPTION_RETURNING_ID = "INSERT INTO options (текст_выбора, id_опроса) VALUES (%s, %s) RETURNING id;"
INSERT_VOTE = "INSERT INTO votes (имя_пользователя, id_выбора, временная_метка_голосования) VALUES (%s, %s, %s);"


def create_tables(connection):
    with get_cursor(connection) as cursor:
        cursor.execute(CREATE_POLLS)
        cursor.execute(CREATE_OPTIONS)
        cursor.execute(CREATE_VOTES)


# -- Polls --

def create_poll(connection, title: str, owner: str):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_POLLS_RETURN_ID, (title, owner))

        poll_id = cursor.fetchone()[0]
        return poll_id


def get_polls(connection) -> list[Poll]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_ALL_POLLS)
        return cursor.fetchall()


def get_poll(connection, poll_id) -> Poll:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLL, (poll_id,))
        return cursor.fetchone()


def get_latest_poll(connection) -> Poll:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_LATEST_POLL)
        return cursor.fetchone()


def get_poll_options(connection, poll_id: int) -> list[Option]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLL_OPTIONS, (poll_id,))
        return cursor.fetchall()


# -- Options --

def get_option(connection, option_id: int) -> Option:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_OPTION, (option_id,))
        return cursor.fetchone()


def add_option(connection, option_text: str, poll_id: int):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_OPTION_RETURNING_ID, (option_text, poll_id))
        option_id = cursor.fetchone()[0]
        return option_id


# -- Votes --

def get_votes_for_option(connection, option_id: int) -> list[Vote]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_VOTES_FOR_OPTION, (option_id,))
        return cursor.fetchall()


def add_poll_vote(connection, username: str, vote_timestamp: float, option_id: int):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_VOTE, (username, option_id, vote_timestamp))
