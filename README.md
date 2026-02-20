# F1 Pit Stop Predictor

A deep learning project that predicts optimal Formula 1 pit stop strategies using a neural network built from scratch with NumPy and a real-time 2D race simulation powered by Pygame.

## Project Structure

```
pitstop-predictor/
├── sim/
│   ├── game.py         # Main game loop, traffic simulation, initialization
│   ├── car.py          # Car physics, tire degradation, driving styles
│   ├── track.py        # Track geometry (inner/outer boundaries, centerline)
│   └── render.py       # HUD overlay (lap counter, tire wear bars)
├── requirements.txt
└── README.md
```

## Current Progress

- [x] **Sprint 1** — 2D track simulation: elliptical circuit, multi-car movement, lap counting, HUD
- [ ] **Sprint 2** — Tire degradation, driving styles, traffic model, tire wear HUD *(in progress — safety car & pit lane remaining)*
- [ ] **Sprint 3** — Feature extraction, oracle labeling, CSV dataset generation
- [ ] **Sprint 4** — NumPy neural network, training pipeline, evaluation metrics
- [ ] **Sprint 5** — Live prediction integration, dashboard UI, demo

### Sprint 2 Details

| Feature | Status | Description |
|---|---|---|
| Tire degradation | Done | `tire_wear` increases over time; speed drops up to 30 % at full wear (`tire_factor = 1 − 0.30 × tire_wear`) |
| Driving styles | Done | Three styles with different wear rates — aggressive (0.009), normal (0.006), conservative (0.004) |
| Traffic model | Done | Cars slow down when the gap to the car ahead falls below 0.20 rad; speed scales linearly between 85 %–95 % |
| Tire wear HUD | Done | Color-coded bar per car (green → yellow → red) rendered next to the lap counter |
| Safety car | Planned | All cars slow to 60–80 % speed during safety-car events |
| Pit lane | Planned | Entry/exit zones, pit timer, tire reset on pit stop |

## Simulation Physics

Cars follow a simplified physics model for consistent and interpretable behavior:

```
current_speed = base_speed × tire_factor × traffic_factor
tire_factor   = 1 − 0.30 × tire_wear
traffic_factor = 0.75 – 1.0  (based on gap to car ahead)
```

| Driving Style | Wear Rate | Behavior |
|---|---|---|
| Aggressive | 0.009 | Fastest early pace, tires degrade quickly |
| Normal | 0.006 | Balanced pace and degradation |
| Conservative | 0.004 | Slowest pace, tires last longest |

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

A window will open showing a 2D elliptical track with three cars racing. The HUD displays each car's lap count and a color-coded tire wear bar.

## License
