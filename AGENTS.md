# Decision Matrix AI: owner-approved development workflow

The owner approved this workflow on 2026-09-03.

- Inspect the current branch, git status and remotes before work. Preserve
  unrelated and unfinished user changes. Never include secrets, .env files,
  temporary databases or transferred patch/ZIP files in commits.
- Create and use separate `codex/*` working branches. The assistant may commit
  and publish task-related changes to these branches without another approval.
  Prefer this workflow over asking the owner to transfer patches manually.
- Do not commit or push to `main`, merge a pull request, enable auto-merge,
  promote a deployment to Production, or migrate the Production database
  without the owner's separate, explicit approval. Favicon selection and
  approval of a development branch are NOT release approval.
- Before publishing a working branch, inspect deployment triggers. Do not let
  a branch push inadvertently deploy Production or start a Preview against
  the Production database. If environment isolation cannot be verified, keep
  automatic deployment disabled for that working branch.
- The current `vercel.json` disables Git-triggered Vercel deployments only for
  `codex/preview-reliability-favicon`. It is not a repository branch-protection
  rule and does not change the existing Production branch configuration.
- Prepare and start an isolated Preview when available tools permit it. Be
  explicit when there is no access to the owner's Codespaces terminal. Do not
  claim that a preview URL exists until the process and URL are verified.
- Local synthetic Preview: `python -m scripts.preview_mock_server`. This makes
  a fresh temporary SQLite database and mock model responses, with no real
  MWS/email/analytics calls. In Codespaces keep the forwarded port Private.
  Never expose the synthetic demo publicly or use real user data in it.
- Keep authorization, email verification, CSRF, AI rate limits, the 100 RUB
  daily safeguard and analytics consent intact. No real monetization paywall.
- Run tests with isolated database settings and mocked paid providers. Clearly
  distinguish HTTP/DOM tests from real-browser and real-MWS checks.
- After Preview review, report the exact branch/commit and working-tree state.
  Await separate release approval before merging or deploying.
