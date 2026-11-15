from decimal import Decimal, ROUND_HALF_UP, getcontext
import sys

getcontext().prec = 34

# Approximate units of each currency per 1 USD. Update these rates as needed.
USD_RATES = {
    "USD": Decimal("1.00"),
    "EUR": Decimal("0.92"),
    "GBP": Decimal("0.79"),
    "JPY": Decimal("150.00"),
    "CAD": Decimal("1.35"),
    "AUD": Decimal("1.52"),
    "INR": Decimal("83.00"),
}


class ExpressionParser:
    def __init__(self, expression):
        self.input = expression
        self.position = 0

    def parse(self):
        value = self.parse_expression()
        self.skip_spaces()
        if self.position != len(self.input):
            raise ValueError("Unexpected character: " + self.input[self.position])
        return value

    def parse_expression(self):
        value = self.parse_term()
        while True:
            self.skip_spaces()
            if self.match("+"):
                value += self.parse_term()
            elif self.match("-"):
                value -= self.parse_term()
            else:
                return value

    def parse_term(self):
        value = self.parse_power()
        while True:
            self.skip_spaces()
            if self.match("*"):
                value *= self.parse_power()
            elif self.match("/"):
                divisor = self.parse_power()
                if divisor == 0:
                    raise ArithmeticError("Division by zero")
                value /= divisor
            elif self.match("%"):
                divisor = self.parse_power()
                if divisor == 0:
                    raise ArithmeticError("Division by zero")
                value %= divisor
            else:
                return value

    def parse_power(self):
        value = self.parse_unary()
        self.skip_spaces()
        if self.match("^"):
            value = value ** self.parse_power()
        return value

    def parse_unary(self):
        self.skip_spaces()
        if self.match("+"):
            return self.parse_unary()
        if self.match("-"):
            return -self.parse_unary()
        if self.match("("):
            value = self.parse_expression()
            self.skip_spaces()
            if not self.match(")"):
                raise ValueError("Missing closing parenthesis")
            return value
        return self.parse_number()

    def parse_number(self):
        self.skip_spaces()
        start = self.position
        has_digit = False
        while self.position < len(self.input) and self.input[self.position].isdigit():
            self.position += 1
            has_digit = True
        if self.position < len(self.input) and self.input[self.position] == ".":
            self.position += 1
            while self.position < len(self.input) and self.input[self.position].isdigit():
                self.position += 1
                has_digit = True
        if not has_digit:
            raise ValueError("Expected a number at position {}".format(self.position))
        return float(self.input[start:self.position])

    def match(self, expected):
        if self.position < len(self.input) and self.input[self.position] == expected:
            self.position += 1
            return True
        return False

    def skip_spaces(self):
        while self.position < len(self.input) and self.input[self.position].isspace():
            self.position += 1


def show_examples():
    print("Calculator examples:")
    print("  (12 + 3) * 2 = {}".format(ExpressionParser("(12 + 3) * 2").parse()))
    print("  Decimal 10 in binary = {}".format(format(10, "b")))
    print("  Binary 1010 in decimal = {}".format(int("1010", 2)))
    ten_euros = Decimal("10") / USD_RATES["EUR"] * USD_RATES["USD"]
    print("  10 EUR in USD = {}".format(ten_euros.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)))
    print("\nCommands (pass a command and its values as arguments):")
    print('  math "(12 + 3) * 2"')
    print("  toBinary 10 | fromBinary 1010")
    print("  currency 10 USD EUR")
    print("Supported currencies: " + ", ".join(USD_RATES))
    print("Currency rates are approximate examples, not live rates.")


def convert_currency(amount_text, from_text, to_text):
    from_currency = from_text.upper()
    to_currency = to_text.upper()
    if from_currency not in USD_RATES or to_currency not in USD_RATES:
        raise ValueError("Unsupported currency. Use: " + ", ".join(USD_RATES))

    amount = Decimal(amount_text)
    converted = amount / USD_RATES[from_currency] * USD_RATES[to_currency]
    rounded = converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    print("{} {} = {} {}".format(
        format(amount.normalize(), "f"), from_currency, format(rounded, "f"), to_currency
    ))


def main(args):
    if not args:
        show_examples()
        return

    command = args[0].lower()
    if command == "math":
        if len(args) < 2:
            raise ValueError('Usage: math <expression>')
        print(ExpressionParser(" ".join(args[1:])).parse())
    elif command in ("binary", "tobinary"):
        if len(args) != 2:
            raise ValueError("Usage: toBinary <decimal integer>")
        print(format(int(args[1]), "b") if int(args[1]) >= 0 else "-" + format(-int(args[1]), "b"))
    elif command in ("decimal", "frombinary"):
        if len(args) != 2:
            raise ValueError("Usage: fromBinary <binary number>")
        print(int(args[1], 2))
    elif command == "currency":
        if len(args) != 4:
            raise ValueError("Usage: currency <amount> <from> <to>")
        convert_currency(args[1], args[2], args[3])
    else:
        raise ValueError("Unknown command: " + args[0])


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as error:
        print("Error: " + str(error))
        print('Examples: math "(12 + 3) * 2", toBinary 10, fromBinary 1010, currency 10 USD EUR')
