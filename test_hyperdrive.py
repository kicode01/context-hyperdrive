#!/usr/bin/env python3
"""
test_hyperdrive.py - Standalone Verification & Unit Test Suite for context-hyperdrive
Tests all 7 hyperdrive engines and lifecycle hooks:
1. Multi-Language AST Shrinkwrap (Python, TS/TSX, Go, Rust)
2. Prompt Cache Aligner (Prefix pinning & 90% discount)
3. Intent Amplifier (Terse prompt expansion & cognitive priming)
4. Terminal Log Quantizer (Noise stripping & stack trace folding)
5. Git Diff Compactor (Lockfile exclusion & hunk summarization)
6. Token Budget Circuit Breaker (Ceiling enforcement & FSM)
7. History Compactor (Rolling window & state snapshot)
8. Universal Multi-Agent Hook (Antigravity & Claude Code pre-invocation)
"""

import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from shrinkwrap_ast import shrinkwrap_python, shrinkwrap_code, shrinkwrap_typescript, shrinkwrap_golang, shrinkwrap_rust
from cache_aligner import PromptCacheAligner
from intent_amplifier import IntentAmplifier
from log_quantizer import TerminalLogQuantizer
from diff_compactor import GitDiffCompactor
from token_circuit_breaker import TokenCircuitBreaker
from history_compactor import HistoryCompactor
from hyperdrive_pipeline import ContextHyperdrivePipeline
from hyperdrive_universal_hook import handle_antigravity_preinvocation, handle_claude_hook


