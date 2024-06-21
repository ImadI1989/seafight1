# ✸✸✸ Морской бой ✸✸✸

from random import randint


class BoardException(Exception):
    pass
# Исключение, находится ли точка выстрела за пределами поля
class BoardOutException(BoardException):
    pass
# Исключение, был ли уже сделан выстрел по этой точке
class BoardUsedException(BoardException):
    pass

# Исключение, точка корабля находится вне доски или точка уже занята
class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, orientation):
        self.bow = bow  # Начальная точка корабля (класс Dot)
        self.length = length  # Длина корабля
        self.orientation = orientation  # Ориентация корабля: 0 - горизонтально, 1 - вертикально
        self.lives = length  # Количество "жизней" корабля, равное его длине

    @property
    def dots(self):
        """Генерирует и возвращает список всех точек, которые занимает корабль."""
        ship_dots = []
        for i in range(self.length):
            if self.orientation == 0:
                # Для горизонтальной ориентации увеличиваем x
                cur_dot = Dot(self.bow.x + i, self.bow.y)
            else:
                # Для вертикальной ориентации увеличиваем y
                cur_dot = Dot(self.bow.x, self.bow.y + i)
            ship_dots.append(cur_dot)

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count = 0

        self.field = [["0"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        # Создание заголовка поля с номерами столбцов
        header = "   | " + " | ".join(map(str, range(1, 7))) + " |"
        # Генерация строк поля, включая номера строк и состояние каждой клетки
        rows = [f"{i + 1}  | " + " | ".join(row) + " |" for i, row in enumerate(self.field)]

        # Объединение заголовка и строк поля
        result = header + "\n" + "\n".join(rows)

        # Скрытие символов кораблей
        if self.hide:
            result = result.replace("■", "0")
        return result

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2)]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        # Проверяем, можно ли добавить корабль на доску
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                # Если точка корабля находится вне доски или точка уже занята
                raise BoardWrongShipException("Невозможно разместить корабль в этом месте!")

        # Если все точки корабля валидны, добавляем корабль на доску
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"  # Отмечаем точки корабля на доске
            self.busy.append(dot)  # Добавляем точки корабля в список занятых точек

        self.ships.append(ship)  # Добавляем корабль в список кораблей на доске
        self.contour(ship)  # Создаем контур вокруг корабля

    def shot(self, dot):
        # Проверяем, находится ли точка выстрела за пределами поля
        if self.out(dot):
            raise BoardOutException("Выстрел за пределы доски!")

        # Проверяем, был ли уже сделан выстрел по этой точке
        if dot in self.busy:
            raise BoardUsedException("По этой точке уже стреляли!")

        # Отмечаем точку выстрела как занятую
        self.busy.append(dot)

        # Проверяем, попал ли выстрел по какому-нибудь кораблю
        for ship in self.ships:
            if ship.shooten(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"  # Отмечаем попадание на доске
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)  # Обозначаем контур уничтоженного корабля
                    print("Корабль уничтожен!")
                    return False  # Возвращаем False, так как ход передаётся другому игроку
                else:
                    print("Корабль повреждён!")
                    return True  # Возвращаем True, игрок продолжает стрелять

        # Если выстрел не попал по кораблю, отмечаем промах
        self.field[dot.x][dot.y] = "T"
        print("Промах!")
        return False  # Ход передаётся другому игроку

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask() # Запрос координат для выстрела
                repeat = self.enemy.shot(target)  # Выстрел по полученным координатам
                return repeat
            except BoardException as e: # Перехват исключений согласно правилам игры
                print(e)
                continue

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hide = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

# Игра генерирует случайную доску для игры
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("""
    ------------------------
        Добро пожаловать
        в игру SeaFight
    ------------------------
        формат ввода для 
         выстрела: x y
        x - номер строки
        y - номер столбца
    ------------------------
        условные обозначения:
        "■"- вид коробля на поле
        "T" - промах
        "X" - попадание снарядом
    """)

    def print_boards(self):
        print("-" * 30)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 30)
        print("Доска компьютера:")
        print(self.ai.board)
        print("-" * 30)

    def loop(self):
        num = 0
        while True:
            self.print_boards()

            if num % 2 == 0:
                print("\033[92m Ходит пользователь!\033[0m")  # Зеленый цвет
                repeat = self.us.move()
            else:
                print("\033[93m Ходит компьютер!\033[0m")  # Желтый цвет
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("-" * 30)
                print("\033[96m✸✸✸ Пользователь выиграл! ✸✸✸\033[0m")  # Циановый цвет
                break

            if self.us.board.defeat():
                self.print_boards()
                print("-" * 30)
                print("\033[91m✸✸✸ Компьютер выиграл! ✸✸✸\033[0m")  # Красный цвет
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
