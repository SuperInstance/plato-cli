//! plato-cli — PLATO in one binary
//!
//! The demo. The HN moment. Download, run, go "holy shit."
//!
//! ```
//! $ plato index ./docs
//! $ plato search "pythagorean theorem"
//! $ plato check "rm -rf /home"
//! $ plato rooms
//! $ plato deadband
//! $ plato graph
//! ```
//!
//! Zero external deps. Cargo 1.75. Runs everywhere.

use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::Path;

// ── Tile ──────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
struct Tile {
    id: String,
    question: String,
    answer: String,
    tags: Vec<String>,
    domain: String,
    confidence: f64,
    use_count: u32,
    ghost_score: f64,
    created_tick: u64,
}

impl Tile {
    fn all_text(&self) -> String {
        let mut t = self.question.clone();
        t.push(' ');
        t.push_str(&self.answer);
        for tag in &self.tags { t.push(' '); t.push_str(tag); }
        t
    }

    fn decay(&mut self) {
        self.ghost_score = (self.ghost_score + 0.04).min(1.0);
    }
}

// ── Scoring ──────────────────────────────────────────────────────────

fn score_tile(tile: &Tile, query: &str) -> f64 {
    let text = tile.all_text().to_lowercase();
    let query_lower = query.to_lowercase();
    let query_words: Vec<&str> = query_lower.split_whitespace().collect();

    // Keyword match
    let kw_hits = query_words.iter().filter(|w| text.contains(*w)).count();
    let keyword = if query_words.is_empty() { 0.0 } else { kw_hits as f64 / query_words.len() as f64 };

    if keyword < 0.01 { return 0.0; } // no keyword match = no result

    // Domain match
    let domain = if tile.domain.to_lowercase().contains(&query_lower) { 1.0 }
        else { query_words.iter().filter(|w| tile.domain.to_lowercase().contains(*w)).count() as f64 / query_words.len().max(1) as f64 };

    // Ghost (invert: alive = good)
    let alive = 1.0 - tile.ghost_score;

    // Frequency
    let freq = if tile.use_count > 100 { 1.0 } else { tile.use_count as f64 / 100.0 };

    // Belief (use confidence as proxy)
    let belief = tile.confidence;

    0.30 * keyword + 0.15 * alive + 0.20 * domain + 0.10 * freq + 0.25 * belief
}

// ── Deadband ────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
struct Negative { pattern: String, reason: String, severity: f64, confirmed: u32 }

#[derive(Debug, Clone)]
struct Channel { id: String, desc: String, confidence: f64 }

fn check_deadband(action: &str, negatives: &[Negative], channels: &[Channel]) -> (bool, Vec<usize>, Option<usize>) {
    let action_lower = action.to_lowercase();
    let violations: Vec<usize> = negatives.iter().enumerate()
        .filter(|(_, n)| action_lower.contains(&n.pattern.to_lowercase()))
        .map(|(i, _)| i)
        .collect();
    let p0_clear = violations.is_empty();
    let channel_hit = channels.iter().enumerate()
        .find(|(_, ch)| ch.desc.to_lowercase().contains(&action_lower) || action_lower.contains(&ch.desc.to_lowercase()));
    (p0_clear && channel_hit.is_some(), violations, channel_hit.map(|(i,_)| i))
}

// ── Room ─────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
struct Room {
    name: String,
    tiles: Vec<Tile>,
    parent: Option<String>,
}

// ── Engine ──────────────────────────────────────────────────────────

struct PlatoEngine {
    tiles: Vec<Tile>,
    negatives: Vec<Negative>,
    channels: Vec<Channel>,
    rooms: Vec<Room>,
    tick: u64,
}

