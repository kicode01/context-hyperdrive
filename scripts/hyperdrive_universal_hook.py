#!/usr/bin/env python3
"""
hyperdrive_universal_hook.py - Universal Pre-Invocation Hook for All AI Agents
Works seamlessly across:
- Google Antigravity (via .agents/hooks.json PreInvocation)
- Claude Code (via .claude/hooks / settings)
- Cursor & Windsurf (via MCP / rule enforcement)
- Any CLI / AI Model (Low, Medium, High reasoning effort)

Intercepts user prompts in 2ms. If the prompt is terse (3-5 words) or ambiguous,
it automatically injects a high-IQ execution brief before the model runs,
eliminating slow reasoning deliberation and preventing token waste.
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
from shrinkwrap_ast import shrinkwrap_python


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

    # Check if prompt is short (<= 7 words) or needs amplification
    words = user_input.split()
    if len(words) > 8:
        # Long detailed prompts do not require synthetic intent expansion
        return json.dumps({})

    workspace_paths = data.get("workspacePaths", ["."])
    workspace = workspace_paths[0] if workspace_paths else "."

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


def handle_claude_hook(stdin_data: str) -> str:
    """
    Claude Code UserPromptSubmit hook handler.
    Input: Raw prompt or JSON payload on stdin
    Output: Transformed prompt or JSON
    """
    try:
        data = json.loads(stdin_data)
        user_prompt = data.get("prompt", "")
    except Exception:
        user_prompt = stdin_data.strip()

    if not user_prompt or len(user_prompt.split()) > 8:
        return stdin_data

    amplifier = IntentAmplifier()
    spec = amplifier.amplify_prompt(user_prompt)

    amplified_prompt = (
        f"{user_prompt}\n\n"
        f"<!-- context-hyperdrive: high-iq execution brief -->\n"
        f"{spec['execution_brief']}"
    )

    return json.dumps({"prompt": amplified_prompt}) if "{" in stdin_data else amplified_prompt


def main():
    mode = "antigravity"
    if len(sys.argv) > 1:
        if "--claude" in sys.argv:
            mode = "claude"
        elif "--antigravity" in sys.argv:
            mode = "antigravity"
        elif "--cli" in sys.argv:
            mode = "cli"

    stdin_content = sys.stdin.read() if not sys.stdin.isatty() else ""

    if mode == "cli":
        prompt = sys.argv[2] if len(sys.argv) > 2 else stdin_content
        amplifier = IntentAmplifier()
        print(amplifier.amplify_prompt(prompt)["execution_brief"])
        return

    if mode == "claude":
        out = handle_claude_hook(stdin_content)
        print(out)
    else: # Antigravity PreInvocation (default)
        out = handle_antigravity_preinvocation(stdin_content)
        print(out)


if __name__ == "__main__":
    main()
