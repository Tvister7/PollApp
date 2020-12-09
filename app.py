import os
import psycopg2
from psycopg2.errors import DivisionByZero
from dotenv import load_dotenv
import database


DATABASE_PROMPT = ""
MENU_PROMPT = """-- Менюшечка --

1) Создать новый опрос
2) Список текущих опросов
3) Проголосовать
4) Показать результаты опроса
5) Выбрать произвольного победителя из проголосовавших
6) Выход

Ваш выбор: """
NEW_OPTION_PROMPT = "Введите новый выбор (или оставьте поле пустым, если закончили): "


def prompt_create_poll(connection):
    poll_title = input("Введите название опроса: ")
    poll_owner = input("Введите имя создателя  опроса: ")
    options = []

    while new_option := input(NEW_OPTION_PROMPT):
        options.append(new_option)

    database.create_poll(connection, poll_title, poll_owner, options)


def list_open_polls(connection):
    polls = database.get_polls(connection)

    for _id, title, owner in polls:
        print(f"{_id}: {title} (создано пользователем {owner})")


def prompt_vote_poll(connection):
    poll_id = int(input("Введите номер опроса, где хотели бы проголосовать: "))

    poll_options = database.get_poll_details(connection, poll_id)
    _print_poll_options(poll_options)

    option_id = int(input("Выберете интересующий Вас пункт: "))
    username = input("Введите свой ник: ")
    database.add_poll_vote(connection, username, option_id)


def _print_poll_options(poll_with_options: list[database.PollWithOption]):
    for option in poll_with_options:
        print(f"{option[3]}: {option[4]}")


def show_poll_votes(connection):
    poll_id = int(input("Какой опрос хотите посмотреть?: "))
    try:
        # This gives us count and percentage of votes for each option in a poll
        poll_and_votes = database.get_poll_and_vote_results(connection, poll_id)
    except DivisionByZero:
        print("В нем ещё нет голосов.")
    else:
        for _id, option_text, count, percentage in poll_and_votes:
            print(f"Пункт {option_text} получил {count} голосов ({percentage:.1f}% от общего числа)")


def randomize_poll_winner(connection):
    poll_id = int(input("Введите название опроса, где хотите выбрать победителя: "))
    poll_options = database.get_poll_details(connection, poll_id)
    _print_poll_options(poll_options)

    option_id = int(input("""Введите номер выигрышного ответа, 
                         победитель будет выбран из проголосавших за этот вариант: """))
    winner = database.get_random_poll_vote(connection, option_id)
    print(f"Произвольно выбранный победитель: {winner[0]}.")


MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_polls,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randomize_poll_winner
}


def menu():
    database_uri = input(DATABASE_PROMPT)
    if not database_uri:
        load_dotenv()
        database_uri = os.environ["DATABASE_URI"]

    connection = psycopg2.connect(database_uri)
    database.create_tables(connection)

    while (selection := input(MENU_PROMPT)) != "6":
        try:
            MENU_OPTIONS[selection](connection)
        except KeyError:
            print("Выбрана несуществующая опция, попробуйте еще раз!")


menu()