import csv
import os
import random
import sqlite3

from Emitters import *


class Crossword:
    def __init__(self, words_data: list[dict]):
        self.words_data: list[dict] = words_data
        self.is_visible = True
        self.is_vertical = True
        pass


def generate_crossword(error_signals: dict[str, AbstractEmitter], keyword: str, difficulty: int):
    conn = sqlite3.connect("bank.db")
    cur = conn.cursor()

    if keyword == "":
        keyword = \
            cur.execute(
                """SELECT word FROM Words WHERE difficulty = ? ORDER BY RANDOM() LIMIT 1""",
                (difficulty,)).fetchall()[0][0]
    else:
        result = cur.execute("""SELECT DISTINCT word FROM Words WHERE word = ?""",
                             (keyword.capitalize(),)).fetchall()
        if not result:
            error_signals["keyword not found"].signal.emit(keyword)
            conn.commit()
            conn.close()
            return Crossword([])
    keyword = keyword.lower()

    crossword = Crossword([])
    matches = {}
    used_words = set()
    used_words.add(keyword)
    for key_char in keyword:
        if key_char not in matches.keys():
            matches[key_char] = cur.execute(
                """SELECT word, description FROM words WHERE (word
                   LIKE ? OR word LIKE ?) AND difficulty = ? AND word <> ?""",
                (f"%{key_char}%", f"%{key_char.upper()}%", difficulty, keyword.capitalize(),)).fetchall()

        word_info: tuple[str, str] = (keyword, "")
        while word_info[0].lower() in used_words and len(matches[key_char]) != 0:
            random.shuffle(matches[key_char])
            word_info: tuple[str, str] = matches[key_char].pop(0)
        if len(matches[key_char]) == 0:
            error_signals["words are over"].signal.emit(key_char)
            return Crossword([])
        else:
            used_words.add(word_info[0].lower())

        crossword.words_data.append({"word": word_info[0].lower(),
                                     "description": word_info[1].lower(),
                                     "match position": random.choice([i for i in range(0, len(word_info[0])) if
                                                                      word_info[0][
                                                                          i].lower() == key_char.lower()])})

    conn.commit()
    conn.close()
    return crossword


def load_crossword(error_signals: dict[str, AbstractEmitter], path: str):
    try:
        with open(path, mode="r", encoding="utf-8") as crossword_file:
            filename, file_extension = os.path.splitext(path)
            if file_extension != ".csv":
                error_signals["wrong extension"].signal.emit(file_extension)
                return []
            raw_crossword_data = csv.reader(crossword_file, delimiter=';', quotechar=' ')
            i = 0
            word = 0
            description = 1
            keyword = ""
            words_data = []
            for row in raw_crossword_data:
                match i:
                    case 0:
                        if not ((row == ["﻿word", "description", "match position"] and len(
                                list(row)) == 3)):
                            error_signals["corrupted file"].signal.emit(tuple())
                            return []
                    case 1:
                        keyword = row[word].lower()
                        print(keyword)
                    case _:
                        match_pos = int(row[-1]) - 1
                        row[word] = row[word].lower()
                        if row[word][match_pos] != keyword.lower()[i - 2]:
                            error_signals["corrupted file"].signal.emit((keyword, row[word], match_pos, i - 2))
                            return Crossword([])
                        words_data.append({"word": row[word],
                                           "description": row[description],
                                           "match position": match_pos})
                i += 1
            return words_data
    except FileNotFoundError:
        error_signals["file not found"].signal.emit(path)
        return


def save_crossword_table(error_signals: dict[str, AbstractEmitter], filepath: str, crossword: Crossword):
    try:
        with open(filepath, mode="w", encoding="utf-8", newline="") as csvfile:
            crossword_writer = csv.writer(csvfile, delimiter=';')
            keyword = "".join([crossword.words_data[i]["word"][crossword.words_data[i]["match position"]] for i in
                               range(0, len(crossword.words_data))])
            crossword_writer.writerow(("﻿word", "description", "match position"))
            crossword_writer.writerow((keyword, "NULL", "NULL"))
            for i in range(0, len(crossword.words_data)):
                crossword_writer.writerow((crossword.words_data[i]["word"], crossword.words_data[i]["description"],
                                           str(crossword.words_data[i]["match position"] + 1)))
    except IOError:
        error_signals["directory not found"].signal.emit(filepath[:filepath.rindex("/")])
    except IndexError:
        return


def find_sub_dict(original_dict: dict, required_keys: tuple) -> dict:
    return {key: original_dict[key] for key in required_keys if key in original_dict.keys()}
