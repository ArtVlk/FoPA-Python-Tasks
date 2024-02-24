from collections import defaultdict
import argparse


def most_user(file):
    answer = defaultdict(int)
    for line in file:
        current_data = line.split(", ")[0]
        answer[current_data] += 1
    return max(answer, key=answer.get)


def most_resource(file):
    answer = defaultdict(int)
    for line in file:
        content = line.split(", ")[-2]
        answer[content] += 1
    return max(answer, key=answer.get)


def parsing():
    parser = argparse.ArgumentParser(description='Log analyzer')
    parser.add_argument("-f", "--file", help="log file to analyze")
    parser.add_argument("-r", "--resource", default=False, action="store_true",
                        help="most popular resource from data list")
    parser.add_argument("-u", "--user", default=False, action="store_true",
                        help="most active user from data list")
    return parser.parse_args()


def main():
    from sys import exit
    from os import path
    arguments = parsing()
    if not path.exists(arguments.file) or not arguments.file:
        print("Invalid file")
        exit(1)
    if not arguments.resource and not arguments.user:
        print("Provide flags: -u for the most active user or" +
              "-r for most popular resource" +
              " (-h for help)")
        exit(2)
    if arguments.resource:
        with open(arguments.file, encoding="cp1251", errors="ignore") as file:
            print(f"most popular resource -> {most_resource(file)}")
    if arguments.user:
        with open(arguments.file, encoding="cp1251", errors="ignore") as file:
            print(f"most actvie user -> {most_user(file)}")


if __name__ == "__main__":
    main()
