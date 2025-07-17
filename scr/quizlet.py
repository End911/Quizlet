import sqlite3
import string
from random import choice
from deep_translator import GoogleTranslator
import os
from colorama import init, Fore
from tabulate import tabulate
from abc import ABC, abstractmethod

init()

class Quizlet(ABC):
    """Standart class for realization new quizlet trainers"""
    def __init__(self):
        _script_dir = os.path.dirname(__file__)
        self.path_to_db = os.path.join(_script_dir, "quizlet_db.db")
        with sqlite3.connect(self.path_to_db): pass

    def menu(self):
        """The start game menu"""
        choose_action = input(f"{Fore.WHITE}{f" {Fore.YELLOW}{self._app_name}{Fore.WHITE} ":=^75}"
                          f"\nВыберите действие:"
                          f"\n1)Добавить слово в каталог"
                          f"\n2)Редактировать каталог"
                          f"\n3)Начать игру\n")
        while True:
            match choose_action:
                case "1":
                    self._add_word_to_db()
                case "2":
                    self._edit_catalog_menu()
                case "3":
                    self._game_menu()
                case choose_action:
                    choose_action = input(f"{Fore.RED}Ошибка, неверная команда, попробуйте снова\n{Fore.WHITE}")
                    continue

    def _print_score_and_goto_menu(self, true: int, false: int):
        print(f"{Fore.YELLOW}КОНЕЦ ИГРЫ{Fore.WHITE}"
              f"\nПравильных ответов: {Fore.GREEN}{true}{Fore.RESET}"
              f"\nНеправильных ответов: {Fore.RED}{false}{Fore.WHITE}")
        return self.menu()

    @abstractmethod
    def _edit_catalog_menu(self):
        pass
            
    @abstractmethod
    def _add_word_to_db(self):
        pass

    @abstractmethod
    def _get_id(self):
        pass

    @abstractmethod
    def _reorder_ids():
        pass
    
    @abstractmethod
    def _check_id(self):
        pass

    @abstractmethod
    def _game_menu(self):
        pass

    @abstractmethod
    def _first_game(self):
        pass

    @abstractmethod
    def _second_game(self):
        pass

    @abstractmethod
    def _third_game(self):
        pass

    @abstractmethod
    def _register_qty_games(self):
        pass

    def _check_user_answer(self, question: str, real_anser: str) -> bool:
        user_answer = input(f"{Fore.WHITE}Введите перевод {question}: ")
        if user_answer.lower() == real_anser:
            print(f"{Fore.GREEN}Правильно!{Fore.WHITE}")
            return True
        else:
            print(f"{Fore.RED}Неверно, правильный перевод: {Fore.YELLOW}{real_anser}{Fore.RED}{Fore.WHITE}")
            return False