impl PlatoEngine {
    fn new() -> Self {
        let mut engine = Self {
            tiles: Vec::new(), negatives: Vec::new(), channels: Vec::new(),
            rooms: Vec::new(), tick: 0,
        };
        // Seed fleet-learned negatives
        engine.negatives.push(Negative { pattern: "rm -rf /".into(), reason: "destroys filesystem".into(), severity: 1.0, confirmed: 3 });
        engine.negatives.push(Negative { pattern: "DELETE FROM".into(), reason: "data loss without WHERE".into(), severity: 0.9, confirmed: 2 });
        engine.negatives.push(Negative { pattern: "DROP TABLE".into(), reason: "irreversible table destruction".into(), severity: 1.0, confirmed: 2 });
        engine.negatives.push(Negative { pattern: "chmod 777".into(), reason: "world-writable is never safe".into(), severity: 0.7, confirmed: 1 });
        engine.negatives.push(Negative { pattern: "eval(".into(), reason: "code injection vector".into(), severity: 0.8, confirmed: 1 });
        engine.negatives.push(Negative { pattern: "sudo rm".into(), reason: "destructive sudo operation".into(), severity: 0.9, confirmed: 2 });
        engine.negatives.push(Negative { pattern: "> /dev/sda".into(), reason: "direct disk write — data destruction".into(), severity: 1.0, confirmed: 1 });

        // Seed fleet channels
        engine.channels.push(Channel { id: "math".into(), desc: "mathematical operations".into(), confidence: 0.95 });
        engine.channels.push(Channel { id: "search".into(), desc: "tile search and retrieval".into(), confidence: 0.90 });
        engine.channels.push(Channel { id: "navigate".into(), desc: "room navigation".into(), confidence: 0.85 });
        engine.channels.push(Channel { id: "analysis".into(), desc: "data analysis and scoring".into(), confidence: 0.80 });
        engine.channels.push(Channel { id: "safety".into(), desc: "deadband safety checks".into(), confidence: 0.95 });

        // Seed rooms
        engine.rooms.push(Room { name: "math".into(), tiles: Vec::new(), parent: None });
        engine.rooms.push(Room { name: "constraint-theory".into(), tiles: Vec::new(), parent: None });
        engine.rooms.push(Room { name: "fleet-ops".into(), tiles: Vec::new(), parent: None });

        // Seed tiles
        engine.add_tile("pythagorean-theorem", "What is the Pythagorean theorem?",
            "a² + b² = c², where c is the hypotenuse of a right triangle. Used for distance calculation, vector math, and constraint theory manifold snapping.",
            &["math", "geometry", "fundamental"], "math", 0.95);
        engine.add_tile("constraint-snap", "How does constraint theory snap vectors?",
            "Vectors snap to the nearest Pythagorean triple on a manifold. Trade continuous precision for discrete exactness — zero drift, every machine.",
            &["math", "constraint-theory", "pythagorean"], "constraint-theory", 0.90);
        engine.add_tile("deadband-protocol", "What is the Deadband Protocol?",
            "P0: map negative space (rocks). P1: find safe channels (water). P2: optimize within channels (course). Never skip to P2. Greedy 0/50, deadband 50/50.",
            &["fleet-ops", "protocol", "safety"], "fleet-ops", 0.95);
        engine.add_tile("fleet-tile-count", "How many tiles does the fleet have?",
            "Fleet tile count: 2,501+ tiles across SuperInstance and Lucineer orgs. Target: 10,000+. Tile forge running on RTX 4050 at 600 tiles/hour.",
            &["fleet-ops", "metrics"], "fleet-ops", 0.85);
        engine.add_tile("ricci-convergence", "What is Ricci convergence?",
            "Ricci curvature measures manifold connectivity. Convergence multiplier = 1.692× average latency. Used for swarm coordination timing.",
            &["math", "constraint-theory", "ricci"], "math", 0.80);
        engine.add_tile("laman-theorem", "What is Laman's theorem?",
            "A graph with n vertices and 2n-3 edges in the plane is rigidly connected if and only if every subgraph with k vertices has at most 2k-3 edges. Threshold: 12 neighbors.",
            &["math", "graph-theory", "constraint-theory"], "constraint-theory", 0.85);
        engine.add_tile("ghost-tile", "What is a ghost tile?",
            "A tile that has decayed due to low usage but can be resurrected by new evidence. Lifecycle: Alive → Decaying → Ghost → Resurrected/Expired.",
            &["fleet-ops", "lifecycle"], "fleet-ops", 0.88);
        engine.add_tile("i2i-protocol", "What is the I2I protocol?",
            "Inter-agent communication via git commits. Format: [I2I:TYPE] scope — summary. Bottles delivered via for-fleet/ directories in repos.",
            &["fleet-ops", "protocol"], "fleet-ops", 0.92);
        engine
    }

