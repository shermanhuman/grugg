#!/usr/bin/env python3
"""Benchmark grugg vs normal LLM output token counts.

Supports multiple providers: Gemini (Google), OpenAI, and Anthropic.
Auto-detects provider from available API keys, or use --provider flag.
"""

import argparse
import hashlib
import json
import os
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Load .env.local from repo root if it exists
_env_file = Path(__file__).parent.parent / ".env.local"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

SCRIPT_VERSION = "2.0.0"
SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent
PROMPTS_PATH = SCRIPT_DIR / "prompts.json"
SKILL_PATH = REPO_DIR / "skills" / "grugg" / "SKILL.md"
RESULTS_DIR = SCRIPT_DIR / "results"

NORMAL_SYSTEM = "You are a helpful assistant."

# Default models per provider
DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-20250514",
}


# --- Provider abstraction ---

class GeminiProvider:
    """Google Gemini via google-genai SDK."""

    def __init__(self):
        try:
            from google import genai
        except ImportError:
            print("ERROR: google-genai package not installed.", file=sys.stderr)
            print("  pip install google-genai", file=sys.stderr)
            sys.exit(1)
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("ERROR: GOOGLE_API_KEY or GEMINI_API_KEY not set.", file=sys.stderr)
            sys.exit(1)
        self.client = genai.Client(api_key=api_key)
        self.genai = genai

    def call(self, model, system, prompt, max_retries=3):
        from google.genai import types
        delays = [5, 10, 20]
        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        temperature=0,
                        max_output_tokens=4096,
                    ),
                )
                usage = response.usage_metadata
                return {
                    "input_tokens": usage.prompt_token_count or 0,
                    "output_tokens": usage.candidates_token_count or 0,
                    "text": response.text or "",
                    "stop_reason": "stop",
                }
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < max_retries:
                        delay = delays[min(attempt, len(delays) - 1)]
                        print(f"  Rate limited, retrying in {delay}s...", file=sys.stderr)
                        time.sleep(delay)
                    else:
                        raise
                else:
                    raise


class OpenAIProvider:
    """OpenAI via openai SDK."""

    def __init__(self):
        try:
            from openai import OpenAI
        except ImportError:
            print("ERROR: openai package not installed.", file=sys.stderr)
            print("  pip install openai", file=sys.stderr)
            sys.exit(1)
        if not os.environ.get("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not set.", file=sys.stderr)
            sys.exit(1)
        self.client = OpenAI()

    def call(self, model, system, prompt, max_retries=3):
        import openai
        delays = [5, 10, 20]
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    max_tokens=4096,
                    temperature=0,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                )
                usage = response.usage
                return {
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "text": response.choices[0].message.content or "",
                    "stop_reason": response.choices[0].finish_reason,
                }
            except openai.RateLimitError:
                if attempt < max_retries:
                    delay = delays[min(attempt, len(delays) - 1)]
                    print(f"  Rate limited, retrying in {delay}s...", file=sys.stderr)
                    time.sleep(delay)
                else:
                    raise


class AnthropicProvider:
    """Anthropic via anthropic SDK."""

    def __init__(self):
        try:
            import anthropic
        except ImportError:
            print("ERROR: anthropic package not installed.", file=sys.stderr)
            print("  pip install anthropic", file=sys.stderr)
            sys.exit(1)
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
            sys.exit(1)
        self.client = anthropic.Anthropic()
        self._anthropic = anthropic

    def call(self, model, system, prompt, max_retries=3):
        delays = [5, 10, 20]
        for attempt in range(max_retries + 1):
            try:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=4096,
                    temperature=0,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )
                return {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "text": response.content[0].text,
                    "stop_reason": response.stop_reason,
                }
            except self._anthropic.RateLimitError:
                if attempt < max_retries:
                    delay = delays[min(attempt, len(delays) - 1)]
                    print(f"  Rate limited, retrying in {delay}s...", file=sys.stderr)
                    time.sleep(delay)
                else:
                    raise


PROVIDERS = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}


def detect_provider():
    """Auto-detect provider from available API keys."""
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return None


# --- Benchmark logic ---

def load_prompts():
    with open(PROMPTS_PATH) as f:
        data = json.load(f)
    return data["prompts"]


def load_grugg_system():
    return SKILL_PATH.read_text()


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_benchmarks(provider, model, prompts, grugg_system, trials):
    results = []
    total = len(prompts)

    for i, prompt_entry in enumerate(prompts, 1):
        pid = prompt_entry["id"]
        prompt_text = prompt_entry["prompt"]
        entry = {
            "id": pid,
            "category": prompt_entry["category"],
            "prompt": prompt_text,
            "normal": [],
            "grugg": [],
        }

        for mode, system in [("normal", NORMAL_SYSTEM), ("grugg", grugg_system)]:
            for t in range(1, trials + 1):
                print(
                    f"  [{i}/{total}] {pid} | {mode} | trial {t}/{trials}",
                    file=sys.stderr,
                )
                result = provider.call(model, system, prompt_text)
                entry[mode].append(result)
                time.sleep(0.5)

        results.append(entry)

    return results


