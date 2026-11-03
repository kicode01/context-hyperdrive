#!/usr/bin/env python3
"""
token_circuit_breaker.py - Hard Token Budget & Runaway Agent Circuit Breaker
Protects developers from runaway agent loops and unexpected API bills by enforcing
deterministic ceilings on token spend ($USD), total context tokens, and loop iterations.

States:
- CLOSED: Normal operation; spend is below the threshold.
- TRIPPED: Budget ceiling reached; interrupts agent execution and requires manual authorization.
- RESET: Ceiling raised or acknowledged by developer.
"""

import json
import os
import sys
import time
from typing import Dict, Any, Tuple, Optional


class TokenCircuitBreaker:
    """Monitors token consumption and trips a hard interrupt upon budget breach."""

    # Default pricing models (Anthropic Claude 3.5 / Gemini 2.5 average rates per 1M tokens)
    DEFAULT_PRICING = {
        "input_standard": 3.00,   # $3.00 / 1M tokens
        "input_cached": 0.30,     # $0.30 / 1M tokens (90% discount)
        "output": 15.00           # $15.00 / 1M tokens
    }

    def __init__(
        self,
        max_budget_usd: float = 0.50,
        max_total_tokens: int = 150_000,
        max_turns: int = 15,
        ledger_path: Optional[str] = None
    ):
        self.max_budget_usd = max_budget_usd
        self.max_total_tokens = max_total_tokens
        self.max_turns = max_turns
        self.ledger_path = ledger_path

        self.total_input_tokens = 0
        self.total_cached_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
        self.turn_count = 0
        self.state = "CLOSED"  # CLOSED, TRIPPED
        self.trip_reason: Optional[str] = None

        if self.ledger_path and os.path.exists(self.ledger_path):
            self._load_ledger()

    def _load_ledger(self):
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.total_input_tokens = data.get("total_input_tokens", 0)
                self.total_cached_tokens = data.get("total_cached_tokens", 0)
                self.total_output_tokens = data.get("total_output_tokens", 0)
                self.total_cost_usd = data.get("total_cost_usd", 0.0)
                self.turn_count = data.get("turn_count", 0)
                self.state = data.get("state", "CLOSED")
                self.trip_reason = data.get("trip_reason", None)
        except Exception:
            pass

    def _save_ledger(self):
        if not self.ledger_path:
            return
        try:
            data = {
                "max_budget_usd": self.max_budget_usd,
                "max_total_tokens": self.max_total_tokens,
                "max_turns": self.max_turns,
                "total_input_tokens": self.total_input_tokens,
                "total_cached_tokens": self.total_cached_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_cost_usd": round(self.total_cost_usd, 6),
                "turn_count": self.turn_count,
                "state": self.state,
                "trip_reason": self.trip_reason,
                "last_updated": time.time()
            }
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def calculate_cost(self, input_tokens: int, output_tokens: int, cached_tokens: int = 0) -> float:
        """Calculates cost in USD according to standard vs cached token tiers."""
        uncached_input = max(0, input_tokens - cached_tokens)
        cost_uncached = (uncached_input / 1_000_000.0) * self.DEFAULT_PRICING["input_standard"]
        cost_cached = (cached_tokens / 1_000_000.0) * self.DEFAULT_PRICING["input_cached"]
        cost_output = (output_tokens / 1_000_000.0) * self.DEFAULT_PRICING["output"]
        return cost_uncached + cost_cached + cost_output

    def record_turn(
        self,
        input_tokens: int,
        output_tokens: int = 0,
        cached_tokens: int = 0
    ) -> Dict[str, Any]:
        """
        Records an invocation turn and checks for ceiling breaches.
        """
        if self.state == "TRIPPED":
            return self.get_status()

        turn_cost = self.calculate_cost(input_tokens, output_tokens, cached_tokens)
        self.total_input_tokens += input_tokens
        self.total_cached_tokens += cached_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += turn_cost
        self.turn_count += 1

        # Check breach conditions
        total_tokens = self.total_input_tokens + self.total_output_tokens

        if self.total_cost_usd >= self.max_budget_usd:
            self.state = "TRIPPED"
            self.trip_reason = f"Budget ceiling reached: ${self.total_cost_usd:.4f} spent (Max allowed: ${self.max_budget_usd:.2f})"
        elif total_tokens >= self.max_total_tokens:
            self.state = "TRIPPED"
            self.trip_reason = f"Token volume ceiling reached: {total_tokens:,} tokens consumed (Max allowed: {self.max_total_tokens:,})"
        elif self.turn_count >= self.max_turns:
            self.state = "TRIPPED"
            self.trip_reason = f"Loop iteration limit reached: {self.turn_count} turns executed without resolution (Max allowed: {self.max_turns})"

        self._save_ledger()
        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        """Returns the current state and telemetry of the circuit breaker."""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        return {
            "state": self.state,
            "is_tripped": self.state == "TRIPPED",
            "trip_reason": self.trip_reason,
            "turn_count": self.turn_count,
            "max_turns": self.max_turns,
            "total_tokens": total_tokens,
            "max_total_tokens": self.max_total_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "max_budget_usd": self.max_budget_usd,
            "budget_used_pct": round(min(100.0, (self.total_cost_usd / self.max_budget_usd) * 100.0), 2)
        }

    def reset(self, new_budget_usd: Optional[float] = None, new_max_turns: Optional[int] = None):
        """Resets a tripped breaker and optionally extends budget."""
        if new_budget_usd:
            self.max_budget_usd = new_budget_usd
        if new_max_turns:
            self.max_turns = new_max_turns
        self.state = "CLOSED"
        self.trip_reason = None
        self._save_ledger()


