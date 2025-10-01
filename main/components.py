# Copyright (c) Catsgold 
# License: GPL-3.0 

from vec2 import Vec2

class TransformComponent:
    def __init__(self, position=Vec2(), rotation=0, scale=1):
        self.position = position
        self.rotation = rotation
        self.scale = scale

class PhysicsComponent:
    def __init__(self, linearVelocity=Vec2(), angularVelocity=0.0, mass=1.0, drag=0.999):
        self.linearVelocity = linearVelocity
        self.angularVelocity = angularVelocity
        self.mass = mass
        self.drag = drag

    def Update(self, transformComponent, deltaTime):
        if self.linearVelocity.Length() > 0.0:
            transformComponent.position += self.linearVelocity * deltaTime

            damping = (1.0 - self.drag) ** deltaTime
            self.linearVelocity *= damping

            if self.linearVelocity.Length() < 0.001:
                self.linearVelocity = Vec2()

        if abs(self.angularVelocity) > 0.0:
            transformComponent.rotation += self.angularVelocity * deltaTime

            damping = (1.0 - self.drag) ** deltaTime
            self.angularVelocity *= damping

            if abs(self.angularVelocity) < 0.001:
                self.angularVelocity = 0.0
