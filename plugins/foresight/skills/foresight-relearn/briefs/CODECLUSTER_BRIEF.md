# Code-cluster brief - construct records → code-pattern nodes

This step turns the output of the deepen pass into **code patterns**. You get one JSONL line per
incident, each with construct, trap, bad/good snippets and signature. Group them into
concrete, framework-level traps that an agent can recognise in a diff.

## Rules

- **Group by construct + trap**, not by feature. "`bulk_update()` skips `save()`/signals" is
  one pattern no matter which model it hit. The same construct with a *different* trap is a
  different pattern, e.g. `bulk_update()` skipping signals vs. `bulk_update()` omitting
  `updated_at`.
- Keep a pattern even if it was seen only once, when it is grounded (`grounded: true`) and
  its signature is specific. Otherwise drop singletons whose `confidence` is `low`.
- Pick the **best** bad/good pair from the group: short, grounded, and with no customer
  identifiers. Rewrite identifiers to neutral names (`Invoice`, `Order`, `amount`).
- **Signature quality:**
  1. Test each candidate regex mentally against the good snippet. It must not match the
     fix, or it must match only with a clearly different scope.
  2. Prefer anchors on the risky call, e.g. `\.bulk_(update|create)\(`,
     `\buseState\(\s*\w+(Query|Data)\b`, `\.values_list\(`.
  3. Leave `signature` empty rather than ship one that fires on most files.
- `parents`: the FS mechanism id(s) the member incidents were clustered under. They come in
  as `fs` on each input line.
- Ids: `CP-nn` when told `canonical: true`, otherwise `CPL-<kebab-name>`. In incremental
  mode, keep existing ids and append members.

## Output - `code_patterns.json`

```json
{
  "patterns": {
    "CP-01": {
      "title": "bulk_update() skips save() and pre_save signals",
      "framework": "django-orm",
      "construct": "QuerySet.bulk_update()",
      "trap": "No save() and no signals run, so derived fields and signal-driven side effects silently go stale.",
      "bad": "...",
      "good": "...",
      "signature": "\\.bulk_update\\(",
      "signature_scope": "*.py",
      "test_guard": "after bulk path, assert derived field / signal side effect equals single-save path",
      "parents": ["FS-07"],
      "portable": true,
      "members": ["I0123", "I0456"]
    }
  }
}
```

Reply with only: the pattern count, how many have signatures, and your top 10 by member count.
