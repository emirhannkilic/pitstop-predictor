import math
import random
import sys
from pathlib import Path

import numpy as np
import pygame

from car import Car
from render import draw_hud
from track import Track

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ml.features import extract
from ml.nn_numpy import predict_proba

TRAFFIC_THRESHOLD_ANGLE = 0.20
TRAFFIC_FACTOR_MIN = 0.75
TRAFFIC_FACTOR_MAX = 0.90
TWO_PI = 2 * math.pi
TOTAL_LAPS = 50

SC_TRIGGER_CHANCE = 0.003      # per-frame probability when eligible
SC_DURATION_MIN = 4.0          # seconds
SC_DURATION_MAX = 8.0
SC_COOLDOWN = 15.0             # seconds before another SC can trigger
SC_FACTOR_MIN = 0.60
SC_FACTOR_MAX = 0.80

PIT_WEAR_THRESHOLD = 0.75

def load_saved_model():
    model_path = ROOT / "models" / "nn_model.npz"
    data = np.load(model_path, allow_pickle=True)

    params = {
        "W1": data["W1"], "b1": data["b1"],
        "W2": data["W2"], "b2": data["b2"],
        "W3": data["W3"], "b3": data["b3"],
    }
    mean = data["mean"]
    std = data["std"]
    return params, mean, std


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
            t = gap / TRAFFIC_THRESHOLD_ANGLE if TRAFFIC_THRESHOLD_ANGLE > 0 else 1.0
            car.traffic_factor = TRAFFIC_FACTOR_MIN + (TRAFFIC_FACTOR_MAX - TRAFFIC_FACTOR_MIN) * t


pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("F1 Pit Stop Predictor")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

track = Track(center_x=WIDTH // 2, center_y=HEIGHT // 2, radius_x=400, radius_y=250)

spacing = TWO_PI / 5
cars = [
    Car(angle=spacing * 0, speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(255, 0, 0), car_id=1, driving_style="aggressive"),
    Car(angle=spacing * 1, speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(0, 0, 255), car_id=2, driving_style="normal"),
    Car(angle=spacing * 2, speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(0, 255, 0), car_id=3, driving_style="conservative"),
    Car(angle=spacing * 3, speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(255, 165, 0), car_id=4, driving_style="aggressive"),
    Car(angle=spacing * 4, speed=1.0, center_x=track.center_x, center_y=track.center_y,
        radius_x=track.centerline_rx, radius_y=track.centerline_ry, color=(255, 255, 0), car_id=5, driving_style="normal"),
]

model_params, norm_mean, norm_std = load_saved_model()
nn_state = {car.car_id: {"label": "N/A", "conf": 0.0} for car in cars}
auto_mode = False

safety_car_active = False
safety_car_timer = 0.0
safety_car_cooldown = 0.0
sc_factor = 1.0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            auto_mode = not auto_mode

    dt = clock.tick(60) / 1000.0

    # --- safety car state machine ---
    if safety_car_active:
        safety_car_timer -= dt
        if safety_car_timer <= 0:
            safety_car_active = False
            safety_car_cooldown = SC_COOLDOWN
            sc_factor = 1.0
    else:
        safety_car_cooldown = max(0.0, safety_car_cooldown - dt)
        if safety_car_cooldown == 0.0 and random.random() < SC_TRIGGER_CHANCE:
            safety_car_active = True
            safety_car_timer = random.uniform(SC_DURATION_MIN, SC_DURATION_MAX)
            sc_factor = random.uniform(SC_FACTOR_MIN, SC_FACTOR_MAX)

    screen.fill((20, 20, 20))
    track.draw(screen)

    update_traffic_factors(cars)
    for car in cars:
        car.sc_factor = sc_factor
        if not car.wants_pit and not car.in_pit and car.tire_wear >= PIT_WEAR_THRESHOLD:
            car.wants_pit = True
        old_lap = car.lap_count
        car.update(dt, track)
        car.draw(screen)

        if car.lap_count > old_lap:
            _, feat_row = extract(car, cars, safety_car_active, TOTAL_LAPS)
            x = np.array(feat_row, dtype=np.float64).reshape(1, -1)
            x = (x - norm_mean) / norm_std

            proba = float(predict_proba(x, model_params)[0, 0])
            label = "PIT" if proba >= 0.5 else "STAY OUT"
            nn_state[car.car_id] = {"label": label, "conf": proba}
            if auto_mode and label == "PIT" and not car.in_pit and not car.wants_pit:
                car.wants_pit = True

    draw_hud(screen, font, cars, safety_car_active, nn_state, auto_mode)
    pygame.display.flip()

pygame.quit()