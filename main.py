import re
import math

def tokenize(text):
    tokens = re.findall(r'\d+\.\d+|\d+|[<()*/+-]|sqrt', text)
    if ''.join(tokens) != ''.join(text.split()):
        raise ValueError("недопустимый символ в выражении")
    return tokens

def parse_factor(tokens, pos):
    if pos >= len(tokens):
        raise ValueError("неожиданный конец выражения")
    token = tokens[pos]

    if token == '-':
        operand, pos = parse_factor(tokens, pos + 1)
        return ('-', 0.0, operand), pos

    if token == '+':
        return parse_factor(tokens, pos + 1)

    if token == '(':
        pos += 1
        tree, pos = parse_comparison(tokens, pos)
        if pos >= len(tokens) or tokens[pos] != ')':
            raise ValueError("не закрыта скобка")
        return tree, pos + 1

    if token == 'sqrt':
        pos += 1
        if pos >= len(tokens) or tokens[pos] != '(':
            raise ValueError("после sqrt нужна открывающая скобка")
        pos += 1
        arg, pos = parse_comparison(tokens, pos)
        if pos >= len(tokens) or tokens[pos] != ')':
            raise ValueError("не закрыта скобка")
        return ('sqrt', arg), pos + 1

    try:
        return float(token), pos + 1
    except ValueError:
        raise ValueError(f"неожиданный символ '{token}'")

def parse_term(tokens, pos):
    left, pos = parse_factor(tokens, pos)
    while pos < len(tokens) and tokens[pos] in ('*', '/'):
        operator = tokens[pos]
        right, pos = parse_factor(tokens, pos + 1)
        left = (operator, left, right)
    return left, pos

def parse_expr(tokens, pos):
    left, pos = parse_term(tokens, pos)
    while pos < len(tokens) and tokens[pos] in ('+', '-'):
        operator = tokens[pos]
        right, pos = parse_term(tokens, pos + 1)
        left = (operator, left, right)
    return left, pos

def parse_comparison(tokens, pos):
    left, pos = parse_expr(tokens, pos)
    while pos < len(tokens) and tokens[pos] == '<':
        operator = tokens[pos]
        right, pos = parse_expr(tokens, pos + 1)
        left = (operator, left, right)
    return left, pos

def evaluate(tree):
    if isinstance(tree, float):
        return tree
    if tree[0] == 'sqrt':
        value = evaluate(tree[1])
        if value < 0:
            raise ValueError("корень из отрицательного числа")
        return math.sqrt(value)
    operator, left, right = tree
    a = evaluate(left)
    b = evaluate(right)
    if operator == '+':
        return a + b
    elif operator == '-':
        return a - b
    elif operator == '*':
        return a * b
    elif operator == '/':
        return a / b
    elif operator == '<':
        return 1 if a < b else 0

if __name__ == '__main__':
    expression = input("Введите выражение: ")
    try:
        tokens = tokenize(expression)
        tree, pos = parse_comparison(tokens, 0)
        if pos < len(tokens):
            raise ValueError("неправильное выражение")
        print(evaluate(tree))
    except ZeroDivisionError:
        print("Ошибка: деление на ноль")
    except ValueError as error:
        print("Ошибка:", error)