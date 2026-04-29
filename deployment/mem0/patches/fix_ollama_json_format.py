"""Fix Ollama LLM JSON format for thinking models (qwen3.5, etc.)

Problem: Ollama's `format: "json"` conflicts with qwen3.5's thinking mode
(<think>...</think> tags). The thinking output isn't valid JSON, so Ollama's
JSON validation intercepts it and returns empty string.

Fix: Remove `format: "json"` from Ollama params. Instead rely on the prompt
instruction ("Please respond with valid JSON only.") which Mem0 already adds
as a fallback. Most models follow this instruction correctly.
"""

import sys
import os


def patch():
    # Find ollama.py in installed mem0 package
    try:
        import mem0.llms.ollama
        target = os.path.abspath(mem0.llms.ollama.__file__)
    except ImportError:
        print("mem0.llms.ollama not found, skipping")
        return True

    content = open(target).read()

    if "# PATCHED: skip format=json" in content:
        print(f"  {target}: already patched")
        return True

    # Replace the format: "json" line
    old = '''        if response_format and response_format.get("type") == "json_object":
            params["format"] = "json"'''

    new = '''        if response_format and response_format.get("type") == "json_object":
            # PATCHED: skip format=json — conflicts with thinking models (qwen3.5)
            # Rely on prompt instruction instead ("Please respond with valid JSON only.")
            pass'''

    if old not in content:
        print(f"  WARNING: target code not found in {target}")
        return False

    content = content.replace(old, new)
    open(target, "w").write(content)
    print(f"  {target}: patched (removed format=json)")
    return True


if __name__ == "__main__":
    if patch():
        print("Ollama JSON format patch applied.")
    else:
        print("Patch failed.", file=sys.stderr)
        sys.exit(1)
