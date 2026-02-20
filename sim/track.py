import pygame
import math

class Track:
    def __init__(self, center_x, center_y, radius_x, radius_y, track_width=100):
        self.center_x = center_x
        self.center_y = center_y
        self.radius_x = radius_x          
        self.radius_y = radius_y       
        self.track_width = track_width

        self.inner_rx = radius_x - track_width
        self.inner_ry = radius_y - track_width
        self.centerline_rx = (radius_x + self.inner_rx) / 2
        self.centerline_ry = (radius_y + self.inner_ry) / 2

        # start/finish angle (0 radian = right middle point)
        self.start_finish_angle = 0

    def draw(self, screen):
        # outer boundary
        pygame.draw.ellipse(screen, (100, 100, 100),
            (self.center_x - self.radius_x, self.center_y - self.radius_y,
             self.radius_x * 2, self.radius_y * 2), 5)

        # inner boundary
        pygame.draw.ellipse(screen, (100, 100, 100),
            (self.center_x - self.inner_rx, self.center_y - self.inner_ry,
             self.inner_rx * 2, self.inner_ry * 2), 5)

        # centerline 
        points = []
        for i in range(120):
            a = 2 * math.pi * i / 120
            x = self.center_x + self.centerline_rx * math.cos(a)
            y = self.center_y + self.centerline_ry * math.sin(a)
            points.append((x, y))
        pygame.draw.lines(screen, (60, 60, 60), True, points, 1)


        a = self.start_finish_angle
        inner_x = self.center_x + self.inner_rx * math.cos(a)
        inner_y = self.center_y + self.inner_ry * math.sin(a)
        outer_x = self.center_x + self.radius_x * math.cos(a)
        outer_y = self.center_y + self.radius_y * math.sin(a)
        pygame.draw.line(screen, (255, 255, 255), (inner_x, inner_y), (outer_x, outer_y), 3)