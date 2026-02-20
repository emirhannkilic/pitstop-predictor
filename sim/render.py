import pygame

def draw_hud(screen, font, cars):
    y_offset = 20
    
    for car in cars:
        lap_text = font.render(f"Car {car.car_id}: Lap {car.lap_count}", True, car.color)
        screen.blit(lap_text, (10, y_offset))
        
        # Tire wear bar
        bar_x = 200
        bar_y = y_offset + 5
        bar_width = 150
        bar_height = 20

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        fill_width = int(bar_width * car.tire_wear)
        if car.tire_wear < 0.5:
            color = (0, 255, 0)  # green
        elif car.tire_wear < 0.75:
            color = (255, 255, 0)  # yellow
        else:
            color = (255, 0, 0)  # red

        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
        
        y_offset += 40