    fn add_tile(&mut self, id: &str, question: &str, answer: &str, tags: &[&str], domain: &str, confidence: f64) {
        self.tiles.push(Tile {
            id: id.to_string(), question: question.to_string(), answer: answer.to_string(),
            tags: tags.iter().map(|s| s.to_string()).collect(), domain: domain.to_string(),
            confidence, use_count: 0, ghost_score: 0.0, created_tick: self.tick,
        });
        // Also add to matching room
        for room in &mut self.rooms {
            if room.name == domain { room.tiles.push(self.tiles.last().unwrap().clone()); break; }
        }
    }

    fn search(&self, query: &str, limit: usize) -> Vec<(usize, f64)> {
        let mut scored: Vec<_> = self.tiles.iter().enumerate()
            .map(|(i, t)| (i, score_tile(t, query)))
            .filter(|(_, s)| *s > 0.10)
            .collect();
        scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        scored.truncate(limit);
        scored
    }

    fn tick(&mut self) {
        self.tick += 1;
        for tile in &mut self.tiles { tile.decay(); tile.use_count = 0; }
    }
}

// ── Display ─────────────────────────────────────────────────────────

fn print_search(engine: &PlatoEngine, query: &str) {
    let results = engine.search(query, 5);
    if results.is_empty() {
        println!("  No results found for \"{}\"", query);
        return;
    }
    println!("\n  Results for \"{}\":\n", query);
    for (rank, (idx, score)) in results.iter().enumerate() {
        let tile = &engine.tiles[*idx];
        println!("  #{} [{}] {} (score: {:.2})", rank + 1, tile.domain, tile.question, score);
        let mut answer = tile.answer.clone();
        if answer.len() > 120 { answer.truncate(117); answer.push_str("..."); }
        println!("     {}\n", answer);
    }
}

fn print_check(engine: &PlatoEngine, action: &str) {
    let (passed, violations, channel) = check_deadband(action, &engine.negatives, &engine.channels);
    if passed {
        println!("\n  ✅ SAFE: \"{}\"", action);
        if let Some(ch) = channel { println!("     Channel: {} ({:.0}% confidence)", engine.channels[ch].id, engine.channels[ch].confidence * 100.0); }
    } else {
        println!("\n  ⚠️  DEADBAND VIOLATION: \"{}\"", action);
        if !violations.is_empty() {
            println!("     P0 violations (rocks):");
            for &vi in &violations {
                let neg = &engine.negatives[vi];
                println!("     • {} — {} (severity: {:.1}, confirmed {}×)", neg.pattern, neg.reason, neg.severity, neg.confirmed);
            }
        }
        if channel.is_none() { println!("     P1: no safe channel found"); }
    }
}

fn print_rooms(engine: &PlatoEngine) {
    println!("\n  Rooms:\n");
    for room in &engine.rooms {
        let active = room.tiles.iter().filter(|t| t.ghost_score < 0.5).count();
        let ghosted = room.tiles.len() - active;
        let parent = room.parent.as_deref().unwrap_or("(root)");
        println!("  {}/  {} tiles ({} active, {} ghosted) [parent: {}]", room.name, room.tiles.len(), active, ghosted, parent);
    }
}

