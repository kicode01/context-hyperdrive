#!/usr/bin/env python3
"""
intent_amplifier.py - Cognitive Context & Latent Intent Synthesizer
Transforms terse, small user prompts (3-5 words) into mathematically precise,
high-IQ execution briefs by introspecting git status, error logs, and AST symbols.
Bypasses slow, expensive "High Reasoning" token taxes by giving the model explicit focal boundaries.
"""

import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple


class IntentAmplifier:
    """Introspects local project state to enrich short user requests."""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = workspace_path

    def detect_git_context(self) -> Dict[str, List[str]]:
        """Extracts modified, staged, and untracked files."""
        try:
            res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=2
            )
            if res.returncode != 0:
                return {"modified": [], "untracked": []}
            
            modified = []
            untracked = []
            for line in res.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                status = line[:2]
                path = line[3:]
                if "?" in status:
                    untracked.append(path)
                else:
                    modified.append(path)
            return {"modified": modified, "untracked": untracked}
        except Exception:
            return {"modified": [], "untracked": []}

    def amplify_prompt(
        self,
        raw_prompt: str,
        active_file: Optional[str] = None,
        recent_error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Converts short prompts into structured, high-IQ briefs.
        """
        clean_prompt = raw_prompt.strip()
        words = clean_prompt.split()
        is_short_prompt = len(words) <= 7

        git_ctx = self.detect_git_context()
        
        # Extract potential symbols from prompt (e.g. refund, auth, payment, checkout, user)
        extracted_symbols = self._extract_symbols(clean_prompt)
        
        # If active_file wasn't explicitly provided, infer from modified files
        target_file = active_file
        if not target_file and git_ctx["modified"]:
            target_file = git_ctx["modified"][0]

        # Determine cognitive intent category
        intent_category = self._classify_intent(clean_prompt, recent_error)

        # Build high-IQ execution specification
        amplified_spec = {
            "original_prompt": clean_prompt,
            "is_short_prompt": is_short_prompt,
            "intent_category": intent_category,
            "focal_symbols": extracted_symbols,
            "inferred_target_file": target_file or "Auto-detect from AST",
            "active_modifications": git_ctx["modified"][:5],
            "error_context_injected": bool(recent_error),
            "execution_brief": self._build_brief(
                clean_prompt, intent_category, extracted_symbols, target_file, recent_error
            )
        }
        return amplified_spec

    def _extract_symbols(self, text: str) -> List[str]:
        # Matches identifiers or domain terms
        keywords = re.findall(r'[a-zA-Z0-9_]{3,}', text.lower())
        stopwords = {"the", "and", "for", "with", "this", "that", "fix", "make", "can", "you", "does", "please"}
        symbols = [k for k in keywords if k not in stopwords]
        return list(dict.fromkeys(symbols))

    def _classify_intent(self, text: str, error: Optional[str]) -> str:
        t = text.lower()
        if error or any(w in t for w in ["bug", "error", "fail", "broken", "crash", "fix", "regression"]):
            return "BUG_FIX_AND_REGRESSION_PREVENTION"
        elif any(w in t for w in ["optimize", "fast", "speed", "latency", "scale", "performance"]):
            return "PERFORMANCE_OPTIMIZATION"
        elif any(w in t for w in ["test", "verify", "assert", "coverage", "check"]):
            return "VERIFICATION_AND_TEST_SYNTHESIS"
        elif any(w in t for w in ["add", "create", "implement", "build", "new"]):
            return "FEATURE_SYNTHESIS"
        return "GENERAL_CODE_MODIFICATION"

    def _build_brief(
        self,
        raw_prompt: str,
        category: str,
        symbols: List[str],
        target_file: Optional[str],
        error: Optional[str]
    ) -> str:
        lines = [
            f"### HIGH-PRECISION EXECUTION BRIEF (Synthesized from: \"{raw_prompt}\")",
            f"**Objective:** {category.replace('_', ' ').title()}",
            f"**Primary Focal Target(s):** {', '.join(symbols) if symbols else 'Full module context'}",
            f"**Target Source File:** {target_file or 'Discovered dynamically via symbol reference'}",
            "",
            "**Operational Constraints (Bypassing Reasoning Ambiguity):**",
            "1. Focus modifications exclusively on the primary target function; preserve surrounding interfaces.",
            "2. Preserve all existing docstrings, variable type hints, and comments.",
            "3. Enforce mathematical boundary constraints (zero-division, null safety, numeric limits).",
            "4. Emit standard atomic diffs or replacement blocks without tangential refactoring."
        ]

        if error:
            lines.extend([
                "",
                "**Root Cause Telemetry / Error Trace:**",
                f"```text\n{error.strip()}\n```"
            ])

        return "\n".join(lines)


def demo():
    amplifier = IntentAmplifier()
    terse_prompt = "fix refund crash"
    simulated_error = "ValueError: Refund amount cannot exceed original transaction total: $150.00 < $200.00"

    print("=== [DEMO] Intent Amplifier for Small Prompts ===")
    print(f"User Input: \"{terse_prompt}\" (Only 3 words!)\n")
    
    spec = amplifier.amplify_prompt(
        raw_prompt=terse_prompt,
        active_file="services/payment_service.py",
        recent_error=simulated_error
    )

    print("--- Amplified High-IQ Execution Brief ---")
    print(spec["execution_brief"])
    print("\n--- Inferred Metadata ---")
    print(f"Category:     {spec['intent_category']}")
    print(f"Focal Target: {spec['focal_symbols']}")
    print(f"Target File:  {spec['inferred_target_file']}")


if __name__ == "__main__":
    demo()
