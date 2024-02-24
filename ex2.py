#!/usr/bin/env python3

import re


def make_stat(filename):
    """
        Функция вычисляет статистику по именам за каждый год с учётом пола.
        """
    stat = {}
    with open(filename, encoding='cp1251') as f:
        for line in f:
            year_match = re.search(r"<h3>(\d{4})", line)
            if year_match:
                year = line[-20:-16]
            name_match = re.search(r"<a href.*?>", line)
            if name_match:
                name = line.split(">")[5].split(' ')[1][:-3]
                if name not in stat:
                    gender = identify_gender(name)
                    stat[name] = [gender, year]
                else:
                    stat[name].append(year)
    return stat


def extract_years(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список годов,
    упорядоченный по возрастанию.
    """
    years_set = set()
    for name in stat:
        info = stat[name]
        for i in range(1, len(info)):
            years_set.add(info[i])
    years_list = sorted(years_set)
    return years_list


def extract_general(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для всех имён.
    Список должен быть отсортирован по убыванию количества.
    """
    general_list = [(name, len(data) - 1) for name, data in stat.items()]
    general_list.sort(key=lambda x: x[1], reverse=True)
    return general_list


def extract_general_male(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён мальчиков.
    Список должен быть отсортирован по убыванию количества.
    """
    general_male_list = []
    for name, data in stat.items():
        if re.search(r'^male', data[0]):
            general_male_list.append((name, len(data) - 1))
    general_male_list.sort(key=lambda x: x[1], reverse=True)
    return general_male_list


def extract_general_female(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён девочек.
    Список должен быть отсортирован по убыванию количества.
    """
    general_female_list = []
    for name, data in stat.items():
        if re.search(r'^female', data[0]):
            general_female_list.append((name, len(data) - 1))
    general_female_list.sort(key=lambda x: x[1], reverse=True)
    return general_female_list


def extract_year(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    general_year_list = []
    for name in stat:
        data = stat[name]
        if year in data:
            general_year_list.append((name, data.count(year)))
    general_year_list.sort(key=lambda x: x[1], reverse=True)
    return general_year_list


def extract_year_male(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён мальчиков в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    male_year_list = []
    for name, data in stat.items():
        if re.search(r'^male', data[0]) and year in data:
            male_year_list.append((name, data.count(year)))
    male_year_list.sort(key=lambda x: x[1], reverse=True)
    return male_year_list


def extract_year_female(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён девочек в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    female_year_list = []
    for name, data in stat.items():
        if re.search(r'^female', data[0]) and year in data:
            female_year_list.append((name, data.count(year)))
    female_year_list.sort(key=lambda x: x[1], reverse=True)
    return female_year_list


def identify_gender(name):
    if (re.search(r'[аья]$', name) and
            not (re.search(r"Илья", name)
                 or re.search(r"Игорь", name)
                 or re.search(r"Никита", name)
                 or re.search(r"Лёва", name))):
        return "female"
    return "male"


if __name__ == '__main__':
    start = make_stat("home.html")
