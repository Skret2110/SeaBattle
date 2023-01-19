from random import randint
from colorama import Fore, Style
name_player = input("Введите имя игрока!")


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return Fore.RED + "Вы выстрелили за пределы доски!" + Style.RESET_ALL


class BoardUsedException(BoardException):
    def __str__(self):
        return Fore.RED + "Вы уже стреляли в это место!" + Style.RESET_ALL


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, n, o):
        self.bow = bow
        self.n = n
        self.o = o
        self.lives = n

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.n):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = Fore.RED + "." + Style.RESET_ALL
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "0")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = Fore.RED + "X" + Style.RESET_ALL
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print(Fore.MAGENTA + f"Корабль уничтожен! "
                                         f"Все погибли!" + Style.RESET_ALL)
                    return True
                else:
                    print(Fore.LIGHTBLUE_EX + f"Сосредоточься, "
                                              f"корабль ранен!" + Style.RESET_ALL)
                    return True

        self.field[d.x][d.y] = Fore.RED + "T" + Style.RESET_ALL
        print(Fore.LIGHTCYAN_EX + "Мимо! Мазила!!!" + Style.RESET_ALL)
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(Fore.YELLOW + f"Ход ИИ: {d.x + 1} {d.y + 1}" + Style.RESET_ALL)
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input(Fore.BLUE + "Ваш ход: " + Style.RESET_ALL).split()

            if len(cords) != 2:
                print(Fore.RED + " Введите 2 координаты! " + Style.RESET_ALL)
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(Fore.RED + " Введите числа! " + Style.RESET_ALL)
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for n in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), n, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @staticmethod
    def gret():
        print(Fore.LIGHTCYAN_EX + "-" * 20)
        print("Приветсвую Вас")
        print("    в игре    ")
        print("  морской бой ")
        print("-" * 20)
        print("формат ввода: х у")
        print(" х - номер строки")
        print("у - номер столбца")
        print("-" * 20 + Style.RESET_ALL)

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print(Fore.BLUE + f"Доска {name_player}!" + Style.RESET_ALL)
            print(self.us.board)
            print("-" * 28)
            print(Fore.YELLOW + "Доска ИИ!" + Style.RESET_ALL)
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 28)
                print(Fore.BLUE + f"Ходит {name_player}!" + Style.RESET_ALL)
                repeat = self.us.move()
            else:
                print("-" * 28)
                print(Fore.YELLOW + "Ходит ИИ!" + Style.RESET_ALL)
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 28)
                print(Fore.MAGENTA + f"Выиграл {name_player} и  спас человечество!" + Style.RESET_ALL)
                break

            if self.us.board.count == 7:
                print("-" * 28)
                print(Fore.RED + "Выиграл ИИ, мы все обреченны!" + Style.RESET_ALL)
                break
            num += 1

    def start(self):
        self.gret()
        self.loop()


g = Game()
g.start()