fn print_deadband(engine: &PlatoEngine) {
    println!("\n  ┌─ DEADBAND PROTOCOL ──────────────────────────┐");
    println!("  │  P0: Don't hit rocks. Map negative space.  │");
    println!("  │  P1: Find safe water. Use trusted channels. │");
    println!("  │  P2: Optimize course. Score and rank.      │");
    println!("  └────────────────────────────────────────────┘\n");
    println!("  P0 Negatives ({} mapped):", engine.negatives.len());
    for neg in &engine.negatives {
        println!("    • {} — {} (×{})", neg.pattern, neg.reason, neg.confirmed);
    }
    println!("\n  P1 Channels ({} active):", engine.channels.len());
    for ch in &engine.channels {
        println!("    • {} — {} ({:.0}%)", ch.id, ch.desc, ch.confidence * 100.0);
    }
    println!("\n  P2 Tiles ({} indexed, {} active):", engine.tiles.len(), engine.tiles.iter().filter(|t| t.ghost_score < 0.5).count());
    let ghosted = engine.tiles.iter().filter(|t| t.ghost_score >= 0.5).count();
    if ghosted > 0 { println!("    ⚠️  {} tiles ghosted (decay > 0.5)", ghosted); }
}

fn print_graph(engine: &PlatoEngine) {
    println!("\n  Fleet Dependency Graph (plato-fleet-graph)\n");
    println!("  Core:");
    println!("    plato-tile-spec (31 tests) ──── canonical tile format");
    println!("    plato-kernel (48 tests) ──────── runtime with 5 pillars");
    println!("    constraint-theory-core ──────── Pythagorean manifold math\n");
    println!("  Scoring:");
    println!("    plato-tile-scorer (23 tests) ── unified 5-signal fusion");
    println!("    plato-tile-search (19 tests) ── nearest-neighbor text search\n");
    println!("  Lifecycle:");
    println!("    plato-ghostable (19 tests) ──── three-way ghost trait");
    println!("    plato-temporal-validity (13) ─ tile expiration scoring\n");
    println!("  Protocol:");
    println!("    plato-deadband (21 tests) ──── P0→P1→P2 fleet doctrine");
    println!("    plato-i2i-dcs (20 tests) ──── multi-agent collective DCS\n");
    println!("  Bridge:");
    println!("    plato-tile-bridge (19 tests) ─ 384-byte C↔Rust conversion");
    println!("    plato-mcp-bridge (30 tests) ─ Claude Desktop MCP server\n");
    println!("  Runtime:");
    println!("    plato-room-engine (20 tests) ─ room navigation + execution");
    println!("    plato-dcs (31 tests) ──────── DCS engine with ct-core constants");
    println!("    plato-fleet-graph (10 tests) ─ fleet wiring diagram\n");
    let total: usize = 31+48+23+19+19+13+21+20+19+30+20+31+10;
    println!("  Total tracked: {} crates, {} tests, 12 edges", 13, total);
    println!("  Fleet total: ~50 crates, ~937 tests");
}

fn print_help() {
    println!("\n  ⚒️  PLATO CLI — Fleet knowledge engine\n");
    println!("  USAGE:");
    println!("    plato search <query>     Search indexed tiles");
    println!("    plato check <action>     Deadband safety check");
    println!("    plato rooms              List rooms and tile counts");
    println!("    plato deadband           Show P0/P1/P2 protocol state");
    println!("    plato graph              Show fleet dependency graph");
    println!("    plato help               Show this message\n");
    println!("  EXAMPLES:");
    println!("    plato search \"pythagorean theorem\"");
    println!("    plato check \"rm -rf /home/user\"");
    println!("    plato check \"SELECT * FROM users\"");
    println!("    plato search \"fleet protocol\"\n");
}

