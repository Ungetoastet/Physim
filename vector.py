import math

class vector2:
    x:float
    y:float
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
    
    @staticmethod
    def up():
        return vector2(0, -1)
    @staticmethod
    def down():
        return vector2(0, 1)
    @staticmethod
    def left():
        return vector2(-1, 0)
    @staticmethod
    def right():
        return vector2(1, 0)
    @staticmethod
    def zero():
        return vector2(0, 0)
    @staticmethod
    def one():
        return vector2(1, 1)
    
    # Add two vectors
    def __add__(self, other):
        new_x = self.x + other.x
        new_y = self.y + other.y
        return vector2(new_x, new_y)

    # Multiply vector * int
    def __mul__(self, other):
        new_x = self.x * other
        new_y = self.y * other
        return vector2(new_x, new_y)

    # Substract two vectors
    def __sub__(self, other):
        new_x = self.x - other.x
        new_y = self.y - other.y
        return vector2(new_x, new_y)

    # Divide vector / int
    def __truediv__(self, other):
        new_x = self.x / other
        new_y = self.y / other
        return vector2(new_x, new_y)

    # Calculate length
    def len(self):
        length = math.sqrt(self.x*self.x + self.y*self.y)
        return length

    # Dot product
    def __and__(self, other):
        dot = self.x * other.x + self.y * other.y
        return dot

    # String representation
    def __str__(self) -> str:
        return f"( {self.x} | {self.y} )"
    
    def __neg__(self):
        return self * -1

    # Unit vector
    def unit(self):
        if self.len() == 0:
            return vector2(1, 1)
        return (self / self.len())

    # Are two vectors perpendicular
    def perp(vec1, vec2):
        if (vec1 & vec2) == 0:
            return True
        return False

    def dist(vec1, vec2):
        d = (vec1 - vec2).len()
        return d