def compute_stats(results):
    rows = []
    all_savings = []

    for entry in results:
        normal_medians = statistics.median(
            [t["output_tokens"] for t in entry["normal"]]
        )
        grugg_medians = statistics.median(
            [t["output_tokens"] for t in entry["grugg"]]
        )
        savings = 1 - (grugg_medians / normal_medians) if normal_medians > 0 else 0
        all_savings.append(savings)

        rows.append(
            {
                "id": entry["id"],
                "category": entry["category"],
                "prompt": entry["prompt"],
                "normal_median": int(normal_medians),
                "grugg_median": int(grugg_medians),
                "savings_pct": round(savings * 100),
            }
        )

    avg_savings = round(statistics.mean(all_savings) * 100)
    min_savings = round(min(all_savings) * 100)
    max_savings = round(max(all_savings) * 100)
    avg_normal = round(statistics.mean([r["normal_median"] for r in rows]))
    avg_grugg = round(statistics.mean([r["grugg_median"] for r in rows]))

    return rows, {
        "avg_savings": avg_savings,
        "min_savings": min_savings,
        "max_savings": max_savings,
        "avg_normal": avg_normal,
        "avg_grugg": avg_grugg,
    }


def format_prompt_label(prompt_id):
    labels = {
        "react-rerender": "Explain React re-render bug",
        "auth-middleware-fix": "Fix auth middleware token expiry",
        "postgres-pool": "Set up PostgreSQL connection pool",
        "git-rebase-merge": "Explain git rebase vs merge",
        "async-refactor": "Refactor callback to async/await",
        "microservices-monolith": "Architecture: microservices vs monolith",
        "pr-security-review": "Review PR for security issues",
        "docker-multi-stage": "Docker multi-stage build",
        "race-condition-debug": "Debug PostgreSQL race condition",
        "error-boundary": "Implement React error boundary",
    }
    return labels.get(prompt_id, prompt_id)


def format_table(rows, summary):
    lines = [
        "| Task | Normal (tokens) | Grugg (tokens) | Saved |",
        "|------|---------------:|----------------:|------:|",
    ]
    for r in rows:
        label = format_prompt_label(r["id"])
        lines.append(
            f"| {label} | {r['normal_median']} | {r['grugg_median']} | {r['savings_pct']}% |"
        )
    lines.append(
        f"| **Average** | **{summary['avg_normal']}** | **{summary['avg_grugg']}** | **{summary['avg_savings']}%** |"
    )
    lines.append("")
    lines.append(
        f"*Range: {summary['min_savings']}%–{summary['max_savings']}% savings across prompts.*"
    )
    return "\n".join(lines)


def save_results(results, rows, summary, provider_name, model, trials, skill_hash):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output = {
        "metadata": {
            "script_version": SCRIPT_VERSION,
            "provider": provider_name,
            "model": model,
            "date": datetime.now(timezone.utc).isoformat(),
            "trials": trials,
            "skill_md_sha256": skill_hash,
        },
        "summary": summary,
        "rows": rows,
        "raw": results,
    }
    path = RESULTS_DIR / f"benchmark_{ts}.json"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    return path


def dry_run(provider_name, model, prompts, trials):
    print(f"Provider: {provider_name}")
    print(f"Model:    {model}")
    print(f"Trials:   {trials}")
    print(f"Prompts:  {len(prompts)}")
    print(f"Total API calls: {len(prompts) * 2 * trials}")
    print()
    for p in prompts:
        print(f"  [{p['id']}] ({p['category']})")
        preview = p["prompt"][:80]
        if len(p["prompt"]) > 80:
            preview += "..."
        print(f"    {preview}")
    print()
    print("Dry run complete. No API calls made.")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark grugg vs normal LLM output tokens",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""providers:
  gemini     Google Gemini (GOOGLE_API_KEY or GEMINI_API_KEY)
  openai     OpenAI (OPENAI_API_KEY)
  anthropic  Anthropic Claude (ANTHROPIC_API_KEY)

Auto-detects provider from available API keys if --provider is not set.
Priority: GOOGLE_API_KEY > OPENAI_API_KEY > ANTHROPIC_API_KEY.""",
    )
    parser.add_argument(
        "--provider", choices=["gemini", "openai", "anthropic"],
        help="LLM provider (auto-detected from API keys if not set)",
    )
    parser.add_argument("--trials", type=int, default=3, help="Trials per prompt per mode (default: 3)")
    parser.add_argument("--dry-run", action="store_true", help="Print config, no API calls")
    parser.add_argument("--model", help="Model to use (default: provider-specific)")
    args = parser.parse_args()

    # Resolve provider
    provider_name = args.provider or detect_provider()
    if not provider_name:
        print("ERROR: No provider detected. Set one of:", file=sys.stderr)
        print("  GOOGLE_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY", file=sys.stderr)
        print("  Or use --provider flag.", file=sys.stderr)
        sys.exit(1)

    model = args.model or DEFAULT_MODELS[provider_name]
    prompts = load_prompts()

    if args.dry_run:
        dry_run(provider_name, model, prompts, args.trials)
        return

    # Initialize provider (lazy import happens here)
    provider = PROVIDERS[provider_name]()

    grugg_system = load_grugg_system()
    skill_hash = sha256_file(SKILL_PATH)

    print(f"Running benchmarks: {len(prompts)} prompts x 2 modes x {args.trials} trials", file=sys.stderr)
    print(f"Provider: {provider_name} | Model: {model}", file=sys.stderr)
    print(file=sys.stderr)

    results = run_benchmarks(provider, model, prompts, grugg_system, args.trials)
    rows, summary = compute_stats(results)
    table_md = format_table(rows, summary)

    json_path = save_results(results, rows, summary, provider_name, model, args.trials, skill_hash)
    print(f"\nResults saved to {json_path}", file=sys.stderr)

    print(table_md)


if __name__ == "__main__":
    main()