class EnglishRussianTrainer(Quizlet):
    def __init__(self):
        super().__init__()
        self._translator_to_ru = GoogleTranslator(source="en", target="ru")
        self._translator_to_en = GoogleTranslator(source="ru", target="en")
        self._app_name = "ENGLISH & RUSSIAN TRAINER"
        with sqlite3.connect(self.path_to_db) as conn:
            conn.executescript("""CREATE TABLE IF NOT EXISTS russian_words (
                         id INTEGER PRIMARY KEY,
                         word TEXT NOT NULL);
                         CREATE TABLE IF NOT EXISTS english_words (
                         id INTEGER PRIMARY KEY,
                         word TEXT NOT NULL);
                        """)

    def _add_word_to_db(self):
        RU_WORDS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        ru_word = input("Введите слово на русском:\n")
        stop_flag = True
        while stop_flag:
            if ru_word == "":
                ru_word = input(f"{Fore.RED}Ошибка, слово не может быть пустым, попробуйте заново{Fore.WHITE}\n")
                continue
            for word in ru_word.lower():
                if word not in RU_WORDS:
                    ru_word = input(f"{Fore.RED}Ошибка, слово должно быть написано только русскими буквами, попробуйте заново{Fore.WHITE}\n")
                    stop_flag = False
                    break
            if not stop_flag:
                stop_flag = True
                continue
            en_word = self._translator_to_en.translate(ru_word)
            with sqlite3.connect(self.path_to_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT word FROM english_words")
                en_rows = cursor.fetchall()
                en_rows = [item for row in en_rows for item in row]
                cursor.execute("SELECT word FROM russian_words")
                ru_rows = cursor.fetchall()
                ru_rows = [item for row in ru_rows for item in row]
                if ru_word in ru_rows:
                    ru_word = input(f"{Fore.RED}Ошибка, слово с идентичным {Fore.YELLOW + "русским" + Fore.RED} переводом уже есть в каталоге, попробуйте заново{Fore.WHITE}\n")                    
                if en_word in en_rows:
                    ru_word = input(f"{Fore.RED}Ошибка, слово с идентичным {Fore.YELLOW + "английским" + Fore.RED} переводом уже есть в каталоге, попробуйте заново{Fore.WHITE}\n")                    
                    continue
                cursor.execute("INSERT INTO english_words (word) VALUES (?)", (en_word.lower(),))
                cursor.execute("INSERT INTO russian_words (word) VALUES (?)", (ru_word.lower(),))
                conn.commit()
            print(f"{Fore.GREEN}Слово успешно добавлено в каталог!{Fore.WHITE}")
            return self.menu()

    def _edit_catalog_menu(self):
        with sqlite3.connect(self.path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT en.id, en.word, ru.word
                            FROM english_words en
                            JOIN russian_words ru ON ru.id = en.id""")
            print(f"{"":=^75}")
            print(tabulate(cursor.fetchall(), headers=[
                "ID", "English", "Russian"], tablefmt="mixed_grid"))
            choose_action = input(f"\n{Fore.YELLOW}Выберите действие{Fore.WHITE}:"
                                    f"\n1)Удалить слово"
                                    f"\n2)Изменить перевод слова"
                                    f"\n3)Выйти в меню\n")
            stop_flag = True
            while stop_flag:
                match choose_action:
                    case "1":
                        word_id = input(f"{Fore.WHITE}Укажите айди слова: ")
                        word_id = self._check_id(word_id)                            
                        cursor.execute("DELETE FROM russian_words WHERE id = ?", (word_id,))
                        cursor.execute("DELETE FROM english_words WHERE id = ?", (word_id,))
                        print(f"{Fore.GREEN}Слово с айди {word_id} удалено!{Fore.WHITE}")
                        conn.commit()
                        self._reorder_ids()
                        return self._edit_catalog_menu()
                    case "2":
                        word_id = input(f"{Fore.WHITE}Укажите айди слова: ")
                        word_id = self._check_id(word_id)
                        user_en_word = input(f"Напишите перевод слова с айди {word_id} на английском языке\n")
                        stop_flag = True
                        while stop_flag:
                            if user_en_word == "":
                                user_en_word = input(f"{Fore.RED}Ошибка, слово не может быть пустым, попробуйте заново{Fore.WHITE}\n")
                                continue
                            for word in user_en_word.lower():
                                if word not in string.ascii_letters:
                                    user_en_word = input(f"{Fore.RED}Ошибка, слово должно быть написано только {Fore.YELLOW + "английскими" + Fore.RED} буквами, попробуйте заново{Fore.WHITE}\n")
                                    stop_flag = False
                                    break
                            if not stop_flag:
                                stop_flag = True
                                continue
                            cursor.execute("SELECT word FROM english_words")
                            en_rows = cursor.fetchall()
                            en_rows = [item for row in en_rows for item in row]
                            if user_en_word in en_rows:
                                user_en_word = input(f"{Fore.RED}Ошибка, слово с идентичным {Fore.YELLOW + "английским" + Fore.RED} переводом уже есть в каталоге, попробуйте заново{Fore.WHITE}\n")                    
                                continue
                            cursor.execute("UPDATE english_words SET word = ? WHERE id = ?", (user_en_word, word_id))
                            conn.commit()
                            print(f"{Fore.GREEN}Слово с айди {word_id} было переименовано{Fore.WHITE}")
                            return self._edit_catalog_menu()
                    case "3":
                        return self.menu()
                    case choose_action:
                        choose_action = input(f"{Fore.RED}Ошибка, неверная команда, попробуйте снова\n{Fore.WHITE}")
                        continue

    def _reorder_ids(self):
        with sqlite3.connect(self.path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT word FROM english_words ORDER BY id")
            en_rows = cursor.fetchall()
            cursor.execute("DELETE FROM english_words")
            cursor.executemany("INSERT INTO english_words (word) VALUES (?)", en_rows)
            cursor.execute("SELECT word FROM russian_words ORDER BY id")
            ru_rows = cursor.fetchall()
            cursor.execute("DELETE FROM russian_words")
            cursor.executemany("INSERT INTO russian_words (word) VALUES (?)", ru_rows)
            conn.commit()

    def _get_id(self):
        with sqlite3.connect(self.path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM russian_words")
            rows = cursor.fetchall()
            return [str(item) for sublist in rows for item in sublist]

    def _check_id(self, id):
        while True:
            ids = self._get_id()
            if id not in ids:
                id = input(f"{Fore.RED}Ошибка, неверный айди, попробуйте заново: {Fore.WHITE}")
                continue
            return id

    def _game_menu(self):
        choose_action = input(f"{Fore.WHITE}{f"{Fore.YELLOW} GAME MENU {Fore.WHITE} ":=^75}"
                          f"\nВыберите режим:"
                          f"\n1)Перевод английских слов"
                          f"\n2)Перевод русских слов"
                          f"\n3)Перевод рандомных слов"
                          f"\n4)Выйти в меню\n")
        while True:
            match choose_action:
                case "1":
                    self._first_game()
                case "2":
                    self._second_game()
                case "3":
                    self._third_game()
                case "4":
                    self.menu()
                case choose_action:
                    choose_action = input(f"{Fore.RED}Ошибка, неверная команда, попробуйте снова\n{Fore.WHITE}")
                    continue
    # ПОДУМАТЬ НАД ОБЩЕЙ ЛОГИКОЙ 3 ИГР
    def _first_game(self):
        """In this game you need to write translations of english words into russian"""
        qty_games = self._register_qty_games()        
        count_true = 0
        count_false = 0
        for _ in range(1, qty_games + 1):
            en_word, ru_word = self.__get_random_en_ru_words()
            match self._check_user_answer(en_word, ru_word):
                case True:
                    count_true += 1
                case False:
                    count_false += 1
        self._print_score_and_goto_menu(count_true, count_false)

    def _second_game(self):
        """In this game you need to write translations of russian words into english"""
        qty_games = self._register_qty_games()        
        count_true = 0
        count_false = 0
        for _ in range(1, qty_games + 1):
            en_word, ru_word = self.__get_random_en_ru_words()
            match self._check_user_answer(ru_word, en_word):
                case True:
                    count_true += 1
                case False:
                    count_false += 1
        self._print_score_and_goto_menu(count_true, count_false)

    def _third_game(self):
        """In this game you need to write translations of random words into the desired language"""
        qty_games = self._register_qty_games()        
        count_true = 0
        count_false = 0
        for _ in range(1, qty_games + 1):
            en_word, ru_word = self.__get_random_en_ru_words()
            random_choice = choice(["en", "ru"])
            match random_choice:
                case "en":
                    user_word = input(f"{Fore.WHITE}Введите перевод {ru_word}: ")
                    if user_word.lower() == en_word:
                        print(f"{Fore.GREEN}Правильно!{Fore.WHITE}")
                        count_true += 1
                    else:
                        print(f"{Fore.RED}Неверно, правильный перевод: {Fore.YELLOW + f"{en_word}" + Fore.RED}{Fore.WHITE}")
                        count_false += 1
                case "ru":
                    user_word = input(f"{Fore.WHITE}Введите перевод {en_word}: ")
                    if user_word.lower() == ru_word:
                        print(f"{Fore.GREEN}Правильно!{Fore.WHITE}")
                        count_true += 1
                    else:
                        print(f"{Fore.RED}Неверно, правильный перевод: {Fore.YELLOW + f"{ru_word}" + Fore.RED}{Fore.WHITE}")
                        count_false += 1
        self._print_score_and_goto_menu(count_true, count_false)

    def _register_qty_games(self):
        qty_games = input(f"{Fore.WHITE}Введите количество раундов: ")
        if qty_games == "" or qty_games == "0":
            print(f"{Fore.RED}Ошибка, вы должны ввести корректное количество раундов, попробуйте заново")
            return self._register_qty_games()
        for word in qty_games:
            if word not in string.digits:
                print(f"{Fore.RED}Ошибка, вы должны ввести корректное количество раундов, попробуйте заново")
                return self._register_qty_games()
        return int(qty_games)

    def __get_random_en_ru_words(self):
        """Special method for this class"""
        with sqlite3.connect(self.path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM english_words")
            id = choice(cursor.fetchall())
            cursor.execute("SELECT word FROM english_words WHERE id = ?", id)
            en_word = choice([item for item in cursor.fetchone()])
            cursor.execute("SELECT word FROM russian_words WHERE id = ?", id)
            ru_word = choice([item for item in cursor.fetchone()])
            return en_word, ru_word


if __name__ == "__main__":
    quizlet = EnglishRussianTrainer()
    quizlet.menu()
