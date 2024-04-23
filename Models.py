class Crossword:
    def __init__(self, words_data: list[dict]):
        self.__keyword_matches: list[dict[str, str]] = []
        pass


class CrosswordGenerator:
    def __init__(self, data: tuple[str]):
        self.keyWord = data[0]
        self.difficulty = data[1]
        pass

    def generate(self) -> Crossword:
        return Crossword([{"word": "Труба", "description": "Описание трубы"}])
