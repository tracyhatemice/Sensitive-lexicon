#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def read_input_text(args_text: str) -> str:
    if args_text:
        return args_text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def load_vocabulary(vocab_dir: Path) -> dict[str, set[str]]:
    per_file: dict[str, set[str]] = {}
    for txt in sorted(vocab_dir.glob("*.txt")):
        words: set[str] = set()
        with txt.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip()
                if not word:
                    continue
                words.add(word)
        per_file[txt.name] = words
    return per_file


def resolve_vocab_dir(arg_vocab_dir: str) -> Path:
    if arg_vocab_dir:
        p = Path(arg_vocab_dir)
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        return p

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[2]
    candidates = [
        script_dir / "reference",
        repo_root / "Vocabulary",
        (Path.cwd() / "Vocabulary").resolve(),
    ]

    for p in candidates:
        if p.exists() and p.is_dir() and any(p.glob("*.txt")):
            return p

    return candidates[0]


def find_matches(content: str, per_file_words: dict[str, set[str]]) -> dict[str, list[str]]:
    content_lower = content.lower()
    result: dict[str, list[str]] = {}
    for file_name, words in per_file_words.items():
        matched = [w for w in words if w.lower() in content_lower]
        if matched:
            result[file_name] = sorted(set(matched), key=lambda x: (len(x), x))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check whether input text contains any terms from skill reference files "
            "or fallback Vocabulary files"
        )
    )
    parser.add_argument(
        "--text",
        default="",
        help="Input text to check. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--vocab-dir",
        default="",
        help=(
            "Vocabulary directory path. If omitted, auto-detects in order: "
            "skill/reference, repo-root/Vocabulary, cwd/Vocabulary."
        ),
    )
    args = parser.parse_args()

    content = read_input_text(args.text)
    if not content:
        print(
            json.dumps(
                {
                    "hit": False,
                    "total_matches": 0,
                    "matches_by_file": {},
                    "error": "No input text provided. Pass --text or pipe stdin.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    vocab_dir = resolve_vocab_dir(args.vocab_dir)
    if not vocab_dir.exists() or not vocab_dir.is_dir():
        print(
            json.dumps(
                {
                    "hit": False,
                    "total_matches": 0,
                    "matches_by_file": {},
                    "vocab_dir_used": str(vocab_dir),
                    "error": (
                        "Vocabulary directory not found. Provide --vocab-dir, or create "
                        "skill reference directory."
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    per_file_words = load_vocabulary(vocab_dir)
    matches_by_file = find_matches(content, per_file_words)

    unique_terms = set()
    for terms in matches_by_file.values():
        unique_terms.update(terms)

    output = {
        "hit": bool(unique_terms),
        "total_matches": len(unique_terms),
        "vocab_dir_used": str(vocab_dir),
        "matches_by_file": matches_by_file,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
