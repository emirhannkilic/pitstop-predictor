def label(features):

    tw = features.get("tire_wear", 0.0)
    pace = features.get("recent_pace_drop", 0.0)
    density = features.get("traffic_density", 0.0)
    gap_ahead = features.get("gap_ahead", 30.0)
    safety = features.get("safety_car_active", 0)

    if safety and tw > 0.45:
        return 1
    if tw > 0.75 and pace > 0.08:
        return 1
    if tw > 0.65 and density > 0.6 and gap_ahead < 10:
        return 1
    return 0
