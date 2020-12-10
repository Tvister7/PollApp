import datetime

import pytz

from connection_pool import get_connection
import random
from models.option import Option
from models.poll import Poll
import database

MENU_PROMPT = """-- Менюшечка --

1) Создать новый опрос
2) Список текущих опросов
3) Проголосовать
4) Показать результаты опроса
5) Выбрать произвольного победителя из проголосовавших
6) Выход

Ваш выбор: """
NEW_OPTION_PROMPT = "Введите новый выбор (или оставьте поле пустым, если закончили): "


def prompt_create_poll():
    poll_title = input("Введите название опроса: ")
    poll_owner = input("Введите имя создателя  опроса: ")
    poll = Poll(poll_title, poll_owner)
    poll.save()

    while new_option := input(NEW_OPTION_PROMPT):
        poll.add_option(new_option)


def list_open_polls():
    for poll in Poll.all():
        print(f"{poll.id}: {poll.title} (создано пользователем {poll.owner})")


def prompt_vote_poll():
    poll_id = int(input("Введите номер опроса, где хотели бы проголосовать: "))
    try:
        _print_poll_options(Poll.get(poll_id).options)

        option_id = int(input("Выберете интересующий Вас пункт: "))
        username = input("Введите свой ник: ")

        Option.get(option_id).vote(username)
    except TypeError:
        print("Нет опроса под этим номером!")


def _print_poll_options(options: list[Option]):
    for option in options:
        print(f"{option.id}: {option.text}")


def show_poll_votes():
    poll_id = int(input("Какой опрос хотите посмотреть?: "))
    try:
        options = Poll.get(poll_id).options
        votes_per_option = [len(option.votes) for option in options]
        total_votes = sum(votes_per_option)
        try:
            for option, votes in zip(options, votes_per_option):
                percentage = votes / total_votes * 100
                if votes % 10 in [2, 3, 4]:
                    print(f"Пункт {option.text} получил {votes} голоса ({percentage:.1f}% от общего числа)")
                elif votes % 10 == 1:
                    print(f"Пункт {option.text} получил {votes} голос ({percentage:.1f}% от общего числа)")
                else:
                    print(f"Пункт {option.text} получил {votes} голосов ({percentage:.1f}% от общего числа)")

        except ZeroDivisionError:
            print("В нем ещё нет голосов.")

        vote_log = input("Хотите увидеть логи? (да/Нет): ")
        if vote_log == "да":
            _print_vote_for_options(options)
    except TypeError:
        print("Нет опроса под этим номером!")


def _print_vote_for_options(options: list[Option]):
    for option in options:
        print(f"-- {option.text} --")
        for vote in option.votes:
            naive_datetime = datetime.datetime.utcfromtimestamp(vote[2])
            utc_date = pytz.utc.localize(naive_datetime)
            local_date = utc_date.astimezone(pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y %H:%M")
            print(f"\t- {vote[0]} в {local_date}")


def randomize_poll_winner():
    poll_id = int(input("Введите номер опроса, где хотите выбрать победителя: "))
    _print_poll_options(Poll.get(poll_id).options)

    option_id = int(input("Введите номер выигрышного ответа, победитель будет выбран из проголосавших за него: "))
    votes = Option.get(option_id).votes
    winner = random.choice(votes)
    print(f"Произвольно выбранный победитель: {winner[0]}.")


MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_polls,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randomize_poll_winner
}


def menu():
    with get_connection() as connection:
        database.create_tables(connection)

        while (selection := input(MENU_PROMPT)) != "6":
            try:
                MENU_OPTIONS[selection]()
            except KeyError:
                print("Выбрана несуществующая опция, попробуйте еще раз!")


menu()
