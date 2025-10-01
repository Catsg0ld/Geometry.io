# Copyright (c) Catsgold 
# License: GPL-3.0 

from components import PhysicsComponent, TransformComponent
from math import cos, sin, pi, radians
from vec2 import Vec2
import pygame

def GenPolygon(c, s, r):
    return [(c.x + cos(2*pi*i/r) * s,
             c.y + sin(2*pi*i/r) * s)
            for i in range(r)]

def ApplyTransform(points, transform: TransformComponent):
    result = []
    
    c, s = cos(radians(transform.rotation)), sin(radians(transform.rotation))
    for x, y in points:
        x, y = x * transform.scale, y * transform.scale
        tx, ty = x * c - y * s, x * s + y * c
        tx += transform.position.x
        ty += transform.position.y
        result.append((tx, ty))
    return result


class Shape():
    def __init__(self, position=Vec2(), pointCount=3, size=50, color=(255, 0, 0)):
        super().__init__()
        self.physics = PhysicsComponent()
        self.transform = TransformComponent(position)
        self.pointCount = pointCount
        self.color = color
        self.size = size
        self.points = GenPolygon(Vec2(), size, pointCount)
        self.hp = pointCount * 25

    def Draw(self, surface: pygame.Surface, deltaTime=0.016, offset=Vec2()):
        if (self.points != None):
            self.transform.position += offset
            self.physics.Update(self.transform, deltaTime)
            pygame.draw.polygon(surface, self.color, ApplyTransform(self.points, self.transform), 3)
            self.transform.position -= offset

    def GetPoints(self): return ApplyTransform(self.points, self.transform)   

    
    def Copy(self):
        newShape = Shape(
            position=self.transform.position.Copy(), 
            pointCount=self.pointCount,
            size=self.size 
        )

        newShape.color = self.color
        newShape.hp = self.hp

        newShape.physics.linearVelocity = self.physics.linearVelocity.Copy()
        newShape.physics.angularVelocity = self.physics.angularVelocity
        return newShape