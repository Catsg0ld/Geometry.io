# Copyright (c) Catsgold 
# License: GPL-3.0 

import pygame
import sys
import time
from random import randint
from collisions import PolygonCircleCollision, PolygonCollision
from shape import Shape
from agar import Agar
from vec2 import Vec2

class Game:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont("Consolas", 16)
        
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("Geometry.io?")
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        self.MAX_UPGRADE_LEVEL = 5
        self.UPGRADE_COSTS = [50, 100, 200, 400, 800]
        self.PLAYER_SPEED = 2000
        self.BULLET_SPEED = 1500
        self.BASE_FIRE_RATE = 2.0  
        
        self.player = Agar(Vec2(self.WIDTH // 2, self.HEIGHT // 2), 30, (0, 255, 0))
        self.shapes = []
        self.bullets = []
        self.fragments = 9999
        self.lastShotTime = 0
        
        self.upgrades = {
            "FireRate": {"Level": 0, "Multiplier": 1},
            "Speed": {"Level": 0, "Multiplier": 1},
            "Damage": {"Level": 0, "Multiplier": 1}
        }
        self.upgradeKeyPressed = [False, False, False]

    def HandleInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        keys = pygame.key.get_pressed()
        mouseButtons = pygame.mouse.get_pressed()
        
        self.HandleMovement(keys)
        self.HandleUpgrades(keys)
        self.HandleShooting(mouseButtons)

    def HandleMovement(self, keys):
        move = Vec2()
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        
        if move.Length() > 0:
            move = move.Normalized() * self.PLAYER_SPEED * (self.clock.get_time() / 1000.0)
            self.player.physics.linearVelocity += move

    def HandleUpgrades(self, keys):
        upgradeKeys = [pygame.K_1, pygame.K_2, pygame.K_3]
        upgradeNames = list(self.upgrades.keys())
        
        for i, key in enumerate(upgradeKeys):
            if keys[key]:
                if not self.upgradeKeyPressed[i]:
                    self.TryUpgrade(upgradeNames[i])
                    self.upgradeKeyPressed[i] = True
            else:
                self.upgradeKeyPressed[i] = False  


    def TryUpgrade(self, upgradeName):
        upgrade = self.upgrades[upgradeName]
        if upgrade["Level"] >= self.MAX_UPGRADE_LEVEL:
            return

        cost = self.UPGRADE_COSTS[upgrade["Level"]]
        if self.fragments >= cost:
            self.fragments -= cost
            upgrade["Level"] += 1
            upgrade["Multiplier"] = 1 + 0.2 * upgrade["Level"]

    def HandleShooting(self, mouseButtons):
        if not mouseButtons[0]:
            return

        currentTime = time.time()
        effectiveFireRate = self.BASE_FIRE_RATE * self.upgrades["FireRate"]["Multiplier"]
        effectiveCooldown = 1.0 / effectiveFireRate 

        if currentTime - self.lastShotTime >= effectiveCooldown:
            self.lastShotTime = currentTime
            self.SpawnBullet()

    def SpawnBullet(self):
        mousePos = Vec2(*pygame.mouse.get_pos())
        center = Vec2(self.WIDTH // 2, self.HEIGHT // 2)
        direction = (mousePos - center).Normalized()
        
        bullet = Agar(self.player.transform.position.Copy(), 15, (255, 0, 0))
        bullet.physics.linearVelocity = direction * self.BULLET_SPEED * self.upgrades["Speed"]["Multiplier"]
        bullet.damage = 25 * self.upgrades["Damage"]["Multiplier"]

        self.bullets.append(bullet)

    def SpawnShapes(self):
        if len(self.shapes) >= 15:
            return
        
        angleCount = randint(3, 8)
        size = randint(25, 100)
        position = self.FindSpawnPosition()
        color = (randint(50, 255), randint(50, 255), randint(50, 255))
        
        self.shapes.append(Shape(position, angleCount, size, color))

    def FindSpawnPosition(self):
        minDistance = 200
        while True:
            spawnX = self.player.transform.position.x + randint(-self.WIDTH, self.WIDTH)
            spawnY = self.player.transform.position.y + randint(-self.HEIGHT, self.HEIGHT)
            distance = ((spawnX - self.player.transform.position.x) ** 2 +
                        (spawnY - self.player.transform.position.y) ** 2) ** 0.5
            if distance >= minDistance:
                return Vec2(spawnX, spawnY)

    def UpdateEntities(self):
        dt = self.clock.get_time() / 1000.0
        offset = Vec2(self.WIDTH // 2, self.HEIGHT // 2) - self.player.transform.position
        
        self.UpdateShapes(dt, offset)
        self.UpdateBullets(dt, offset)
        self.player.Draw(self.screen, dt, offset)
        self.HandleCollisions()
        self.CleanupEntities()

    def UpdateShapes(self, dt, offset):
        for shape in self.shapes:
            PolygonCircleCollision(shape, self.player)
            shape.Draw(self.screen, dt, offset)

    def UpdateBullets(self, dt, offset):
        for bullet in self.bullets:
            bullet.transform.position += bullet.physics.linearVelocity * dt
            bullet.Draw(self.screen, dt, offset)

    def HandleCollisions(self):
        shapesToRemove = []
        bulletsToRemove = []
        shapesToAdd = []
        
        for bullet in self.bullets:
            for shape in self.shapes:
                if PolygonCircleCollision(shape, bullet):
                    shape.hp -= bullet.damage
                    bulletsToRemove.append(bullet)
                    
                    if shape.hp <= 0:
                        shapesToRemove.append(shape)
                        self.fragments += shape.pointCount
                        
                        if shape.pointCount > 3:
                            direction = shape.transform.position - self.player.transform.position
                            childColor = (randint(50, 255), randint(50, 255), randint(50, 255))
                            child = Shape(shape.transform.position + direction,
                                        shape.pointCount - 1,
                                        randint(25, 100),
                                        childColor)
                            child.physics.linearVelocity = direction * 10
                            child.physics.angularVelocity = randint(-50, 50)
                            shapesToAdd.append(child)
                    break
                else:
                    if bullet.physics.linearVelocity < 2.0: 
                        bulletsToRemove.append(bullet)
        
        for i in range(len(self.shapes)):
            for j in range(i + 1, len(self.shapes)):
                PolygonCollision(self.shapes[i], self.shapes[j])
        
        for shape in shapesToRemove:
            if shape in self.shapes:
                self.shapes.remove(shape)
        
        self.shapes.extend(shapesToAdd)
        
        for bullet in bulletsToRemove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)

    def CleanupEntities(self):
        self.shapes = [shape for shape in self.shapes 
                      if not (abs(shape.transform.position.x - self.player.transform.position.x) > self.WIDTH + 200 or
                             abs(shape.transform.position.y - self.player.transform.position.y) > self.HEIGHT + 200)]
        
        self.bullets = [bullet for bullet in self.bullets 
                       if not (abs(bullet.transform.position.x - self.player.transform.position.x) > self.WIDTH + 200 or
                              abs(bullet.transform.position.y - self.player.transform.position.y) > self.HEIGHT + 200)]

    def DrawHUD(self):
        fpsText = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255))
        self.screen.blit(fpsText, (10, 10))

        statsLines = [
            f"Fragments: {self.fragments}",
            f"Fire Rate: x{self.upgrades['FireRate']['Multiplier']:.1f} ({self.upgrades['FireRate']['Level'] if self.upgrades['FireRate']['Level'] < self.MAX_UPGRADE_LEVEL else 'MAX'})",
            f"Speed: x{self.upgrades['Speed']['Multiplier']:.1f}",
            f"Damage: x{self.upgrades['Damage']['Multiplier']:.1f}"
        ]
        
        for i, line in enumerate(statsLines):
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (self.WIDTH - 200, 10 + i * 20))

        tipsLines = [
            "Upgrades: 1-3",
            f"1: Fire Rate (cost {self.UPGRADE_COSTS[self.upgrades['FireRate']['Level']] if self.upgrades['FireRate']['Level'] < self.MAX_UPGRADE_LEVEL else 'MAX'})",
            f"2: Speed (cost {self.UPGRADE_COSTS[self.upgrades['Speed']['Level']] if self.upgrades['Speed']['Level'] < self.MAX_UPGRADE_LEVEL else 'MAX'})",
            f"3: Damage (cost {self.UPGRADE_COSTS[self.upgrades['Damage']['Level']] if self.upgrades['Damage']['Level'] < self.MAX_UPGRADE_LEVEL else 'MAX'})"
        ]
        
        for i, line in enumerate(tipsLines):
            text = self.font.render(line, True, (255, 255, 0))
            self.screen.blit(text, (10, self.HEIGHT - 80 + i * 20))


    def DrawAimIndicator(self):
        mousePos = Vec2(*pygame.mouse.get_pos())
        center = Vec2(self.WIDTH // 2, self.HEIGHT // 2)
        arrowDir = (mousePos - center).Normalized()
        
        startPos = (self.WIDTH // 2, self.HEIGHT // 2)
        endPos = (self.WIDTH // 2 + arrowDir.x * 50, self.HEIGHT // 2 + arrowDir.y * 50)
        
        pygame.draw.line(self.screen, (255, 255, 0), startPos, endPos, 3)
        pygame.draw.circle(self.screen, (255, 255, 0), (int(endPos[0]), int(endPos[1])), 5)

    def Run(self):
        while True:
            self.screen.fill((0, 0, 0))
            
            self.HandleInput()
            self.SpawnShapes()
            self.UpdateEntities()
                        
            self.DrawAimIndicator()
            self.DrawHUD()
            
            pygame.display.flip()
            self.clock.tick(self.FPS)

if __name__ == "__main__":
    game = Game()
    game.Run()