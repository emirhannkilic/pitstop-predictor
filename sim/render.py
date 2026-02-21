import pygame

def draw_hud(screen, font, cars, safety_car_active=False):
    y_offset = 20

    if safety_car_active:
        sc_text = font.render("SAFETY CAR", True, (255, 200, 0))
        sc_rect = sc_text.get_rect(centerx=screen.get_width() // 2, y=10)
        pygame.draw.rect(screen, (80, 60, 0), sc_rect.inflate(20, 8))
        screen.blit(sc_text, sc_rect)

    for car in cars:
        lap_text = font.render(f"Car {car.car_id}: Lap {car.lap_count}", True, car.color)
        screen.blit(lap_text, (10, y_offset))

        bar_x = 200
        bar_y = y_offset + 5
        bar_width = 150
        bar_height = 20

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        fill_width = int(bar_width * car.tire_wear)
        if car.tire_wear < 0.5:
            color = (0, 255, 0)
        elif car.tire_wear < 0.75:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)

        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))

        if car.in_pit:
            pit_label = font.render("IN PIT", True, (255, 200, 0))
            screen.blit(pit_label, (bar_x + bar_width + 10, y_offset))
        elif car.wants_pit:
            pit_label = font.render("PIT SOON", True, (180, 180, 180))
            screen.blit(pit_label, (bar_x + bar_width + 10, y_offset))

        y_offset += 40