# cron-job.org setup for SHAPELIVE (Monday - Friday, timezone Asia/Kolkata)

All jobs call the GitHub API the same way:

* URL     `https://api.github.com/repos/pkjha1010/zeko/actions/workflows/<FILE>/dispatches`
* Method  `POST`
* Headers `Authorization: Bearer <your GitHub token>`  |  `Accept: application/vnd.github+json`  |  `X-GitHub-Api-Version: 2022-11-28`  |  `Content-Type: application/json`
* Token   a fine-grained personal access token for the repo `pkjha1010/zeko` with **Actions: Read and write**.  Success = HTTP 204.

| # | Time (IST) | Workflow file | Request body | What it does |
|---|-----------|---------------|--------------|--------------|
| 1 | **20:00** Sun-Thu (optional, you can also run it by hand) | `shape_live_plan.yml`    | `{"ref":"main"}` | EVENING preview of the next trading day (no alerts) |
| 2 | **08:30** Mon-Fri | `shape_live_plan.yml`    | `{"ref":"main"}` | MORNING plan: creates the alerts, writes `live_plan/plan.json` |
| 3 | **08:55** Mon-Fri | `shape_live_manager.yml` | `{"ref":"main"}` | the manager, ONE call per day |

The manager workflow contains two chained jobs, so cron job 3 is the ONLY call it needs (the old second call at 12:55 is DELETED):
* job `morning` runs 08:55 -> 12:58:00 and ends quietly (hand-over),
* job `afternoon` starts as soon as `morning` has finished and runs to 15:45:00; it must end clean, otherwise the run fails and GitHub mails you.
If the run is started late (e.g. 13:30 after a problem) the `morning` job does nothing and the `afternoon` job takes over at once.  The manager keeps no memory of its own: the afternoon job
rebuilds everything from Kite (today's orders, positions, alerts) and the plan file.  The few seconds between the two jobs are harmless: entry and the stop-loss / target GTT are carried by Zerodha.

The plan decides what to do from the clock (input `when` = auto):  before 09:15 on a trading day = MORNING (real plan);  after 15:45 or on a weekend = EVENING (preview, next trading day);
between 09:15 and 15:45 it refuses.  Make sure the MORNING plan has finished (green) before 08:55 - the manager reads `live_plan/plan.json` when it starts.

Other useful calls (GitHub "Actions" tab or a cron job of your own):
* `shape_live_manager.yml`, `{"ref":"main","inputs":{"mode":"cleanup"}}`  - delete every waiting SHP| alert now.
* `shape_live_manager.yml`, `{"ref":"main","inputs":{"dry_run":"1"}}`    - print what the manager would do, send nothing.
* `shape_live_plan.yml`,    `{"ref":"main","inputs":{"mode":"probe"}}`   - print your existing ATO alerts (check the GTT layout, see below).
* `shape_live_plan.yml`,    `{"ref":"main","inputs":{"when":"morning","dry_run":"1"}}` - rehearse the morning plan without creating alerts.

## GTT layout
WRU uses a stop-loss without a target: `{"target": 0, "stoploss": -20}` (the same layout your old plan used with -10).  BPB uses `{"target": 60, "stoploss": 0}`.
To check how Zerodha stores them, create two ATO alerts by hand (20 % stop-loss only, 60 % target only), run the plan with `mode = probe` and compare.  If it differs set the env values
`GTT_SL_ONLY` / `GTT_TP_ONLY` / `GTT_TP_SL` on the plan step (`{tp}` and `{sl}` are replaced by the percentages).
