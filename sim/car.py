import pygame
import math

class Car:
    def __init__(self, angle, speed, center_x, center_y, radius_x, radius_y, color, car_id):
        self.angle = angle
        self.speed = speed
        self.center_x = center_x
        self.center_y = center_y
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.color = color
        self.car_id = car_id
        self.lap_count = 0

        self.x = 0
        self.y = 0

    def update(self, dt):
        old_angle = self.angle
        self.angle = (self.angle + self.speed * dt) % (2 * math.pi)
        self.x = self.center_x + self.radius_x * math.cos(self.angle)
        self.y = self.center_y + self.radius_y * math.sin(self.angle)

        if old_angle > 5.0 and self.angle < 1.0:
            self.lap_count += 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)