import math
import pygame
from car import Car
from track import Track
from render import draw_hud

TRAFFIC_THRESHOLD_ANGLE = 0.20  # radians; traffic factor kicks in below this gap
TRAFFIC_FACTOR_MIN = 0.85
TRAFFIC_FACTOR_MAX = 0.95
TWO_PI = 2 * math.pi


def update_traffic_factors(cars):
    for car in cars:
        gap = TWO_PI  # no car ahead
        for other in cars:
            if other is car:
                continue
            diff = (other.angle - car.angle) % TWO_PI
            if 0 < diff < gap:
                gap = diff
        if gap >= TRAFFIC_THRESHOLD_ANGLE:
            car.traffic_factor = 1.0
        else:
            # linear: gap 0 -> MIN, gap threshold -> MAX
            t = gap / TRAFFIC_THRESHOLD_ANGLE if TRAFFIC_THRESHOLD_ANGLE > 0 else 1.0
            car.traffic_factor = TRAFFIC_FACTOR_MIN + (TRAFFIC_FACTOR_MAX - TRAFFIC_FACTOR_MIN) * t


pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("F1 Pit Stop Predictor")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

track = Track(center_x=WIDTH // 2, center_y=HEIGHT // 2, radius_x=400, radius_y=250)

cars = [
    Car(angle=0,    speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(255, 0, 0), car_id=1, driving_style="aggressive"),
    Car(angle=2.09, speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(0, 0, 255), car_id=2, driving_style="normal"),
    Car(angle=4.19, speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(0, 255, 0), car_id=3, driving_style="conservative"),
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(60) / 1000.0
    screen.fill((20, 20, 20))

    track.draw(screen)

    update_traffic_factors(cars)
    for car in cars:
        car.update(dt)
        car.draw(screen)

    draw_hud(screen, font, cars)
    pygame.display.flip()

pygame.quit()