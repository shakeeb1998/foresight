# Deepen brief — ground code-level incidents in real fix commits

Mined incidents describe what went wrong in prose. This pass turns each code-level one into a
**code pattern**: the concrete construct, its silent trap, a bad/good snippet taken from the
actual fix diff, and a grep signature. An agent can then scan a new diff for the same shape.

You get: a JSONL chunk of incidents (`id`, `project`, `date`, `area`, `root_cause`,
`anti_pattern`, `code_shape`, `files`, `evidence`), plus the local repo path(s).

## Hard rules

- **Read-only git.** Allowed: `git -C <repo> log`, `show`, `grep`, `diff`, `blame`.
  Forbidden: checkout, switch, reset, stash, commit, fetch, worktree, and any command that
  writes. Other sessions are working in these repos.
- Spend at most about 3 minutes per incident. If the fix commit can't be found, derive the
  pattern from the incident text alone and set `grounded: false`.
- Never copy secrets, customer names, or data values into snippets. Rename identifiers that
  expose a customer.

## Finding the fix commit

Work through these in order, and stop at the first confident hit:

1. `git -C <repo> log --all --since=<date-3d> --until=<date+7d> --format='%h %ad %s' --date=short -- <files>`
2. `git -C <repo> log --all --since=<date-3d> --until=<date+7d> -i --grep='<2-3 keywords from area/root_cause>'`
3. `git -C <repo> log --all -S'<distinctive identifier from code_shape/root_cause>' --since=<date-10d>`

Confirm the hit with `git show <sha> -- <file>`: the diff must actually change the construct
the incident describes.

## Output (JSONL, one line per incident)

- `id`: the incident id.
- `grounded`: `true` when it came from a real diff, `false` when it came from text.
- `commit`: short sha, or "". This stays local and is never published.
- `framework`: e.g. `django-orm`, `drf`, `react`, `rtk-query`, `react-native`, `expo`,
  `flutter`, `playwright`, `celery`, `postgres`.
- `construct`: the exact API or language construct, e.g. `QuerySet.bulk_update()`,
  `SerializerMethodField + .values_list()`, `useState(initialFromAsyncHook)`,
  `Count() x2 over reverse FKs`, `FloatField for money`.
- `trap`: one sentence on what the construct silently does that the author didn't expect.
- `bad`: the pre-fix code, 10 lines or fewer, trimmed to the essential shape.
- `good`: the post-fix code, 10 lines or fewer.
- `signature`: a Python regex matched against **added lines of a unified diff**. It flags the
  risky construct in new code. Keep it specific enough that it won't fire on every file, e.g.
  `\.bulk_update\(` or `SerializerMethodField` in serializer files. Use "" if no textual
  signature is possible.
- `signature_scope`: a glob of the files where the signature applies, e.g. `*serializers*.py`,
  `*.tsx`.
- `test_guard`: the concrete test that would have caught it (name and what it asserts).
- `confidence`: `high`, `med` or `low`.

Skip, and write no line for, any incident that turns out not to be code-level after all.

Reply with only: lines written, how many were grounded, and the top 5 constructs.
