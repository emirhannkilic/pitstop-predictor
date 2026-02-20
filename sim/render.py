import pygame

def draw_hud(screen, font, cars):
    y_offset = 20
    
    for car in cars:
        lap_text = font.render(f"Car {car.car_id}: Lap {car.lap_count}", True, car.color)
        screen.blit(lap_text, (10, y_offset))
        y_offset += 40