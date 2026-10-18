# cron-job.org setup for SHAPELIVE (three jobs, Monday - Friday, timezone Asia/Kolkata)

All three jobs call the GitHub API the same way:

* URL     `https://api.github.com/repos/pkjha1010/zeko/actions/workflows/<FILE>/dispatches`
* Method  `POST`
* Headers `Authorization: Bearer <your GitHub token>`  |  `Accept: application/vnd.github+json`  |  `X-GitHub-Api-Version: 2022-11-28`  |  `Content-Type: application/json`
* Token   a fine-grained personal access token for the repo `pkjha1010/zeko` with **Actions: Read and write** (nothing else needed).  Success = HTTP 204.

| # | Time (IST) | Workflow file | Request body |
|---|-----------|---------------|--------------|
| 1 | **06:00** Mon-Fri | `shape_live_plan.yml`    | `{"ref":"main"}` |
| 2 | **09:00** Mon-Fri | `shape_live_manager.yml` | `{"ref":"main","inputs":{"job_end":"12:58:00"}}`  (morning job, hands over quietly) |
| 3 | **12:55** Mon-Fri | `shape_live_manager.yml` | `{"ref":"main","inputs":{"job_end":"15:45:00"}}`  (afternoon job, must end clean) |

Why two manager jobs: one GitHub job may run at most 6 hours; 09:00 -> 15:45 is 6 h 45 min.  The manager keeps no memory of its own - the afternoon job rebuilds everything
from Kite (today's orders, positions, alerts) and the plan file, so it can also be started at any other time (e.g. after a crash) with the same call.  The two jobs share a
queue (`concurrency`), job 3 waits until job 2 has finished at 12:58; the gap of a few seconds is harmless: ENTRY and the target / stop-loss GTT are carried by Zerodha itself.

Other useful calls (run by hand from the GitHub "Actions" tab, or a cron job of your own):
* `shape_live_manager.yml`, `{"ref":"main","inputs":{"mode":"cleanup"}}`  - delete every waiting SHP| alert now.
* `shape_live_manager.yml`, `{"ref":"main","inputs":{"dry_run":"1"}}`    - print what the manager would do, send nothing.
* `shape_live_plan.yml`,    `{"ref":"main","inputs":{"mode":"probe"}}`   - print your existing ATO alerts (check the GTT target / stop-loss layout, see below).

Set the cron-job.org "failure notifications" on, and keep GitHub's "workflow run failed" e-mail on: the afternoon job ends with an ERROR when anything of the strategies is still open
at 15:45 (open position, waiting order, GTT or alert).

## One thing to check once before the first live day (GTT layout)
The plan asks Zerodha for a built-in GTT with a **target +60 %** for all three strategies and a **stop-loss -20 %** for WRU only
(`"gtt": {"target": 60, "stoploss": 0}` and `{"target": 60, "stoploss": -20}`; `stoploss: 0` = no stop-loss).  Your old plan used `{"target": 0, "stoploss": -10}`, so the
field names are the same, but I could not test the NEW target leg against Zerodha.  Do this once:
1. In the Kite app create ONE ATO alert by hand with a 60 % target and a 20 % stop-loss, validity Day, and another with only the 60 % target.
2. Run `shape_live_plan.yml` with `mode = probe` and look at how the two alerts are printed.
3. If the layout differs, set the repository variables `GTT_TP_SL` / `GTT_TP_ONLY` (JSON text, `{tp}` and `{sl}` are replaced by the percentages) as env of the plan step.
Until this is confirmed, run the plan with `dry_run = 1` and trade with one lot.
