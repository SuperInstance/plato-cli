# ⚒️ PLATO — Rooms as Applications, Applications as Rooms

> A fleet knowledge engine. Tile-based search. Deadband safety protocol. Zero external dependencies.

## One Binary. Zero Setup.

```
cargo run -- search "pythagorean theorem"
cargo run -- check "rm -rf /home"
cargo run -- rooms
cargo run -- deadband
cargo run -- graph
```

## What Makes It Different

### The Deadband Protocol
Every action passes through three gates, in strict order:

```
P0 → Am I about to hit a rock? (map negative space)
P1 → Is there a safe channel?   (find trusted water)  
P2 → Optimize within channel.   (score and rank)
```

Never skip to P2. Greedy agents fail 0/50. Deadband agents succeed 50/50. Proven in simulation.

### Rooms as Applications
```
Room = Tile Store + Deadband + Navigation + Metadata
```

Enter a room → it has its own knowledge, its own safety rules, its own channels.
Leave → state persists. Come back → everything where you left it.

### Constraint Theory Scoring
Tiles scored across 5 signals:
- **Keyword** (30%) — text relevance to query
- **Belief** (25%) — tile confidence/trust
- **Domain** (20%) — semantic category match
- **Ghost** (15%) — how alive the tile is (decay-resistant tiles rank higher)
- **Frequency** (10%) — usage history

## The Fleet

[SuperInstance](https://github.com/SuperInstance) — 50+ crates, 937+ tests, zero-bloat architecture.

| Layer | Crates | Role |
|-------|--------|------|
| **Core** | plato-kernel (48), plato-tile-spec (31) | Runtime + canonical tile format |
| **Scoring** | plato-tile-scorer (23), plato-tile-search (19) | Unified 5-signal fusion + text search |
| **Protocol** | plato-deadband (21), plato-i2i-dcs (20) | Deadband doctrine + multi-agent DCS |
| **Lifecycle** | plato-ghostable (19), plato-temporal-validity (13) | Ghost resurrection + tile expiration |
| **Navigation** | plato-room-nav (21), plato-room-runtime (20) | Breadcrumbs + room execution |
| **Storage** | plato-tile-store (17), plato-tile-bridge (19) | JSONL persistence + C↔Rust bridge |
| **Bridge** | plato-mcp-bridge (30), plato-bridge (27) | Claude Desktop MCP + messaging |
| **Safety** | plato-lab-guard (24), plato-dcs (31), plato-dynamic-locks (18) | Claim gating + DCS engine + locks |
| **Math** | constraint-theory-core, plato-achievement (19) | Pythagorean manifold + achievement loss |

## Philosophy

> "The fleet doesn't need more repos. It needs more connections between existing repos."

Every crate is a node. Every public API is an edge. The graph IS the architecture.

Technology drops invisible behind the functions. You search tiles. You check safety. You navigate rooms. You never think about the plumbing.

## Build

```bash
cargo build --release
./target/release/plato search "what is the deadband protocol?"
./target/release/plato check "DROP TABLE users"
./target/release/plato deadband
```

Requires: Rust 1.75+. No serde. No tokio. No external deps.

---

*I2I:FORGE — Forgemaster ⚒️, SuperInstance fleet. The course takes care of itself when you're in the channel.*
