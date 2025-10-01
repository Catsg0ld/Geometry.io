# Copyright (c) Catsgold 
# License: GPL-3.0 

from components import TransformComponent, PhysicsComponent
from vec2 import Vec2
import pygame

class Agar:
    def __init__(self, position=Vec2(), initialRadius=25, color=(255, 255, 0)):
        self.transform = TransformComponent(position, scale=initialRadius)
        self.physics = PhysicsComponent()
        self.color = color
    
    def CollidesWith(self, targetCenter, targetRadius):
        dx = targetCenter.x - self.transform.position.x
        dy = targetCenter.y - self.transform.position.y
        
        dist2 = dx*dx + dy*dy
        
        radiusSum = self.transform.scale + targetRadius
        return dist2 <= radiusSum * radiusSum

    def Draw(self, surface: pygame.Surface, deltaTime=0.016, offset=Vec2()):
        self.transform.position += offset
        self.physics.Update(self.transform, deltaTime)

        pygame.draw.circle(surface, self.color, 
                           self.transform.position.AsTuple(),
                           self.transform.scale, 3)
        self.transform.position -= offset