"""
PLATO CLI — Command-line interface for all consciousness packages

Usage:
    plato-cli phi fleet_orchestration
    plato-cli attention oracle1
    plato-cli meta tiles fleet_orchestration
    plato-cli surprise report kimi-cli "refactor" "30 min" "2 hours"
    plato-cli fflearn positive oracle1 "good outcome"
    plato-cli swarm "Design a fleet protocol"
    plato-cli reasoner "Should we use async actors?"
    plato-cli dashboard
    plato-cli status
"""

import sys
import argparse
from typing import List, Dict, Any

def cmd_phi(args) -> None:
    """Compute Phi for a room."""
    from plato_room_phi import RoomPhi
    phi = RoomPhi()
    if args.room == "all":
        results = phi.scan_all_rooms(limit=10)
        print(f"{'Room':<30} {'Phi':<8} {'Level':<15} {'Tiles':<8}")
        print("-" * 65)
        for r in results:
            print(f"{r['room']:<30} {r['phi']:<8.3f} {r['level']:<15} {r['tile_count']:<8}")
    else:
        result = phi.compute_for_room(args.room)
        print(f"Room: {result['room']}")
        print(f"Phi: {result['phi']:.3f}")
        print(f"Level: {result['level']}")
        print(f"Tiles: {result['tile_count']}")
        print(f"Status: {result['status']}")

def cmd_attention(args) -> None:
    """Query attention tracking."""
    from plato_attention import AttentionTracker
    tracker = AttentionTracker()
    if args.agent:
        tiles = tracker.get_agent_attention(args.agent)
        print(f"Attention for {args.agent}:")
        for t in tiles:
            print(f"  - {t.get('answer', '')[:80]}")
    else:
        summary = tracker.get_attention_summary()
        print(f"Total attention tiles: {summary['total_tiles']}")
        print(f"Agents tracking: {summary['agents_tracking']}")
        print("By agent:")
        for agent, count in summary.get("by_agent", {}).items():
            print(f"  {agent}: {count} tiles")

def cmd_meta(args) -> None:
    """Query meta-tiles."""
    from plato_meta import MetaTileEngine
    meta = MetaTileEngine()
    if args.tile_id:
        tiles = meta.get_meta_tiles_for(args.tile_id)
        print(f"Meta-tiles for {args.tile_id}:")
        for t in tiles:
            print(f"  [Level {t.get('meta_level', 0)}] {t.get('answer', '')[:80]}")
    else:
        summary = meta.get_meta_level_summary()
        print("Meta-tile levels:")
        for level, count in summary.items():
            print(f"  {level}: {count}")

def cmd_surprise(args) -> None:
    """Report surprise or query fleet surprise."""
    from plato_surprise import SurpriseDetector
    detector = SurpriseDetector()
    if args.subcmd == "report" and len(args.positional) >= 4:
        agent, event, expected, observed = args.positional[0], args.positional[1], args.positional[2], args.positional[3]
        result = detector.report_outcome(agent=agent, expected=expected, observed=observed, domain=args.domain or "fleet_orchestration")
        print(f"Surprise: {result['surprise']:.3f}")
        print(f"Accumulated: {result['accumulated_surprise']:.3f}")
        if result['threshold_exceeded']:
            print("⚠️  THRESHOLD EXCEEDED — self-healing triggered")
    elif args.subcmd == "status":
        fleet = detector.get_fleet_surprise()
        print(f"Total surprise: {fleet['total_surprise']:.3f}")
        print(f"Average: {fleet['average_surprise']:.3f}")
        if fleet['critical_agents']:
            print(f"Critical agents: {', '.join(fleet['critical_agents'])}")

def cmd_fflearn(args) -> None:
    """Run Forward-Forward learning."""
    from plato_fflearning import ForwardForwardLearner
    learner = ForwardForwardLearner()
    if args.pass_type == "positive":
        result = learner.positive_pass(agent=args.agent, experience=args.experience)
        print(f"Goodness: {result['goodness']:.3f}")
        print(f"Level: {learner._goodness_to_level(result['goodness'])}")
    elif args.pass_type == "negative":
        result = learner.negative_pass(agent=args.agent, experience=args.experience)
        print(f"Goodness: {result['goodness']:.3f}")
    elif args.pass_type == "status":
        state = learner.get_learning_state(args.agent)
        print(f"Goodness: {state['goodness']:.3f}")
        print(f"Level: {state['level']}")

