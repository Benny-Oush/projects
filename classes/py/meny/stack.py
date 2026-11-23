class Stack:
    def __init__(self):
        self.max_size = 12
        self.data = [None] * self.max_size
        self.idx = -1

    def clear(self):
        if self.idx != -1:
            self.idx = -1

    def push(self, value):
        if self.idx + 1 < self.max_size:
            self.idx += 1
            self.data[self.idx] = value

    def pop(self):
        if not self.is_empty():
            value = self.data[self.idx]
            self.idx -= 1
            return value

    def peek(self):
        if not self.is_empty():
            return self.data[self.idx]

    def peek_all(self):
        return self.data[self.idx :: -1]

    def is_empty(self):
        return self.idx == -1


def check_brackets(equation: str) -> bool:
    brackets_stack = Stack()
    sets = {")": "(", "]": "[", "}": "{"}
    for i, char in enumerate(equation):
        if char in "([{":
            brackets_stack.push(char)
        elif char in ")]}" and sets[char] != brackets_stack.pop():
            return (False, i)
    return (True, None) if brackets_stack.is_empty() else (False, len(equation) - 1)


class ScoreCard:
    def __init__(self, name):
        self.name = name
        self.scores = []

    def add_score(self, score):
        if type(score) is not int or not 0 <= score <= 100:
            return False
        self.scores.append(score)
        return True

    def average(self):
        if not self.scores:
            return
        total = 0
        for score in self.scores:
            total += score
        return total / len(self.scores)

    def passed(self):
        return (
            len(self.scores) > 1
            and self.average() >= 70
            and all(score >= 60 for score in self.scores)
        )

# לא נבדק האם שני מופעים חולקים את אותם ציונים כיוון שאין היגיון בדרישה זו. אין שום מניעה שלשני תלמידים יהיו ציונים זהים.

def best_card(cards):
    if not cards:
        return
    if len(cards) < 2:
        return cards[0]
    max_card = max(cards, key=lambda card: card.average())
    max_average = max_card.average()
    top_average = list(filter(lambda card: card.average() == max_average, cards))
    if len(top_average) == 1:
        return max_card
    most_scores = max(top_average, key=lambda card: card.scores)
    top_scores = list(
        filter(lambda card: len(card.scores) == len(most_scores.scores), top_average)
    )
    if len(top_scores) == 1:
        return top_scores[0]
    return min(top_scores, key=lambda card: card.name)


def eval_postfix(tokens):
    try:
        if len(tokens) % 2 == 0:
            raise ValueError("Invalid expression")
        tokens_stack = Stack()
        for token in tokens:
            if type(token) is int:
                tokens_stack.push(token)
            elif token in "-+*":
                val2 = tokens_stack.pop()
                val1 = tokens_stack.pop()
                match token:
                    case "-":
                        tokens_stack.push(val1 - val2)
                    case "+":
                        tokens_stack.push(val1 + val2)
                    case "*":
                        tokens_stack.push(val1 * val2)
            else:
                raise ValueError("Invalid expression")
        if len(tokens_stack.peek_all()) != 1:
            raise ValueError("Invalid expression")
        return tokens_stack.pop()
    except ValueError as e:
        print(e)


class UndoCounter:
    def __init__(self, start: int = 0) -> None:
        if not isinstance(start, int) or isinstance(start, bool) or start < 0:
            raise ValueError("start must be an int and greater than 0")
        self.value = start
        self.history = []

    def change(self, delta: int) -> bool:
        if not isinstance(delta, int) or isinstance(delta, bool) or delta == 0:
            raise ValueError("delta must be an int and can not be 0")
        if self.value + delta < 0:
            return False
        self.history.append(self.value)
        self.value += delta
        return True

    def undo(self) -> bool:
        if not self.history:
            return False
        self.value = self.history.pop()
        return True

    def history_size(self):
        return len(self.history)

    def apply_batch(self, deltas: list[int]) -> bool:
        if not isinstance(deltas, list) or not deltas:
            return False
        tmp_value = self.value
        for delta in deltas:
            if delta == 0 or not isinstance(delta, int) or isinstance(delta, bool):
                return False
            tmp_value += delta
            if tmp_value < 0:
                return False
        self.history.append(self.value)
        self.value = tmp_value
        return True


def check_UndoCounter_class():
    counter = UndoCounter(6)
    print(counter.value)
    print(counter.change(-15))  
    print(counter.value)
    print(counter.apply_batch([3, -15, 20]))
    print(counter.value)
    print(counter.change(8))
    print(counter.value)
    print(counter.undo())
    print(counter.value)
    print(counter.apply_batch([2, -2]))
    print(counter.value)

def is_stack_permutation(incoming, outgoing):
    if len(incoming) != len(outgoing):
        return False
    stack = []
    out_i = 0
    for item in incoming:
        stack.append(item)
        while stack and stack[-1] == outgoing[out_i]:
            stack.pop()
            out_i += 1
    return len(stack) == 0

# מכיוון שאין כפילויות ברשימות, הקרון שנמצא כרגע בראש המחסנית הוא האיבר היחיד שיכול לספק את הדרישה הנוכחית בסדר היציאה

def to_base(n, base):
    if type(n) is not int or type(base) is not int:
        raise ValueError("n and base must be exact integers")
    if n < 0 or not (2 <= base <= 16):
        raise ValueError("n can not be negative and base must be between 2 and 16")
    if n == 0:
        return "0"
    digits_map = "0123456789ABCDEF"
    stack = []
    while n > 0:
        remainder = n % base
        stack.append(digits_map[remainder])
        n //= base
    result = []
    while stack:
        result.append(stack.pop())

    return "".join(result)

# כל מספר מורכב מקבוצות של הבסיס ועוד שארית בודדת. כשמחלקים בבסיס בפעם הראשונה, כל הקבוצות מתחלקות בשלמותן, ומה שנשאר הוא רק היחידות הבודדות - כלומר הספרה הימנית ביותר. בכל חלוקה נוספת נחשפת הספרה הבאה משמאל, ולכן המחסנית הופכת את הסדר חזרה לכתיבה רגילה משמאל לימין.

# מעקב ידני (45 לבסיס 2):
# 45 חלקי 2 = 22, שארית 1. מחסנית: 1
# 22 חלקי 2 = 11, שארית 0. מחסנית: 1, 0
# 11 חלקי 2 = 5, שארית 1. מחסנית: 1, 0, 1
# 5 חלקי 2 = 2, שארית 1. מחסנית: 1, 0, 1, 1
# 2 חלקי 2 = 1, שארית 0. מחסנית: 1, 0, 1, 1, 0
# 1 חלקי 2 = 0, שארית 1. מחסנית: 1, 0, 1, 1, 0, 1

# שליפה מהמחסנית מהסוף להתחלה נותנת: 101101.