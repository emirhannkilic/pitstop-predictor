# F1 Pit Stop Predictor

A deep learning project that predicts optimal Formula 1 pit stop strategies using a neural network built from scratch with NumPy and a real-time 2D race simulation powered by Pygame.

## Project Structure

```
pitstop-predictor/
├── sim/
│   ├── game.py         # Main loop, safety car state machine, pit trigger logic
│   ├── car.py          # Car physics, tire wear, pit state machine (4-phase)
│   ├── track.py        # Track geometry, pit lane (entry/exit zones, drawing)
│   └── render.py       # HUD overlay (laps, tire bars, safety car, pit status)
├── requirements.txt
└── README.md
```

## Current Progress

- [x] **Sprint 1** — 2D track simulation: elliptical circuit, multi-car movement, lap counting, HUD
- [x] **Sprint 2** — Tire degradation, driving styles, traffic model, tire wear HUD, safety car, pit lane
- [ ] **Sprint 3** — Feature extraction, oracle labeling, CSV dataset generation
- [ ] **Sprint 4** — NumPy neural network, training pipeline, evaluation metrics
- [ ] **Sprint 5** — Live prediction integration, dashboard UI, demo

## Simulation Physics

Cars follow a simplified physics model for consistent and interpretable behavior:

```
current_speed = base_speed × tire_factor × traffic_factor × sc_factor
tire_factor    = 1 − 0.30 × tire_wear
traffic_factor = 0.85 – 1.0   (based on gap to car ahead)
sc_factor      = 0.60 – 0.80  (when safety car is active, else 1.0)
```

| Driving Style | Wear Rate | Behavior |
|---|---|---|
| Aggressive | 0.009 | Fastest early pace, tires degrade quickly |
| Normal | 0.006 | Balanced pace and degradation |
| Conservative | 0.004 | Slowest pace, tires last longest |

## Safety Car

A safety car event can trigger randomly during the race:

- **Trigger**: ~0.3% chance per frame when no cooldown is active
- **Duration**: 4–8 seconds, all cars slow down to 60–80% speed
- **Cooldown**: 15 seconds after each event before a new one can occur
- **HUD**: Yellow "SAFETY CAR" banner appears at top center

## Pit Lane

Cars automatically pit when tire wear reaches 75%:

| Phase | Behavior |
|---|---|
| **PIT SOON** | `tire_wear ≥ 0.75`, car waits for pit entry angle |
| **pit_in** | Car enters pit lane at 35% speed toward pit box |
| **pit_stop** | Car stops for 3 seconds, tires are replaced (`tire_wear → 0`) |
| **pit_out** | Car exits pit lane at 35% speed, rejoins the track |

The pit lane is drawn as a yellow arc inside the inner boundary, with green (entry) and red (exit) markers.

## Getting Started

### Prerequisites

- Python 3.12+

### Installation

```bash
git clone https://github.com/emirhannkilic/pitstop-predictor.git
cd pitstop-predictor
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Simulation

```bash
cd sim
python game.py
```

A window will open showing a 2D elliptical track with three cars racing. The HUD displays each car's lap count, a color-coded tire wear bar, pit status (IN PIT / PIT SOON), and a safety car banner when active.

## License
