import math

TWO_PI = 2 * math.pi
FEATURE_NAMES = [
    "tire_wear", "laps_since_pit", "recent_pace_drop", "gap_ahead", "gap_behind",
    "traffic_density", "is_stuck", "lap_norm", "safety_car_active"
]

GAP_ANGLE_WINDOW = 0.5
STUCK_THRESHOLD_SEC = 2.0
PACE_DROP_CLIP = 0.3


def angular_speed(car):
    tf = 1 - 0.30 * car.tire_wear
    return car.base_speed * tf * car.traffic_factor * car.sc_factor


def gap_to_seconds(angle_gap, car):
    w = angular_speed(car)
    if w <= 0:
        return 30.0
    return min(30.0, max(0.0, angle_gap / w))


def extract(car, all_cars, safety_car_active, total_laps):
    tire_wear = min(1.0, max(0.0, car.tire_wear))
    laps_since_pit = min(50, max(0, car.laps_since_pit))

    # recent_pace_drop: from last 3–4 lap speeds
    recent_pace_drop = 0.0
    if len(car.lap_speeds) >= 2:
        speeds = car.lap_speeds[-4:] if len(car.lap_speeds) >= 4 else car.lap_speeds
        if len(speeds) >= 2:
            drop = (max(speeds) - min(speeds)) / max(speeds) if max(speeds) > 0 else 0.0
            recent_pace_drop = min(PACE_DROP_CLIP, max(0.0, drop))

    # gap_ahead, gap_behind: nearest car ahead/behind in angle, converted to seconds
    gap_ahead = 30.0
    gap_behind = 30.0
    for other in all_cars:
        if other is car or other.in_pit:
            continue
        diff = (other.angle - car.angle) % TWO_PI
        if 0 < diff < TWO_PI / 2:
            gap_ahead = min(gap_ahead, gap_to_seconds(diff, car))
        if 0 < (TWO_PI - diff) < TWO_PI / 2:
            gap_behind = min(gap_behind, gap_to_seconds(TWO_PI - diff, car))

    traffic_density = 1.0 - car.traffic_factor
    traffic_density = min(1.0, max(0.0, traffic_density))

    is_stuck = 1 if car.seconds_in_traffic >= STUCK_THRESHOLD_SEC else 0

    # progress through race
    lap_norm = min(1.0, max(0.0, car.lap_count / total_laps)) if total_laps > 0 else 0.0

    safety_car_active_int = 1 if safety_car_active else 0

    d = {
        "tire_wear": tire_wear,
        "laps_since_pit": laps_since_pit,
        "recent_pace_drop": recent_pace_drop,
        "gap_ahead": gap_ahead,
        "gap_behind": gap_behind,
        "traffic_density": traffic_density,
        "is_stuck": is_stuck,
        "lap_norm": lap_norm,
        "safety_car_active": safety_car_active_int,
    }
    row = [d[k] for k in FEATURE_NAMES]
    return d, row
