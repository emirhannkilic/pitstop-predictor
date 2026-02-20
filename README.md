# F1 Pit Stop Predictor

A deep learning project that predicts optimal Formula 1 pit stop strategies using a neural network built from scratch with NumPy and a real-time 2D race simulation powered by Pygame.

## Project Structure

```
pitstop-predictor/
├── sim/
│   ├── game.py         # Main game loop and initialization
│   ├── car.py          # Car physics and movement on elliptical track
│   ├── track.py        # Track geometry (inner/outer boundaries, centerline)
│   └── render.py       # HUD overlay (lap counter per car)
├── requirements.txt
└── README.md
```

## Current Progress

- [x] **Sprint 1** — 2D track simulation: elliptical circuit, multi-car movement, lap counting, HUD
- [ ] **Sprint 2** — Tire degradation, fuel load, weather effects, telemetry data collection
- [ ] **Sprint 3** — NumPy neural network, training pipeline, oracle labeling
- [ ] **Sprint 4** — Live prediction integration, dashboard UI, evaluation metrics

## Getting Started

### Prerequisites

- Python 3.12+

### Installation

```bash
git clone https://github.com/<emirhannkilic>/pitstop-predictor.git
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

A window will open showing a 2D elliptical track with three cars racing. The HUD displays each car's current lap count.


## License
