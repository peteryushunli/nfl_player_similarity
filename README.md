# NFL player similarity data

The data pipeline behind the fantasy hub's commissioner-only **/comps** page.
It builds `data/nfl_similarity.db`, a SQLite file of every QB/RB/WR/TE regular
season from 1999 through the latest completed season, from
[nflverse](https://github.com/nflverse) via `nflreadpy`. The hub's
`scripts/push-nfl-comps.mjs` copies it into Supabase (`nfl_players` /
`nfl_player_seasons`), where the TypeScript port of the similarity model runs.

This repo used to be a standalone app: a FastAPI + React site, an older
Streamlit app, and the Python similarity models. It was retired in September
2026 once /comps went live in the hub, and is preserved at the tag
`standalone-app-final` (`git checkout standalone-app-final`).

## Yearly refresh

Once the season is over (February on; the ingest picks up the new season by
itself):

```bash
pip install -r requirements.txt   # once; Python 3.10+
python -m src.db.ingest           # rebuild data/nfl_similarity.db (a couple of minutes)
python -m pytest                  # check the data contract below
```

Commit the rebuilt DB. Then, in the hub, dry-run the push, check its summary,
and write:

```bash
cd ~/fantasy_football_manager_hub
node scripts/push-nfl-comps.mjs            # dry run: what would be added/removed
node scripts/push-nfl-comps.mjs --write    # production write
```

The push script reads `~/nfl_player_similarity/data/nfl_similarity.db` unless
you pass `--db=<path>` (e.g. for a build in a worktree). `make ingest`,
`make test`, and `make push-dry-run` wrap these steps; there's deliberately no
make target for `--write`.

The hub side is documented in the hub README's
[Player comps data](https://github.com/peteryushunli/fantasy_football_manager_hub#player-comps-data)
section.

## Data contract

The push script reads these columns. `tests/test_contract.py` checks that the
schema and the built DB have them, repeats the script's refuse-to-push checks,
and checks career consistency, ID/date formats, and field coverage. Keep its
`CONTRACT` in sync if the script's queries change.

| Table | Columns |
|---|---|
| `players` | gsis_id, name, position, birth_date, first_season, last_season, headshot_url, espn_id, sleeper_id |
| `draft` | gsis_id, draft_year, round, pick, position_pick, team |
| `seasons` | gsis_id, season, season_number, team, games_played, games_started, pass_completions, pass_attempts, pass_yards, pass_tds, interceptions, rush_attempts, rush_yards, rush_tds, targets, receptions, receiving_yards, receiving_tds, fantasy_points_ppr |

- Regular season only. Seasons with no pass attempts, carries, targets, or
  receptions are dropped, so `season_number` counts a player's seasons with
  offensive involvement.
- `espn_id` / `sleeper_id` are digit strings (`"331"`); `birth_date` is `YYYY-MM-DD`.
- nflverse has no targets for 2003–2008, so receptions stand in for them there.
- `games_started` isn't in nflverse's season stats, so it's always NULL (the hub stores 0).
- The schema carries more columns than the contract (EPA, air yards, shares, ...);
  the hub doesn't read them.

## Layout

```
src/db/ingest.py        nflverse → SQLite (python -m src.db.ingest)
src/db/schema.sql       table definitions
src/db/database.py      SQLite connection + schema setup
data/nfl_similarity.db  the built DB (committed; the hub's source)
tests/test_contract.py  data contract checks
```
