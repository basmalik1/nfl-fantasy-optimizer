"""Rebuild draft-assistant.html from Sleeper's public API.

Pipeline:
  1. season projections (2026) + actuals (2025) -> per-game values
  2. weekly projections wk1-18   -> bye weeks (team missing = bye) + wk15-17 opponents
  3. inline the board into src/template.html -> draft-assistant.html

No auth required. Run:  python src/build.py
"""
import json, os, statistics, collections, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
POS  = ["QB", "RB", "WR", "TE", "K", "DEF"]
UA   = {"User-Agent": "Mozilla/5.0"}   # api.sleeper.com 403s without this

def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))

def season():
    """2026 projections + 2025 actuals, keyed by player_id."""
    board, actual = {}, {}
    for p in POS:
        for e in get(f"https://api.sleeper.com/stats/nfl/2025?season_type=regular&position[]={p}&order_by=pts_ppr"):
            st = e.get("stats") or {}
            actual[str(e.get("player_id"))] = (st.get("pts_ppr"), st.get("gp"))
        for e in get(f"https://api.sleeper.com/projections/nfl/2026?season_type=regular&position[]={p}&order_by=pts_ppr"):
            st, pl = e.get("stats") or {}, e.get("player") or {}
            ppr, adp = st.get("pts_ppr"), st.get("adp_ppr")
            if ppr is None: continue
            if (adp is None or adp >= 400) and ppr < 60: continue
            sp, sg = actual.get(str(e.get("player_id")), (None, None))
            board[str(e.get("player_id"))] = {
                "n": (f"{pl.get('first_name') or ''} {pl.get('last_name') or ''}").strip(),
                "p": p, "t": e.get("team") or "FA",
                "adp": round(adp, 1) if adp and adp < 400 else None,
                # NOTE: Sleeper projects 18 GP for EVERY player -> zero injury risk priced in.
                "pj": round(ppr / 18.0, 2),
                "p25": round(sp / sg, 1) if (sp and sg and sg >= 4) else None,
                "g25": int(sg) if sg else None,
                "inj": pl.get("injury_status") or "",
            }
    return board

def weekly(board):
    """Derive byes + wk15-17 opponents from weekly projections."""
    q = "&".join(f"position[]={p}" for p in POS)
    weeks, teamweeks = {}, collections.defaultdict(set)
    for w in range(1, 19):
        wk = {}
        for e in get(f"https://api.sleeper.com/projections/nfl/2026/{w}?season_type=regular&{q}&order_by=pts_ppr"):
            pts = (e.get("stats") or {}).get("pts_ppr")
            if pts is None: continue
            wk[str(e.get("player_id"))] = {"p": round(pts, 2), "o": e.get("opponent")}
            if e.get("team"): teamweeks[e["team"]].add(w)
        weeks[w] = wk
        print(f"  wk{w:>2} {len(wk):>4} entries")
    byes = {}
    for t, ws in teamweeks.items():
        miss = [w for w in range(1, 19) if w not in ws]
        byes[t] = miss[0] if len(miss) == 1 else None
    for pid, d in board.items():
        d["bye"] = byes.get(d["t"])
        vals = {w: weeks[w][pid]["p"] for w in range(1, 19) if pid in weeks[w]}
        po   = [vals[w] for w in (15, 16, 17) if w in vals]
        mu   = statistics.mean(vals.values()) if vals else 0
        # playoff ratio measured at +/-1.5% across draftable players -> displayed, NOT scored
        d["po"]  = round(statistics.mean(po) / mu, 3) if (len(po) == 3 and mu > 0.5) else None
        d["opp"] = [weeks[w].get(pid, {}).get("o") for w in (15, 16, 17)] if len(po) == 3 else None
    return byes

def main():
    os.makedirs(DATA, exist_ok=True)
    print("season projections + actuals...")
    board = season()
    print(f"  {len(board)} players")
    print("weekly projections (byes + playoff opponents)...")
    byes = weekly(board)
    print(f"  {len(byes)} teams")
    for name, obj in (("data.json", board), ("byes.json", byes)):
        with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
            json.dump(obj, f)
    tmpl = open(os.path.join(ROOT, "src", "template.html"), encoding="utf-8").read()
    html = tmpl.replace("__DATA__", json.dumps(board))
    assert "__DATA__" not in html, "template placeholder not substituted"
    out = os.path.join(ROOT, "draft-assistant.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"wrote {out} ({len(html)} bytes)")

if __name__ == "__main__":
    main()
