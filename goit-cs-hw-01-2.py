class LexicalError(Exception):
    pass


class ParsingError(Exception):
    pass


class TokenType:                                          # Типи токенів для арифметичних операцій і дужок
    INTEGER = "INTEGER"                                   # Додаємо підтримку цілих чисел
    PLUS = "PLUS"                                         # Додаємо підтримку для операції додавання
    MINUS = "MINUS"                                       # Додаємо підтримку для операції віднімання
    MUL = "MUL"                                           # Додаємо підтримку для операції множення
    DIV = "DIV"                                           # Додаємо підтримку для операції ділення
    LPAREN = "LPAREN"                                     # Додаємо підтримку відкритої дужки
    RPAREN = "RPAREN"                                     # Додаємо підтримку закритої дужки
    EOF = "EOF"                                           # Додаємо підтримку кінця введеного виразу


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {repr(self.value)})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):                                                          # Метод для зчитування цілих чисел
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):                                                   # Метод для отримання наступного токену
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())

            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS, "+")

            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS, "-")

            if self.current_char == "*":
                self.advance()
                return Token(TokenType.MUL, "*")

            if self.current_char == "/":
                self.advance()
                return Token(TokenType.DIV, "/")

            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN, "(")

            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN, ")")

            raise LexicalError("Lexical error")

        return Token(TokenType.EOF, None)


class AST:
    pass


class BinOp(AST):
    # Вузол для бінарних операцій (додавання, віднімання, множення, ділення)
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise ParsingError("Lexical error")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):                                        # Обробка чисел або виразів у дужках
        token = self.current_token
        if token.type == TokenType.INTEGER:                  # Якщо це ціле число
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.LPAREN:                 # Якщо це відкрита дужка, "з'їдаємо" її та обчислюємо вираз у дужках
            self.eat(TokenType.LPAREN)
            node = self.expr()                               # Рекурсивно обчислюємо вираз у дужках
            self.eat(TokenType.RPAREN)                       # "З'їдаємо" закриту дужку
            return node
        else:
            self.error()

    def term(self):                                          # Обробка множення та ділення
        node = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:                  # Якщо це операція множення
                self.eat(TokenType.MUL)                      # "з'їдаємо" цей знак *
            elif token.type == TokenType.DIV:                # Якщо це операція ділення
                self.eat(TokenType.DIV)                      # "з'їдаємо" цей знак /

            node = BinOp(left=node, op=token, right=self.factor()) # Створюємо вузол для множення або ділення

        return node

    def expr(self):                                         # Обробка операцій додавання та віднімання
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:                # Якщо це операція додавання
                self.eat(TokenType.PLUS)                    # "з'їдаємо" цей знак +
            elif token.type == TokenType.MINUS:             # Якщо це операція віднімання
                self.eat(TokenType.MINUS)                   # "з'їдаємо" цей знак -

            node = BinOp(left=node, op=token, right=self.term())   # Створюємо вузол додавання або віднімання

        return node


def print_ast(node, level=0):                               # Функція для виведення абстрактного синтаксичного дерева
    indent = "  " * level
    if isinstance(node, Num):
        print(f"{indent}Num({node.value})")
    elif isinstance(node, BinOp):
        print(f"{indent}BinOp:")
        print(f"{indent}  left: ")
        print_ast(node.left, level + 2)
        print(f"{indent}  op: {node.op.type}")
        print(f"{indent}  right: ")
        print_ast(node.right, level + 2)
    else:
        print(f"{indent}Unknown node type: {type(node)}")


class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):                                     # Метод для обчислення бінарних операцій
        if node.op.type == TokenType.PLUS:                           # Обчислюємо додавання
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == TokenType.MINUS:                        # Обчислюємо віднімання
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == TokenType.MUL:                          # Обчислюємо множення
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == TokenType.DIV:                          # Обчислюємо ділення, перевіряючи на поділ на нуль
            try:
                return self.visit(node.left) / self.visit(node.right)
            except ZeroDivisionError:                                # Виключаємо помилку ділення на 0
                raise Exception("Division by zero")

    def visit_Num(self, node):                                       # Повертаємо значення числа
        return node.value

    def interpret(self):                                             # Починаємо обчислення виразу
        tree = self.parser.expr()                                    # Створюємо абстрактне синтаксичне дерево (AST)
        return self.visit(tree)                                      # Відвідуємо корінь дерева для обчислення

    def visit(self, node):                                           # Визначаємо правильний метод для обчислення вузла
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):                                   # Якщо немає відповідного методу для відвідування вузла, "райзимо" помилку
        raise Exception(f"There is no method: visit_{type(node).__name__}")


def main():
    while True:
        try:
            text = input('Введіть вираз (або "exit" для виходу): ')
            if text.lower() == "exit":
                print("До нових зустрічей.")
                break
            lexer = Lexer(text)                                     # Лексичний аналізатор
            parser = Parser(lexer)                                  # Парсер для побудови синтаксичного дерева
            interpreter = Interpreter(parser)                       # Інтерпретатор для обчислення виразу
            result = interpreter.interpret()                        # Обчислюємо результат
            print(result)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()