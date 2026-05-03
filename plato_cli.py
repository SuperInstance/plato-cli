#!/usr/bin/env python3
"""
plato-cli — PLATO in one binary
Search tiles, check deadband, navigate rooms, submit tiles.
"""

import sys, json, urllib.request, urllib.error, argparse
from typing import Optional, List, Dict

PLATO_DEFAULT = "http://147.224.38.131:8847"

class PlatoCLI:
    def __init__(self, url: str = PLATO_DEFAULT):
        self.url = url.rstrip('/')
    
    def _get(self, endpoint: str) -> dict:
        try:
            with urllib.request.urlopen(f"{self.url}{endpoint}", timeout=10) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}
    
    def status(self):
        d = self._get("/status")
        if "error" in d:
            print(f"❌ {d['error']}")
            return
        rooms = len(d.get("rooms", {}))
        acc = d.get("gate_stats", {}).get("accepted", 0)
        rej = d.get("gate_stats", {}).get("rejected", 0)
        print(f"PLATO Gate: {d.get('version', 'unknown')}")
        print(f"Rooms: {rooms} | Tiles: {acc:,} accepted, {rej:,} rejected")
    
    def rooms(self, limit: int = 20):
        d = self._get("/status")
        if "error" in d:
            print(f"❌ {d['error']}")
            return
        rooms = sorted(d.get("rooms", {}).items(), key=lambda x: x[1].get("tile_count", 0), reverse=True)
        print(f"{'Room':<30} {'Tiles':<8} {'Created'}")
        print("-" * 60)
        for name, info in rooms[:limit]:
            print(f"{name:<30} {info.get('tile_count', 0):<8} {info.get('created', 'unknown')[:10]}")
    
    def search(self, query: str, room: Optional[str] = None):
        # PLATO gate search endpoint (if available) or basic filter
        d = self._get("/status")
        if "error" in d:
            print(f"❌ {d['error']}")
            return
        rooms = d.get("rooms", {})
        matches = []
        for rname, info in rooms.items():
            if room and rname != room:
                continue
            if query.lower() in rname.lower():
                matches.append((rname, info.get("tile_count", 0)))
        if not matches:
            print(f"No rooms matching '{query}'")
            return
        for name, count in sorted(matches, key=lambda x: x[1], reverse=True):
            print(f"{name}: {count} tiles")
    
    def deadband(self, room: str):
        # Check if room is below deadband threshold
        d = self._get("/status")
        if "error" in d:
            print(f"❌ {d['error']}")
            return
        info = d.get("rooms", {}).get(room)
        if not info:
            print(f"Room '{room}' not found")
            return
        tiles = info.get("tile_count", 0)
        threshold = 5  # typical deadband
        status = "✅ Above deadband" if tiles >= threshold else "⚠️ Below deadband"
        print(f"{room}: {tiles} tiles — {status} (threshold: {threshold})")
    
    def submit(self, question: str, answer: str, agent: str, room: str):
        payload = json.dumps({
            "question": question,
            "answer": answer,
            "agent": agent,
            "room": room
        }).encode()
        req = urllib.request.Request(f"{self.url}/submit", data=payload, headers={
            "Content-Type": "application/json"
        })
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                result = json.loads(r.read().decode())
                print(f"✅ Submitted: {result.get('status', 'ok')}")
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP {e.code}: {e.read().decode()[:200]}")
        except Exception as e:
            print(f"❌ {e}")

def main():
    p = argparse.ArgumentParser(description="PLATO CLI — fleet knowledge operations")
    p.add_argument("--url", default=PLATO_DEFAULT, help="PLATO gate URL")
    sub = p.add_subparsers(dest="cmd")
    
    sub.add_parser("status", help="Show gate status")
    
    rooms_p = sub.add_parser("rooms", help="List rooms by tile count")
    rooms_p.add_argument("-n", type=int, default=20, help="Limit")
    
    search_p = sub.add_parser("search", help="Search rooms")
    search_p.add_argument("query", help="Search term")
    search_p.add_argument("--room", help="Specific room")
    
    dead_p = sub.add_parser("deadband", help="Check room deadband status")
    dead_p.add_argument("room", help="Room name")
    
    submit_p = sub.add_parser("submit", help="Submit a tile")
    submit_p.add_argument("question", help="Question")
    submit_p.add_argument("answer", help="Answer")
    submit_p.add_argument("--agent", default="plato-cli", help="Agent name")
    submit_p.add_argument("--room", required=True, help="Target room")
    
    args = p.parse_args()
    cli = PlatoCLI(args.url)
    
    if args.cmd == "status":
        cli.status()
    elif args.cmd == "rooms":
        cli.rooms(args.n)
    elif args.cmd == "search":
        cli.search(args.query, args.room)
    elif args.cmd == "deadband":
        cli.deadband(args.room)
    elif args.cmd == "submit":
        cli.submit(args.question, args.answer, args.agent, args.room)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
