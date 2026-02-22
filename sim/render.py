import pygame

def draw_hud(screen, font, cars, safety_car_active=False, nn_state=None, auto_mode=False):
    mode_font = pygame.font.Font(None, 30)
    hud_font = pygame.font.Font(None, 28)
    y_offset = 46

    if safety_car_active:
        sc_text = font.render("SAFETY CAR", True, (255, 200, 0))
        sc_rect = sc_text.get_rect(centerx=screen.get_width() // 2, y=10)
        pygame.draw.rect(screen, (80, 60, 0), sc_rect.inflate(20, 8))
        screen.blit(sc_text, sc_rect)

    mode_text = "MODE: AUTO (NN)" if auto_mode else "MODE: RECOMMENDATION"
    mode_color = (120, 255, 120) if auto_mode else (180, 180, 180)
    mode_surface = mode_font.render(mode_text + " | Press A to toggle", True, mode_color)
    screen.blit(mode_surface, (10, 10))

    for car in cars:
        lap_text = hud_font.render(f"Car {car.car_id}: Lap {car.lap_count}", True, car.color)
        screen.blit(lap_text, (10, y_offset))

        bar_x = 155
        bar_y = y_offset + 4
        bar_width = 130
        bar_height = 16

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
            pit_label = hud_font.render("IN PIT", True, (255, 200, 0))
            screen.blit(pit_label, (bar_x + bar_width + 10, y_offset))
        elif car.wants_pit:
            pit_label = hud_font.render("PIT SOON", True, (180, 180, 180))
            screen.blit(pit_label, (bar_x + bar_width + 10, y_offset))

        if nn_state and car.car_id in nn_state:
            rec = nn_state[car.car_id]
            label_short = "PIT" if rec["label"] == "PIT" else "STAY"
            nn_text = hud_font.render(
                f"NN | CAR {car.car_id}: {label_short} ({rec['conf']:.2f})",
                True,
                (200, 220, 255),
            )
            nn_rect = nn_text.get_rect(topright=(screen.get_width() - 20, y_offset))
            screen.blit(nn_text, nn_rect)

        y_offset += 46