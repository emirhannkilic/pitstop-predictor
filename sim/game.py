import pygame
from car import Car
from track import Track
from render import draw_hud

pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("F1 Pit Stop Predictor")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

track = Track(center_x=WIDTH // 2, center_y=HEIGHT // 2, radius_x=400, radius_y=250)

cars = [
    Car(angle=0,    speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(255, 0, 0), car_id=1),
    Car(angle=2.09, speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(0, 0, 255), car_id=2),
    Car(angle=4.19, speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(0, 255, 0), car_id=3),
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(60) / 1000.0
    screen.fill((20, 20, 20))

    track.draw(screen)

    for car in cars:
        car.update(dt)
        car.draw(screen)

    draw_hud(screen, font, cars)
    pygame.display.flip()

pygame.quit()