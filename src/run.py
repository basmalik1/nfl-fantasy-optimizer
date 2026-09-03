"""Launch the dashboard: refresh projections if stale, serve, open a browser.

    python src/run.py                 # refresh if cache is >12h old, then serve
    python src/run.py --force         # always refetch
    python src/run.py --no-refresh    # skip the network entirely (game day)
    python src/run.py --page draft    # open the draft assistant instead

A refresh failure never blocks the launch -- the dashboard comes up on the cached
board with a warning, because a stale lineup beats no lineup ten minutes before
kickoff.
"""
import argparse, functools, http.server, os, socket, sys, time, webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build

# Line-buffer stdout so progress shows up when this is redirected to a log or
# run from a scheduler, not just from an interactive terminal.
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

ROOT = build.ROOT
STAMP = os.path.join(build.DATA, "data.json")
PAGES = {"season": "season-manager.html", "draft": "draft-assistant.html"}


def cache_age_hours():
    """Hours since the board was last refetched, or None if never."""
    if not os.path.exists(STAMP):
        return None
    return (time.time() - os.path.getmtime(STAMP)) / 3600.0


def refresh(force, max_age):
    age = cache_age_hours()
    if age is None:
        print("no cached board -- fetching")
    elif force:
        print(f"cache is {age:.1f}h old -- forcing refresh")
    elif age <= max_age:
        print(f"cache is {age:.1f}h old (under {max_age}h) -- re-rendering from cache")
        build.render()
        return True
    else:
        print(f"cache is {age:.1f}h old -- refreshing")
    try:
        build.main()
        return True
    except Exception as e:
        # Network down, Sleeper 5xx, whatever. Fall back to whatever we have.
        print(f"\n  !! refresh failed: {type(e).__name__}: {e}")
        if os.path.exists(STAMP):
            print(f"  !! serving the cached board instead ({age:.1f}h old)\n")
            try:
                build.render()
            except Exception as e2:
                print(f"  !! could not render cached board either: {e2}")
                return False
            return True
        print("  !! no cached board to fall back on -- cannot serve\n")
        return False


def free_port(start, tries=12):
    """First bindable port at or after `start`. The old server may still hold one."""
    for p in range(start, start + tries):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return None


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *a):        # keep the console readable
        pass

    def end_headers(self):
        # These pages are regenerated in place; never let a browser cache them.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="refetch regardless of cache age")
    ap.add_argument("--no-refresh", action="store_true", help="skip the network entirely")
    ap.add_argument("--max-age", type=float, default=12.0, help="hours before a refetch (default 12)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--page", choices=sorted(PAGES), default="season")
    ap.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = ap.parse_args()

    if args.no_refresh:
        age = cache_age_hours()
        print(f"skipping refresh (cache {age:.1f}h old)" if age is not None
              else "skipping refresh (no cache)")
        if not os.path.exists(os.path.join(ROOT, PAGES[args.page])):
            print("  !! that page has never been built -- run without --no-refresh once")
            return 1
    elif not refresh(args.force, args.max_age):
        return 1

    port = free_port(args.port)
    if port is None:
        print(f"!! no free port in {args.port}-{args.port + 11}")
        return 1
    if port != args.port:
        print(f"port {args.port} busy -- using {port}")

    url = f"http://127.0.0.1:{port}/{PAGES[args.page]}"
    print(f"\nserving {ROOT}\n  {url}\nctrl-c to stop\n")
    if not args.no_open:
        webbrowser.open(url)

    srv = http.server.ThreadingHTTPServer(
        ("127.0.0.1", port), functools.partial(Handler, directory=ROOT))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("stopped")
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
