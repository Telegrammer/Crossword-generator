import csv
import os

from Emitters import *


class Crossword:
    def __init__(self, words_data: list[dict]):
        self.__keyword_matches: list[dict] = []
        pass


class CrosswordGenerator:
    def __init__(self, data: tuple[str]):
        self.keyWord = data[0]
        self.difficulty = data[1]
        pass

    def generate(self) -> Crossword:
        return Crossword([{"word": "Труба", "description": "Описание трубы"}])


def load_crossword(error_signals: dict[str, AbstractEmitter], path: str):
    try:
        with open(path, mode="r", encoding="utf-8") as crossword_file:
            filename, file_extension = os.path.splitext(path)
            if file_extension != ".csv":
                error_signals["wrong extension"].signal.emit(file_extension)
                return
            raw_crossword_data = csv.reader(crossword_file, delimiter=',', quotechar=' ')
            i = 0
            word = 0
            description = 1
            keyword = ""
            words_data = []
            for row in raw_crossword_data:
                match i:
                    case 0:
                        if not ((row[0] == "﻿word" and row[1] == "description" and row[2] == "match position" and len(
                                list(row)) == 3)):
                            error_signals["corrupted file"].signal.emit(tuple())
                            return
                    case 1:
                        keyword = row[word].lower()
                        print(keyword)
                    case _:
                        match_pos = int(row[2]) - 1
                        row[word] = row[word].lower()
                        if row[word][match_pos] != keyword.lower()[i - 2]:
                            error_signals["corrupted file"].signal.emit((keyword, row[word], match_pos))
                            return
                        words_data.append({"word": row[word],
                                           "description": row[description],
                                           "match position": match_pos})
                i += 1
            return words_data
    except FileNotFoundError:
        error_signals["file not found"].signal.emit(path)
        return


def find_sub_dict(original_dict: dict, required_keys: tuple) -> dict:
    return {key: original_dict[key] for key in required_keys if key in original_dict.keys()}
