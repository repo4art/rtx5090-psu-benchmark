# Raw data for PSU_INVESTIGATION.md

## 750 W runs (all passed) — written by `psu_bench.sh`

| Files | Run |
|---|---|
| `psu_750w.*` | morning baseline, 13:29 |
| `psu_750w_recheck.*` | evening recheck, 18:10 |
| `psu_750w_final.*` | final run with the 750 W reinstalled, 18:45 (current script) |

- `.csv`: one row per 100 ms: timestamp, GPU power (W), SM clock (MHz), temperature (°C), then `sw_power_cap`, `hw_slowdown`, `hw_power_brake_slowdown`, `hw_thermal_slowdown` (`Active` / `Not Active`)
- `.toks`: tokens/s for each of the three generations
- `.json`: summary as computed by the script

## 1200 W runs (all lost power)

There are no sample files. The script version used then wrote samples through a buffer, and each power cut discarded them; the current script line-buffers for that reason.

`1200w_last_log_lines_per_boot.txt` is what the system journal kept instead: for every boot between 15:44 and 18:30, its first and last timestamp and the last Ollama progress lines. A run that died shows generation at ~61 tok/s and then nothing. Not every boot is a test: some are BIOS visits and cable changes, and boot -2 (18:08–18:14) is the 750 W recheck, which ended normally. Some failed runs left no Ollama lines because the journal had not yet been flushed to disk when power went. Map boots to tests with the times in the table in `PSU_INVESTIGATION.md`.