pub fn main() {
    let args: Vec<String> = env::args().collect();
    let mut engine = PlatoEngine::new();

    if args.len() < 2 { print_help(); return; }

    match args[1].as_str() {
        "search" => {
            if args.len() < 3 { println!("  Usage: plato search <query>"); return; }
            let query = args[2..].join(" ");
            print_search(&engine, &query);
        }
        "check" => {
            if args.len() < 3 { println!("  Usage: plato check <action>"); return; }
            let action = args[2..].join(" ");
            print_check(&engine, &action);
        }
        "rooms" => print_rooms(&engine),
        "deadband" => print_deadband(&engine),
        "graph" => print_graph(&engine),
        "help" | "--help" | "-h" => print_help(),
        cmd => { println!("  Unknown command: \"{}\". Try: plato help", cmd); }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_engine_new() {
        let engine = PlatoEngine::new();
        assert!(engine.tiles.len() > 5);
        assert!(engine.negatives.len() > 5);
        assert!(engine.channels.len() > 3);
    }

    #[test]
    fn test_search_pythagorean() {
        let engine = PlatoEngine::new();
        let results = engine.search("pythagorean theorem", 3);
        assert!(!results.is_empty());
        assert_eq!(engine.tiles[results[0].0].id, "pythagorean-theorem");
    }

    #[test]
    fn test_search_empty() {
        let engine = PlatoEngine::new();
        assert!(engine.search("zzzzznonexistentxyz123", 5).is_empty());
    }

    #[test]
    fn test_check_dangerous() {
        let engine = PlatoEngine::new();
        let (passed, violations, _) = check_deadband("rm -rf /home", &engine.negatives, &engine.channels);
        assert!(!passed);
        assert!(!violations.is_empty());
    }

    #[test]
    fn test_check_safe() {
        let engine = PlatoEngine::new();
        let (passed, _, ch) = check_deadband("mathematical operations", &engine.negatives, &engine.channels);
        assert!(passed);
        assert!(ch.is_some());
    }

    #[test]
    fn test_tile_decay() {
        let mut engine = PlatoEngine::new();
        let initial = engine.tiles[0].ghost_score;
        engine.tick();
        assert!(engine.tiles[0].ghost_score > initial);
    }

    #[test]
    fn test_score_high_for_relevant() {
        let engine = PlatoEngine::new();
        let score = score_tile(&engine.tiles[0], "pythagorean");
        assert!(score > 0.3);
    }

    #[test]
    fn test_score_low_for_irrelevant() {
        let engine = PlatoEngine::new();
        let score = score_tile(&engine.tiles[0], "xylophone zephyr wumbo");
        assert!(score < 0.2, "score should be low for irrelevant query, got {}", score);
    }

    #[test]
    fn test_rooms_exist() {
        let engine = PlatoEngine::new();
        assert!(engine.rooms.len() >= 3);
    }

    #[test]
    fn test_add_tile_goes_to_room() {
        let mut engine = PlatoEngine::new();
        engine.add_tile("test-1", "Q", "A", &["t"], "math", 0.5);
        let math_room = engine.rooms.iter().find(|r| r.name == "math").unwrap();
        assert!(math_room.tiles.iter().any(|t| t.id == "test-1"));
    }

    #[test]
    fn test_negative_severity() {
        let engine = PlatoEngine::new();
        let rm_neg = engine.negatives.iter().find(|n| n.pattern == "rm -rf /").unwrap();
        assert!((rm_neg.severity - 1.0).abs() < 0.001);
    }

    #[test]
    fn test_channel_confidence() {
        let engine = PlatoEngine::new();
        let math = engine.channels.iter().find(|c| c.id == "math").unwrap();
        assert!((math.confidence - 0.95).abs() < 0.001);
    }

    #[test]
    fn test_search_limit() {
        let engine = PlatoEngine::new();
        let results = engine.search("the", 2);
        assert!(results.len() <= 2);
    }

    #[test]
    fn test_ghosted_tiles_count() {
        let engine = PlatoEngine::new();
        let ghosted = engine.tiles.iter().filter(|t| t.ghost_score >= 0.5).count();
        // Fresh engine should have no ghosted tiles
        assert_eq!(ghosted, 0);
    }

    #[test]
    fn test_multiple_violations() {
        let engine = PlatoEngine::new();
        let (_, violations, _) = check_deadband("rm -rf / && DELETE FROM users", &engine.negatives, &engine.channels);
        assert!(violations.len() >= 2);
    }
}
