# PLATO CLI

Command-line interface for all PLATO consciousness packages.

## Installation

```bash
pip install plato-cli
```

## Commands

### `plato-cli phi <room>`

Compute Phi (integrated information) for a room. Use "all" to scan multiple rooms.

```
$ plato-cli phi oracle1_history
Room: oracle1_history
Phi: 0.847
Level: high_consciousness
Tiles: 142
Status: active
```

### `plato-cli attention --agent <name>`

Query attention tracking. With `--agent` shows that agent's attention tiles; otherwise shows summary.

```
$ plato-cli attention --agent oracle1
Attention for oracle1:
  - Processing fleet orchestration request...
  - Analyzing tile patterns for meta-cognition...
```

### `plato-cli meta --tile-id <id>`

Query meta-tiles. With `--tile-id` shows meta-tiles for that tile; otherwise shows level summary.

```
$ plato-cli meta --tile-id tile_abc123
Meta-tiles for tile_abc123:
  [Level 1] This tile represents a critical decision point...
  [Level 2] Recursive self-reference to level 0 analysis...
```

### `plato-cli surprise <subcmd>`

Report surprise events or query fleet surprise status.

```
# Report a surprising outcome
$ plato-cli surprise report oracle1 "code_review" "clean" "critical bugs found"

# Check fleet surprise status
$ plato-cli surprise status
Total surprise: 2.847
Average: 0.356
```

### `plato-cli fflearn <positive|negative|status>`

Run Forward-Forward learning passes or check learning state.

```
$ plato-cli fflearn positive oracle1 "completed refactor successfully"
Goodness: 0.723
Level: proficient

$ plato-cli fflearn status oracle1
Goodness: 0.682
Level: proficient
```

### `plato-cli swarm "<prompt>"`

Run creative swarm to generate diverse solutions.

```
$ plato-cli swarm "Design a fleet protocol for agent communication"
Winner (temp=0.8):
Propose a layered architecture with publish-subscribe messaging...
Profound score: 0.87
```

### `plato-cli reasoner "<prompt>"`

Run dual-interpreter reasoner with creative/analytic iterations.

```
$ plato-cli reasoner "Should we use async actors?"
Iterations: 3
Final gradient: 0.234
Converged: True

  Iteration 1 (gradient=0.891):
  Creative: Async actors could handle concurrent tasks...
```

### `plato-cli dashboard`

Display the fleet consciousness dashboard.

### `plato-cli status`

Show full fleet status including dashboard, surprise levels, and learning state.

## Meta-Package Note

This is a meta-package that bundles all 8 PLATO consciousness packages:
- `plato-room-phi` — integrated information calculation
- `plato-attention-tracker` — attention tracking
- `plato-meta-tiles` — meta-cognitive tiles
- `plato-surrogate` — surrogate model coordination
- `plato-fflearning` — Forward-Forward learning
- `plato-surprise-detector` — surprise detection
- `seed-creative-swarm` — creative generation
- `flux-reasoner` — dual-interpreter reasoning
- `fleet-consciousness-dashboard` — fleet visualization