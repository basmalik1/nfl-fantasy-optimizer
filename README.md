# NFL Fantasy Draft Pick Optimizer

A live draft assistant for [Sleeper](https://sleeper.com). Polls the public Sleeper
API every 4 seconds during your draft, tracks who's been taken, and ranks the best
available pick for your roster.

No account, no API key, no install.

## Run

```
python -m http.server 8765 --bind 127.0.0.1
```

Open <http://127.0.0.1:8765/draft-assistant.html>. Serve it over HTTP — the Sleeper
request is blocked from a `file://` origin.

## Point it at your league

```
draft-assistant.html?draft=<draft_id>&slot=3&teams=10&rounds=15
```

Or copy `config.local.example.js` to `config.local.js` (gitignored) and fill it in.
Your league id is in the Sleeper URL; the draft id comes from
`api.sleeper.app/v1/league/<league_id>`.

## How it ranks players

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

## Rebuild the board

```
python src/build.py
```

## Layout

```
draft-assistant.html      generated, self-contained — this is the app
src/template.html         page source; __DATA__ is the injection point
src/build.py              rebuilds the board from the Sleeper API
data/                     cached projections, byes, schedule
```

The Sleeper API is read-only. This tells you what to pick; it can't pick for you.

## License

MIT — see [LICENSE](LICENSE).
