# Guest MVP release — 2026-10-01

Owner explicitly approved implementation and Production release.

## Delivered

- Landing with examples, light grey placeholders (#a1a7ad), black input text,
  and enabled-by-default optional AI suggestions.
- Guest task → understanding check → comparison → optional account save.
- Mandatory conditions are non-compensatory; unknown facts stay unknown.
  User information, model assumptions and missing facts are labelled separately.
- No fixed alternatives/conditions count cap. Comparisons batch both dimensions;
  technical text-size and abuse limits and 100 RUB daily guard remain.
- Results persist through existing login or new registration/email verification
  without repeating model calls. Guest access uses a signed session and hashed
  capability; unsaved data expires after seven days of inactivity.
- Pricing offers paused. Simple consent-only session cohort funnel at /admin;
  existing technical statistics and feedback at /admin/technical.
- Old projects, reports, authentication, CSRF and legal documents retained.

## Database

Additive Alembic revision `e1d202610001`, parent `3a7d9c1e5b42`:
new decision_briefs/decision_journeys tables, nullable AI log user_id and guest
identity. Migration runs before application startup via existing Docker command.
Rollback must preserve guest billing logs; downgrade refuses to delete evidence.

## Validation

Complete automated suite: **423 passed**, 73.46 seconds. JavaScript syntax
checks and `git diff --check` also pass.
Providers are mocked: tests are not a real MWS run. Tests include guest ownership
and expiration, auth save, invalid response preserving previous results, consent
revocation, duplicate events, stale revisions, recovering a lost start response,
and all 575 pairs in a 25×23 comparison without truncation.

Fresh synthetic SQLite Preview runs all migrations; PostgreSQL offline SQL
compilation succeeds. PostgreSQL online migration
and real browser/Production checks depend on the release environment and are
reported separately. No load/performance claim is made from mock timings.

## Owner check on the live site

1. Without signing in, open the homepage: placeholders are light grey; typed text
   is black. Select an example, adjust question and details.
2. Uncheck AI suggestions to retain only your own options and conditions.
3. Start; check understanding, add/remove options and conditions, mark an
   indispensable condition “Обязательно”, compare.
4. Verify unknown mandatory facts are not treated as confirmed; open details.
5. Change conditions and compare again. Refresh without new model calls.
6. Save: sign in to an existing account or register and confirm email. Return to
   the same result; saved decisions are in the hamburger menu.
7. As admin, check /admin periods/cohorts. Without analytics consent there are
   no optional funnel events. Technical AI expenses are retained regardless.
8. Repeat on a phone; check menu, fields, example links, comparison and errors.

## Limits

No web search in generated comparisons: current external facts must be supplied
by the user. Guest identity is a browser session, not a deduplicated person.
A background request interrupted by a process restart is marked uncertain;
no automatic paid replay is performed. Hourly expiry cleanup is supplemented
by request-time cleanup. Email delivery and actual MWS behaviour require live
verification; automated mocks do not prove them.
