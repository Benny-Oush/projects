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
    for char in equation:
        if char in "([{":
            brackets_stack.push(char)
        elif char in ")]}" and sets[char] != brackets_stack.pop():
            return False
    return brackets_stack.is_empty()


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


