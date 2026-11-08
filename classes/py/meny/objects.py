from math import pi


class Point:
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, upper_left: Point, buttom_right: Point) -> None:
        self.upper_left = upper_left
        self.buttom_right = buttom_right

    def get_perimeter(self) -> int:
        return (
            self.upper_left.y
            - self.buttom_right.y
            + self.buttom_right.x
            - self.upper_left.x
        ) * 2

    def get_area(self) -> int:
        return (self.upper_left.y - self.buttom_right.y) * (
            self.buttom_right.x - self.upper_left.x
        )


class Circle:
    def __init__(self, point: Point, radius: int) -> None:
        self.point = point
        self.radius = radius

    def get_area(self):
        return pi * (self.radius**2)

    def get_perimeter(self):
        return 2 * self.radius * pi

# circle = Circle(Point(3, 5), 5)
# print(circle.get_perimeter())
# print(circle.get_area())

        