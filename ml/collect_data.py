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
TRAFFIC_FACTOR_MIN = 0.75
TRAFFIC_FACTOR_MAX = 0.90
TWO_PI = 2 * math.pi
SC_TRIGGER_CHANCE = 0.003
SC_DURATION_MIN = 4.0
SC_DURATION_MAX = 8.0
SC_COOLDOWN = 15.0
SC_FACTOR_MIN = 0.60
SC_FACTOR_MAX = 0.80
PIT_WEAR_THRESHOLD = 0.75

TOTAL_LAPS = 50
NUM_RACES = 100
MAX_FRAMES = 200000
FPS = 60
DT = 1.0 / FPS

STYLES = ["aggressive", "normal", "conservative"]


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


def make_cars(track):
    spacing = TWO_PI / 5
    cars = []
    for i in range(5):
        style = random.choice(STYLES)
        cars.append(Car(
            angle=spacing * i,
            speed=1.0,
            center_x=track.center_x,
            center_y=track.center_y,
            radius_x=track.centerline_rx,
            radius_y=track.centerline_ry,
            color=(0, 0, 0),
            car_id=i + 1,
            driving_style=style,
        ))
    return cars


def run_race(track):
    cars = make_cars(track)

    safety_car_active = False
    safety_car_timer = 0.0
    safety_car_cooldown = 0.0
    sc_factor = 1.0

    rows = []
    frame = 0

    while frame < MAX_FRAMES:
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

    return rows


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))

    track = Track(center_x=600, center_y=400, radius_x=400, radius_y=250)
    all_rows = []

    for race in range(NUM_RACES):
        rows = run_race(track)
        all_rows.extend(rows)
        if (race + 1) % 20 == 0:
            print(f"  Race {race + 1}/{NUM_RACES} done — {len(all_rows)} rows so far")

    out_path = ROOT / "data" / "dataset.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(FEATURE_NAMES + ["label"])
        w.writerows(all_rows)

    pit_ratio = sum(r[-1] for r in all_rows) / len(all_rows) * 100 if all_rows else 0
    print(f"\nWrote {len(all_rows)} rows to {out_path}")
    print(f"Pit ratio: {pit_ratio:.1f}% (target 15–35%)")
    pygame.quit()


if __name__ == "__main__":
    main()