class TestStandaloneHyperdrive(unittest.TestCase):

    def test_1_shrinkwrap_python(self):
        source = """
class DataService:
    def helper_one(self):
        x = 100
        return x * 2

    def target_method(self, val: int):
        return val + 42

    def helper_two(self):
        y = 200
        return y * 3
"""
        shrinkwrapped, stats = shrinkwrap_python(source, ["target_method"])
        self.assertIn("target_method", shrinkwrapped)
        self.assertIn("return val + 42", shrinkwrapped)
        self.assertIn("pass", shrinkwrapped)
        self.assertGreater(stats["tokens_saved"], 0)

    def test_2_shrinkwrap_typescript_tsx(self):
        ts = """
export const CheckoutView: React.FC = () => {
    const computeTax = () => { return 10; };
    const handleRefund = async (id: string) => {
        return "REFUND_PROCESSED";
    };
    return <div>{handleRefund('123')}</div>;
};
"""
        out, stats = shrinkwrap_code(ts, ["handleRefund"], "checkout.tsx")
        self.assertIn("handleRefund", out)
        self.assertIn("REFUND_PROCESSED", out)
        self.assertIn("pruned: computeTax", out)
        self.assertEqual(stats["language"], "typescript")

    def test_3_shrinkwrap_go_and_rust(self):
        go_code = """
package ledger
func UnusedHelper() int { return 1 }
func ProcessLedger() bool { return true }
"""
        go_out, go_stats = shrinkwrap_code(go_code, ["ProcessLedger"], "ledger.go")
        self.assertIn("ProcessLedger", go_out)
        self.assertIn("pruned: UnusedHelper", go_out)
        self.assertEqual(go_stats["language"], "golang")

        rust_code = """
impl Processor {
    fn unused(&self) -> u32 { 42 }
    pub fn process_tx(&self) -> bool { true }
}
"""
        rs_out, rs_stats = shrinkwrap_code(rust_code, ["process_tx"], "lib.rs")
        self.assertIn("process_tx", rs_out)
        self.assertIn("pruned: unused", rs_out)
        self.assertEqual(rs_stats["language"], "rust")

    def test_4_cache_aligner_pins_prefix(self):
        system = "You are an autonomous engineering assistant."
        tools = [{"name": "patch_ast", "description": "Apply patch"}]
        rules = ["Rule A", "Rule B"]

        aligner1 = PromptCacheAligner(system, tools, rules)
        aligner2 = PromptCacheAligner(system, tools, rules)
        self.assertEqual(aligner1.prefix_hash, aligner2.prefix_hash)

        payload = aligner1.assemble_payload("dynamic turn")
        self.assertIn("cost_savings_pct", payload)
        self.assertGreater(payload["cost_savings_pct"], 0)

    def test_5_intent_amplifier_short_prompts(self):
        amplifier = IntentAmplifier(workspace_path=BASE_DIR)
        res = amplifier.amplify_prompt("fix refund crash", recent_error="ValueError: Invalid")
        self.assertTrue(res["is_short_prompt"])
        self.assertEqual(res["intent_category"], "BUG_FIX_AND_REGRESSION_PREVENTION")
        self.assertIn("refund", res["focal_symbols"])
        self.assertIn("HIGH-PRECISION EXECUTION BRIEF", res["execution_brief"])

    def test_6_log_quantizer_collapses_noise(self):
        log = """
test_one PASSED
test_two PASSED
test_three PASSED
test_four PASSED
Warning: Deprecated API
Warning: Deprecated API
Warning: Deprecated API
Traceback (most recent call last):
  File "/usr/lib/python3.11/site-packages/pytest/runner.py", line 10, in run
    result = fn()
  File "/workspace/app/main.py", line 42, in my_func
    raise ZeroDivisionError("division by zero")
ZeroDivisionError: division by zero
"""
        quantizer = TerminalLogQuantizer()
        quantized, metrics = quantizer.quantize(log)
        self.assertIn("passing tests collapsed", quantized)
        self.assertIn("internal library frames collapsed", quantized)
        self.assertIn("division by zero", quantized)
        self.assertGreater(metrics["tokens_saved"], 0)

    def test_7_diff_compactor_filters_lockfiles(self):
        diff = """diff --git a/package-lock.json b/package-lock.json
index 111..222 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,5 +1,5 @@
-version = 1
+version = 2
diff --git a/src/main.py b/src/main.py
index 333..444 100644
--- a/src/main.py
+++ b/src/main.py
@@ -10,3 +10,3 @@ def calculate():
-    return 1
+    return 2
"""
        compactor = GitDiffCompactor()
        compacted, metrics = compactor.compact_diff(diff)
        self.assertIn("Excluded Lockfile / Generated", compacted)
        self.assertIn("package-lock.json", compacted)
        self.assertIn("File: src/main.py", compacted)
        self.assertIn("return 2", compacted)
        self.assertGreater(metrics["tokens_saved"], 0)

    def test_8_token_circuit_breaker(self):
        breaker = TokenCircuitBreaker(max_budget_usd=0.05, max_turns=3)
        self.assertEqual(breaker.state, "CLOSED")

        # Record normal turn
        breaker.record_turn(input_tokens=1000, output_tokens=100)
        self.assertEqual(breaker.state, "CLOSED")

        # Exceed budget
        breaker.record_turn(input_tokens=25000, output_tokens=1000)
        self.assertEqual(breaker.state, "TRIPPED")

        # Blocked call
        st = breaker.record_turn(input_tokens=500)
        self.assertEqual(st["state"], "TRIPPED")

        # Reset
        breaker.reset(new_budget_usd=1.00)
        self.assertEqual(breaker.state, "CLOSED")

    def test_9_history_compactor(self):
        chat = [
            {"role": "user", "content": "Create src/server.py"},
            {"role": "assistant", "content": "Created src/server.py"},
            {"role": "user", "content": "We decided to use port 8080"},
            {"role": "assistant", "content": "Updated port in src/server.py"},
            {"role": "user", "content": "Active request 1"},
            {"role": "assistant", "content": "Active response 1"}
        ]
        compactor = HistoryCompactor(active_window_turns=2)
        compacted, metrics = compactor.compact_history(chat)
        self.assertTrue(metrics["compaction_performed"])
        self.assertEqual(len(compacted), 4)
        self.assertIn("COMPACTED SESSION STATE SNAPSHOT", compacted[0]["content"])
        self.assertEqual(compacted[2]["content"], "Active request 1")

    def test_10_hyperdrive_pipeline(self):
        pipeline = ContextHyperdrivePipeline(
            system_prompt="Guidelines for code agent",
            tools=[{"name": "test", "description": "run test"}],
            rules=["Rule A"]
        )
        res = pipeline.process(
            raw_prompt="fix target func",
            source_code="def helper(): pass\ndef target_func(): return 42\n"
        )
        self.assertIn("intent_summary", res)
        self.assertIn("shrinkwrap_summary", res)
        self.assertIn("economics", res)
        self.assertGreater(res["economics"]["total_savings_pct"], 0)

    def test_11_universal_hook_antigravity(self):
        input_json = json.dumps({"lastUserInput": "fix refund bug", "workspacePaths": [BASE_DIR]})
        out = handle_antigravity_preinvocation(input_json)
        data = json.loads(out)
        self.assertIn("injectSteps", data)
        self.assertIn("CONTEXT-HYPERDRIVE AUTO-HOOK ACTIVE", data["injectSteps"][0]["ephemeralMessage"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
