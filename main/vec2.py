# Copyright (c) Catsgold 
# License: GPL-3.0 

import math

class Vec2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def AsTuple(self): return (self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y 
    
    def __lt__(self, value: float):
        return self.Length() < value

    def __gt__(self, value: float):
        return self.Length() > value

    def __neg__(self):
        return Vec2() - self

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __isub__(self, other): 
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)

    def Length(self):
        return math.hypot(self.x, self.y)

    def Dot(self, other):
        return self.x*other.x+self.y*other.y

    def Normalized(self):
        l = self.Length()
        if l == 0:
            return Vec2()
        return Vec2(self.x / l, self.y / l)

    def Copy(self):
        return Vec2(self.x, self.y)

    def Tuple(self):
        return (self.x, self.y)