def cmd_swarm(args) -> None:
    """Run creative swarm."""
    from seed_swarm import CreativeSwarm
    swarm = CreativeSwarm(deepinfra_key=args.deepinfra_key or "RhZPtvuy4cXzu02LbBSffbXeqs5Yf2IZ")
    result = swarm.generate(prompt=args.prompt, include_pro=True)
    print(f"Winner (temp={result['winner']['temperature']}):")
    print(f"{result['winner']['text'][:300]}")
    print(f"\nProfound score: {result['pro_score']:.2f}")

def cmd_reasoner(args) -> None:
    """Run dual-interpreter reasoner."""
    from flux_reasoner import FluxReasoner
    reasoner = FluxReasoner()
    result = reasoner.reason_with_iterations(input=args.prompt, iterations=3)
    print(f"Iterations: {len(result['iterations'])}")
    print(f"Final gradient: {result['final_gradient']:.3f}")
    print(f"Converged: {result['converged']}")
    for i, iteration in enumerate(result['iterations']):
        print(f"\n  Iteration {i+1} (gradient={iteration['gradient']:.3f}):")
        print(f"  Creative: {iteration['creative'][:150]}...")

def cmd_dashboard(args) -> None:
    """Show fleet consciousness dashboard."""
    from fleet_dashboard import FleetDashboard
    dashboard = FleetDashboard()
    print(dashboard.render_text())

def cmd_status(args) -> None:
    """Show full fleet status."""
    from fleet_dashboard import FleetDashboard
    from plato_surprise import SurpriseDetector
    from plato_fflearning import ForwardForwardLearner
    dashboard = FleetDashboard()
    print(dashboard.render_text())
    print()
    detector = SurpriseDetector()
    fleet_surprise = detector.get_fleet_surprise()
    print(f"Fleet surprise: {fleet_surprise['total_surprise']:.3f}")
    learner = ForwardForwardLearner()
    fleet_state = learner.get_fleet_learning_state()
    print(f"Fleet learning avg: {fleet_state.get('fleet_goodness_avg', 0.5):.3f}")

def main():
    parser = argparse.ArgumentParser(description="PLATO CLI — consciousness package commands")
    subparsers = parser.add_subparsers(dest="command")
    
    # phi
    p = subparsers.add_parser("phi")
    p.add_argument("room", nargs="?", default="oracle1_history")
    
    # attention
    p = subparsers.add_parser("attention")
    p.add_argument("--agent", default=None)
    
    # meta
    p = subparsers.add_parser("meta")
    p.add_argument("--tile-id", default=None)
    
    # surprise
    p = subparsers.add_parser("surprise")
    p.add_argument("subcmd", choices=["report", "status"])
    p.add_argument("positional", nargs="*")
    p.add_argument("--domain")
    
    # fflearn
    p = subparsers.add_parser("fflearn")
    p.add_argument("pass_type", choices=["positive", "negative", "status"])
    p.add_argument("--agent", default="oracle1")
    p.add_argument("--experience", default="")
    
    # swarm
    p = subparsers.add_parser("swarm")
    p.add_argument("prompt")
    p.add_argument("--deepinfra-key", default=None)
    
    # reasoner
    p = subparsers.add_parser("reasoner")
    p.add_argument("prompt")
    
    # dashboard
    subparsers.add_parser("dashboard")
    
    # status
    subparsers.add_parser("status")
    
    args = parser.parse_args()
    
    commands = {
        "phi": cmd_phi,
        "attention": cmd_attention,
        "meta": cmd_meta,
        "surprise": cmd_surprise,
        "fflearn": cmd_fflearn,
        "swarm": cmd_swarm,
        "reasoner": cmd_reasoner,
        "dashboard": cmd_dashboard,
        "status": cmd_status,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()