def demo():
    print("=== [DEMO] Hard Token Budget Circuit Breaker ===")
    print("Setting budget ceiling: $0.05 USD | Max turns: 4")

    breaker = TokenCircuitBreaker(max_budget_usd=0.05, max_turns=4)

    # Turn 1: Normal initial query
    print("\n--- Turn 1: Initial Prompt ---")
    st = breaker.record_turn(input_tokens=2500, output_tokens=300, cached_tokens=0)
    print(f"State: {st['state']} | Cost: ${st['total_cost_usd']} ({st['budget_used_pct']}% of limit)")

    # Turn 2: Cached turn
    print("\n--- Turn 2: Cached Follow-Up ---")
    st = breaker.record_turn(input_tokens=3000, output_tokens=400, cached_tokens=2500)
    print(f"State: {st['state']} | Cost: ${st['total_cost_usd']} ({st['budget_used_pct']}% of limit)")

    # Turn 3: Large file dump (pushes cost over $0.05)
    print("\n--- Turn 3: Large File Dump & Tool Call ---")
    st = breaker.record_turn(input_tokens=15000, output_tokens=1200, cached_tokens=0)
    print(f"State: {st['state']} | Cost: ${st['total_cost_usd']} ({st['budget_used_pct']}% of limit)")

    if st['is_tripped']:
        print("\n[!] CIRCUIT BREAKER TRIPPED! [!]")
        print(f"Reason: {st['trip_reason']}")
        print("Halting autonomous execution to prevent runaway billing.")

    # Turn 4: Attempted execution while tripped
    print("\n--- Turn 4: Blocked Execution Attempt ---")
    st = breaker.record_turn(input_tokens=5000, output_tokens=500)
    print(f"Call blocked! State remains: {st['state']}")

    # Reset with expanded ceiling
    print("\n--- Developer Authorizes Extension ($0.20) ---")
    breaker.reset(new_budget_usd=0.20)
    print(f"Breaker reset! New State: {breaker.state} | Max Budget: ${breaker.max_budget_usd}")


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python token_circuit_breaker.py [--status] [--reset [amount]] [--demo]")
        print("Monitors agent spend, total token limits, and trips on ceiling breaches.")
    elif "--status" in sys.argv:
        breaker = TokenCircuitBreaker(ledger_path=".hyperdrive_ledger.json")
        print(json.dumps(breaker.get_status(), indent=2))
    elif "--reset" in sys.argv:
        breaker = TokenCircuitBreaker(ledger_path=".hyperdrive_ledger.json")
        idx = sys.argv.index("--reset")
        new_b = float(sys.argv[idx + 1]) if len(sys.argv) > idx + 1 else None
        breaker.reset(new_budget_usd=new_b)
        print(f"Breaker reset to CLOSED. New Budget: ${breaker.max_budget_usd}")
    else:
        demo()
