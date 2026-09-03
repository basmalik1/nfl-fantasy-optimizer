# NFL Fantasy Draft Pick Optimizer

Live draft assistant for Sleeper. Polls the public Sleeper API every 4s during a
draft, tracks who is gone, and ranks the best available pick for your roster.

Configured for any Sleeper league — 10-team PPR snake by default.

## Run

```
python -m http.server 8765 --bind 127.0.0.1
```
Then open http://127.0.0.1:8765/draft-assistant.html

Serve over HTTP, not `file://` — the Sleeper fetch is blocked from a file origin.

## Point it at your league

Either pass URL params:

```
draft-assistant.html?draft=<draft_id>&slot=3&teams=10&rounds=15
```

or copy `config.local.example.js` to `config.local.js` (gitignored) and fill it in.

`<league_id>` is in your Sleeper URL (`/leagues/<league_id>/...`). Get the draft id
with:

```
curl -s https://api.sleeper.app/v1/league/<league_id> | grep -o '"draft_id":"[0-9]*"'
```

No league or draft identifiers are committed to this repo.

## Rebuild the board

```
python src/build.py
```
Pulls fresh projections and regenerates `draft-assistant.html`. No auth needed.

## The model

Full-season, not week-1. Inputs are 2026 projected season points and 2025 actual
season points, both reduced to per-game.

- **VOR** — value over replacement at this league's real replacement level
  (QB12, RB30, WR34, TE12, K11, DEF11). Elite RB is worth ~+9.5 ppg over
  replacement; the best QB only ~+3.6. That is the whole argument for waiting on QB.
- **Value over next available** — compares the best player at each position now
  against who will likely survive to your *next* pick, and favors the steeper cliff.
- **Durability adjustment** — Sleeper projects **18 GP for every player**, so injury
  risk is not in their numbers. 2025 games played, shrunk toward a full season and
  capped at a 12% haircut. Toggle it off with "Rate only" in the UI.
- **Bye stacking** — penalty when a pick would put 3+ (‑0.25), 4 (‑0.8), or 5+ (‑1.6)
  of your non-K/DEF players on the same bye. Week 11 has six teams out.
- **Injury flags** — IR/PUP/NA/Out excluded outright. An early-September
  "Questionable" is a week-1 tag and is weighted near zero over a 17-week season.

## Deliberately not modeled

**Playoff schedule (wk 15-17).** Measured it: across draftable players the ratio of
projected playoff-week output to their own season baseline spans 0.986–1.029 — about
±1.5%, or ±0.2 ppg on a 15-ppg starter. Sleeper's weekly projections barely flex for
opponent, so weighting this would be fake precision. Each player's wk15/16/17
opponents are **displayed** so you can judge; they carry no scoring weight. Doing this
properly needs a real opponent-strength source.

## Data notes

Bye weeks are derived, not hardcoded: pull all 18 weeks of projections, and the week a
team has zero projected players is its bye. All 32 teams resolve to exactly one.

`api.sleeper.com` returns 403 without a `User-Agent` header. `api.sleeper.app/v1` does not.

The API is **read-only** — it can report picks but cannot submit one.

## Layout

```
draft-assistant.html   generated, self-contained (open this)
src/template.html      page source, __DATA__ is the injection point
src/build.py           regenerates the board from the Sleeper API
data/                  cached board, byes, weekly projections
```
