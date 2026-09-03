# NFL Fantasy Optimizer

Two tools for a [Sleeper](https://sleeper.com) fantasy football league:

- **`draft-assistant.html`** — live during your draft. Polls the API every 4 seconds,
  tracks who's been taken, and ranks the best available pick.
- **`season-manager.html`** — the rest of the season. Optimal weekly lineup, waiver
  targets with FAAB bids, and trade offers worth sending.

No account, no API key, no install. Sleeper's public API is read-only, so both tools
recommend — they can't set a lineup or send a trade for you.

## Run

```
python src/run.py
```

Refreshes the projections if the cached board is more than 12 hours old, rebuilds both
pages, starts a local server and opens the dashboard.

```
python src/run.py --force         # refetch regardless of cache age
python src/run.py --no-refresh    # skip the network entirely
python src/run.py --page draft    # open the draft assistant instead
```

If a refresh fails — network down, Sleeper having a moment — it warns and serves the
cached board rather than leaving you with nothing before kickoff. Port 8765 by default,
stepping to the next free one if it's taken.

It has to be served over HTTP; the Sleeper request is blocked from a `file://` origin.

## Point it at your league

```
draft-assistant.html?draft=<draft_id>&slot=3&teams=10&rounds=15
```

Or copy `config.local.example.js` to `config.local.js` (gitignored) and fill it in.
Your league id is in the Sleeper URL; the draft id comes from
`api.sleeper.app/v1/league/<league_id>`.

## Season manager

- **Lineup** — fills your starting slots to maximise projected points for the current
  week. Slots are nested (FLEX takes RB/WR/TE), so filling locked slots first and
  taking the best leftovers for FLEX is provably optimal. Flags byes and shows which
  weeks stack up.
- **Waivers** — a free agent only appears if adding him *and dropping someone* raises
  your projected starting lineup. Bench depth that never starts is worth zero. Suggests
  a FAAB bid scaled to the gain, capped at a third of your remaining budget.
- **Trades** — searches 1-for-1 and 2-for-2 swaps against every team. Tier 1 improves
  both starting lineups; tier 2 improves yours while theirs stays flat. Ties go to the
  cheaper package. It assumes the other manager values players off the same
  projections, which they won't, and has no injury-robustness term — trading away your
  only startable player at a position raises your ceiling and your risk together.

## How the draft board ranks players

Full-season and per-game — projected season points against last season's actuals.
No week-1 or matchup weighting.

- **Value over replacement**, measured against your league's real replacement level.
  In a 10-team 1QB league an elite RB is worth ~9.5 ppg over replacement and the best
  QB only ~3.6, which is why it tells you to wait on QB.
- **Value over next available** — favors the position with the steeper drop-off
  between now and your next pick.
- **Durability** — Sleeper projects 18 games for *every* player, so injury risk isn't
  in their numbers. Adds a haircut from last season's games played, capped at 12%.
- **Bye stacking** — penalizes putting 3, 4, or 5+ of your players on the same bye.
- **Injury flags** — IR/PUP/Out excluded; an early-September "Questionable" barely
  counts in a 17-week season.

Week 15–17 opponents are shown but not scored — the playoff-week variation is only
about ±1.5%, too small to be a real signal.

## Rebuild without serving

```
python src/build.py
```

## Layout

```
draft-assistant.html      generated — draft-day tool
season-manager.html       generated — in-season tool
src/template.html         draft page source; __DATA__ is the injection point
src/season-template.html  season page source
src/run.py                refresh + serve + open (start here)
src/build.py              rebuilds the board and renders both pages
data/                     cached projections, byes, schedule
```

The Sleeper API is read-only. This tells you what to pick; it can't pick for you.

## License

MIT — see [LICENSE](LICENSE).
