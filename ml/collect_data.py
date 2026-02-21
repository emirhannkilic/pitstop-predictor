import os
import sys
import csv
import math
import random
from pathlib import Path

# Headless pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sim.car import Car
from sim.track import Track
from ml.features import extract, FEATURE_NAMES
from ml.oracle import label

TRAFFIC_THRESHOLD_ANGLE = 0.20
TRAFFIC_FACTOR_MIN = 0.85
TRAFFIC_FACTOR_MAX = 0.95
TWO_PI = 2 * math.pi
SC_TRIGGER_CHANCE = 0.003
SC_DURATION_MIN = 4.0
SC_DURATION_MAX = 8.0
SC_COOLDOWN = 15.0
SC_FACTOR_MIN = 0.60
SC_FACTOR_MAX = 0.80
PIT_WEAR_THRESHOLD = 0.75

TOTAL_LAPS = 50
MAX_FRAMES = 200000
FPS = 60
DT = 1.0 / FPS


def update_traffic_factors(cars):
    for c in cars:
        gap = TWO_PI
        for other in cars:
            if other is c:
                continue
            diff = (other.angle - c.angle) % TWO_PI
            if 0 < diff < gap:
                gap = diff
        if gap >= TRAFFIC_THRESHOLD_ANGLE:
            c.traffic_factor = 1.0
        else:
            t = gap / TRAFFIC_THRESHOLD_ANGLE if TRAFFIC_THRESHOLD_ANGLE > 0 else 1.0
            c.traffic_factor = TRAFFIC_FACTOR_MIN + (TRAFFIC_FACTOR_MAX - TRAFFIC_FACTOR_MIN) * t


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))

    track = Track(center_x=600, center_y=400, radius_x=400, radius_y=250)
    cars = [
        Car(0, 1.0, track.center_x, track.center_y, track.centerline_rx, track.centerline_ry,
            (255, 0, 0), 1, "aggressive"),
        Car(2.09, 1.0, track.center_x, track.center_y, track.centerline_rx, track.centerline_ry,
            (0, 0, 255), 2, "normal"),
        Car(4.19, 1.0, track.center_x, track.center_y, track.centerline_rx, track.centerline_ry,
            (0, 255, 0), 3, "conservative"),
    ]

    safety_car_active = False
    safety_car_timer = 0.0
    safety_car_cooldown = 0.0
    sc_factor = 1.0

    rows = []
    frame = 0

    while frame < MAX_FRAMES:
        # Safety car
        if safety_car_active:
            safety_car_timer -= DT
            if safety_car_timer <= 0:
                safety_car_active = False
                safety_car_cooldown = SC_COOLDOWN
                sc_factor = 1.0
        else:
            safety_car_cooldown = max(0.0, safety_car_cooldown - DT)
            if safety_car_cooldown == 0.0 and random.random() < SC_TRIGGER_CHANCE:
                safety_car_active = True
                safety_car_timer = random.uniform(SC_DURATION_MIN, SC_DURATION_MAX)
                sc_factor = random.uniform(SC_FACTOR_MIN, SC_FACTOR_MAX)

        update_traffic_factors(cars)
        for c in cars:
            c.sc_factor = sc_factor
            if not c.wants_pit and not c.in_pit and c.tire_wear >= PIT_WEAR_THRESHOLD:
                c.wants_pit = True
            old_lap = c.lap_count
            c.update(DT, track)
            if c.lap_count > old_lap and 1 <= c.lap_count <= TOTAL_LAPS:
                feat_dict, feat_row = extract(c, cars, safety_car_active, TOTAL_LAPS)
                lab = label(feat_dict)
                rows.append(feat_row + [lab])

        if all(c.lap_count >= TOTAL_LAPS for c in cars):
            break
        frame += 1

    out_path = ROOT / "data" / "dataset.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(FEATURE_NAMES + ["label"])
        w.writerows(rows)

    pit_ratio = sum(r[-1] for r in rows) / len(rows) * 100 if rows else 0
    print(f"Wrote {len(rows)} rows to {out_path}")
    print(f"Pit ratio: {pit_ratio:.1f}% (target 15–35%)")
    pygame.quit()


if __name__ == "__main__":
    main()
