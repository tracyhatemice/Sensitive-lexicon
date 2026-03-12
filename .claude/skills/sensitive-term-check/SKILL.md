---
name: sensitive-term-check
description: Use this skill when the user asks whether text contains any sensitive, banned, or forbidden terms from reference/*.txt.
---

# Sensitive Term Check Skill

## Purpose

Check whether user-provided text contains any sensitive, banned, or forbidden terms from this skill's reference files.

## When To Use

- The user asks whether a sentence, paragraph, article, title, or message contains sensitive vocabulary.
- The user asks for a quick hit/no-hit check against this skill's vocabulary list.
- The user asks for matched terms and where they came from.

## Inputs

- Required: text content provided by the user.

## Steps

1. Put the user content into stdin and run:

```bash
python3 .claude/skills/sensitive-term-check/check_vocab.py
```

2. Or pass text directly:

```bash
python3 .claude/skills/sensitive-term-check/check_vocab.py --text "<user content>"
```

3. Return a concise summary:
   - Whether there is a hit.
   - Total unique matched terms.
   - Per-file matched terms (if any).

## Vocabulary Source Priority

If `--vocab-dir` is not provided, the script auto-detects vocabulary in this order:

1. `./reference/*.txt`
2. `./Vocabulary/*.txt` at repository root
3. `./Vocabulary/*.txt` in current working directory

## Output Contract

- If no hit:
  - `hit=false`
  - `total_matches=0`
- If hit:
  - `hit=true`
  - `total_matches=<count>`
  - `vocab_dir_used=<path>`
  - `matches_by_file` with source file and matched terms.

## Notes

- Matching is substring-based and case-insensitive for Latin letters.
- Empty lines in vocabulary files are ignored.
- Duplicate words across files are deduplicated per file in output.
