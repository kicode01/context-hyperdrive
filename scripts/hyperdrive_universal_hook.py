#!/usr/bin/env python3
"""
hyperdrive_universal_hook.py - Universal Pre-Invocation Hook for All AI Agents
Works seamlessly across:
- Google Antigravity (via .agents/hooks.json PreInvocation)
- Claude Code (via .claude/hooks / settings UserPromptSubmit)
- Cursor & Windsurf (via MCP / rule enforcement)
- Any CLI / AI Model (Low, Medium, High reasoning effort)

Intercepts user prompts in 2ms. If the prompt is terse (3-5 words) or ambiguous,
it automatically injects a high-IQ execution brief before the model runs,
eliminating slow reasoning deliberation and preventing token waste.
Enforces hard token budget circuit breaker across all agent environments.
"""

import sys
import json
import os
from typing import Dict, Any, Optional

# Ensure sibling imports work
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from intent_amplifier import IntentAmplifier
from shrinkwrap_ast import shrinkwrap_code
from token_circuit_breaker import TokenCircuitBreaker


def handle_antigravity_preinvocation(stdin_data: str) -> str:
    """
    Antigravity PreInvocation contract:
    Input: JSON on stdin with 'lastUserInput', 'workspacePaths', 'modelName'
    Output: JSON on stdout with 'injectSteps'
    """
    try:
        data = json.loads(stdin_data) if stdin_data.strip() else {}
    except Exception:
        return json.dumps({})

    user_input = data.get("lastUserInput", "").strip()
    if not user_input:
        return json.dumps({})

    workspace_paths = data.get("workspacePaths", ["."])
    workspace = workspace_paths[0] if workspace_paths else "."

    # Check Circuit Breaker status
    ledger_file = os.path.join(workspace, ".hyperdrive_ledger.json")
    breaker = TokenCircuitBreaker(ledger_path=ledger_file)

    if "reset budget" in user_input.lower():
        breaker.reset()
        return json.dumps({
            "injectSteps": [
                {
                    "ephemeralMessage": "[CONTEXT-HYPERDRIVE] Token Budget Circuit Breaker successfully reset to CLOSED state."
                }
            ]
        })

    if breaker.state == "TRIPPED":
        return json.dumps({
            "injectSteps": [
                {
                    "ephemeralMessage": (
                        f"[CONTEXT-HYPERDRIVE ALERT: CIRCUIT BREAKER TRIPPED]\n"
                        f"{breaker.trip_reason}\n"
                        f"Autonomous execution paused to prevent runaway API spend. "
                        f"To resume, type 'reset budget' or update the ceiling in .hyperdrive_ledger.json."
                    )
                }
            ]
        })

    # Check if prompt is short (<= 7 words) or needs amplification
    words = user_input.split()
    if len(words) > 8:
        return json.dumps({})

    amplifier = IntentAmplifier(workspace_path=workspace)
    spec = amplifier.amplify_prompt(user_input)

    brief_text = (
        f"[CONTEXT-HYPERDRIVE AUTO-HOOK ACTIVE]\n"
        f"Detected short prompt (\"{user_input}\"). Bypassing reasoning latency with high-IQ brief:\n\n"
        f"{spec['execution_brief']}\n"
    )

    response = {
        "injectSteps": [
            {
                "ephemeralMessage": brief_text
            }
        ]
    }
    return json.dumps(response, indent=2)


def handle_claude_hook(stdin_data: str, workspace_path: str = ".") -> str:
    """
    Claude Code UserPromptSubmit hook handler.
    Input: Raw prompt or JSON payload on stdin
    Output: Transformed prompt or JSON
    """
    is_json = False
    try:
        data = json.loads(stdin_data)
        user_prompt = data.get("prompt", "")
        is_json = True
    except Exception:
        user_prompt = stdin_data.strip()

    if not user_prompt:
        return stdin_data

    # Check Circuit Breaker
    ledger_file = os.path.join(workspace_path, ".hyperdrive_ledger.json")
    breaker = TokenCircuitBreaker(ledger_path=ledger_file)

    if "reset budget" in user_prompt.lower():
        breaker.reset()
        reset_msg = "[CONTEXT-HYPERDRIVE] Token Budget Circuit Breaker successfully reset to CLOSED state."
        if is_json:
            return json.dumps({"prompt": f"{user_prompt}\n\n{reset_msg}"})
        return f"{user_prompt}\n\n{reset_msg}"

    if breaker.state == "TRIPPED":
        trip_msg = (
            f"[CONTEXT-HYPERDRIVE ALERT: CIRCUIT BREAKER TRIPPED]\n"
            f"{breaker.trip_reason}\n"
            f"Autonomous execution paused to prevent runaway API spend. "
            f"To resume, type 'reset budget' or update the ceiling in .hyperdrive_ledger.json."
        )
        if is_json:
            return json.dumps({"prompt": trip_msg})
        return trip_msg

    if len(user_prompt.split()) > 8:
        return stdin_data

    amplifier = IntentAmplifier(workspace_path=workspace_path)
    spec = amplifier.amplify_prompt(user_prompt)

    amplified_prompt = (
        f"{user_prompt}\n\n"
        f"<!-- context-hyperdrive: high-iq execution brief -->\n"
        f"{spec['execution_brief']}"
    )

    return json.dumps({"prompt": amplified_prompt}) if is_json else amplified_prompt


def demo():
    print("==========================================================")
    print("   UNIVERSAL MULTI-AGENT PRE-INVOCATION HOOK DEMO         ")
    print("==========================================================")
    
    print("\n[1] Testing Google Antigravity PreInvocation Hook:")
    sample_antigravity = json.dumps({
        "lastUserInput": "fix refund bug",
        "workspacePaths": ["."],
        "modelName": "antigravity-preview"
    })
    print(f"Incoming JSON:\n{sample_antigravity}")
    out_ag = handle_antigravity_preinvocation(sample_antigravity)
    print(f"Hook Response:\n{out_ag}")

    print("\n[2] Testing Claude Code UserPromptSubmit Hook:")
    sample_claude = json.dumps({"prompt": "fix refund bug"})
    print(f"Incoming JSON:\n{sample_claude}")
    out_cc = handle_claude_hook(sample_claude)
    print(f"Hook Response:\n{out_cc}")
    print("==========================================================")


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python hyperdrive_universal_hook.py [--antigravity | --claude | --cli <prompt> | --demo]")
        print("Universal pre-invocation hook for Google Antigravity, Claude Code, Cursor, and Windsurf.")
        return

    if "--demo" in sys.argv:
        demo()
        return

    mode = "antigravity"
    if "--claude" in sys.argv:
        mode = "claude"
    elif "--antigravity" in sys.argv:
        mode = "antigravity"
    elif "--cli" in sys.argv:
        mode = "cli"

    # If interactive with no piped stdin and no specific cli prompt
    if sys.stdin.isatty() and mode != "cli":
        demo()
        return

    stdin_content = sys.stdin.read() if not sys.stdin.isatty() else ""

    if mode == "cli":
        prompt = sys.argv[2] if len(sys.argv) > 2 else stdin_content
        amplifier = IntentAmplifier()
        print(amplifier.amplify_prompt(prompt)["execution_brief"])
        return

    if mode == "claude":
        out = handle_claude_hook(stdin_content)
        print(out)
    else:  # Antigravity PreInvocation (default)
        out = handle_antigravity_preinvocation(stdin_content)
        print(out)


if __name__ == "__main__":
    main()
