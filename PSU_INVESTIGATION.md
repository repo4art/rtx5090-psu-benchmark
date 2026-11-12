# A 1200 W PSU that couldn't hold 430 W — and the 750 W that could

**Date:** 2026-10-18 · **Box:** a home GPU server · **Verdict:** the be quiet! Dark Power 14 1200 W could not run an RTX 5090 in this system and is being returned. Whether this particular unit is faulty or the design is simply too sensitive to Blackwell's load transients is not proven. The 750 W it was meant to replace ran the same load stably, including a 560 W GPU peak.

## TL;DR

- Swapped a 750 W PSU for a be quiet! Dark Power 14 1200 W to give an RTX 5090 proper headroom.
- On the 1200 W the box lost power **5–15 seconds into GPU load, 12 out of 12 times**. No kernel error, no firmware error record, then an automatic reboot.
- Every variable on the user's side was changed one at a time: both included 16-pin cables, a 4×8-pin adapter on four separate ports, single and multi-rail mode, cable bend, CPU cables, PSU fan mode, smart plug, PCIe Gen4 vs Gen5, the 24-pin, the extra disks. Nothing helped.
- The 750 W passed the same benchmark twice, the second time at **524 W average / 559 W peak** GPU draw — more than the 1200 W ever reached before cutting out (~430 W).
- Wattage is capacity. Whether a PSU stays on depends on its protection and regulation circuits, and in this unit one of them cuts power under a load that a 750 W unit carries. The most likely explanation is that it reacts too early to the RTX 5090's fast load spikes; I could not prove that from outside the case.

## The system

| | |
|---|---|
| GPU | NVIDIA RTX 5090 (600 W power limit, factory default) |
| CPU | Intel Core i5-12400F (65 W) |
| Board | Gigabyte Z790 Gaming X AX, BIOS F12 (2025-01-07) |
| Disks | 3× NVMe, 2× SATA HDD |
| PSU A | 750 W (the original) |
| PSU B | be quiet! Dark Power 14 1200 W (ATX 3.1, native 12V-2x6 cable, OC Key for single/multi-rail) |
| Software | Ubuntu, kernel 7.0.0-34, NVIDIA driver 595.71.05, Ollama 0.30.11 |
| Load | `gemma4:31b` (dense 31B, Q4_K_M, ~20 GB VRAM) generating 3 × 1500 tokens |

Total system draw under the benchmark is estimated (not measured at the wall) at roughly 500–650 W — under half of the 1200 W rating.

## The benchmark

`psu_bench.sh` (next to this file). It warms the model, then runs three long generations while `nvidia-smi` samples power, SM clock, temperature and the throttle reasons (`sw_power_cap`, `hw_slowdown`, `hw_power_brake_slowdown`, `hw_thermal_slowdown`) every 100 ms. A pass is all three generations completing.

LLM token generation is memory-bandwidth bound, which is why the card sits well under its 600 W limit and why a PSU swap was never going to change tokens per second. It is still a sustained, realistic load — the one this box actually runs.

Raw samples and the per-boot journal excerpts are in `psu_data/` (see its README).

## Results — 750 W

| Run | tok/s | GPU power (busy avg) | GPU peak (100 ms) | SM clock | Max temp | Throttling |
|---|---|---|---|---|---|---|
| Morning baseline | 60.2 / 59.8 / 60.4 | 412 W | 435 W | 2549 MHz | 63 °C | none |
| Evening recheck | 61.3 / 60.9 / 61.4 | **524 W** | **559 W** | 2937 MHz | 66 °C | `sw_power_cap` briefly (95 of 751 samples) — the card touching its own limit, normal |
| Final, 750 W reinstalled for good (current `psu_bench.sh`) | 61.3 / 60.9 / 61.4 | 523 W | 555 W | 2938 MHz | 65 °C | `sw_power_cap` briefly (87 of 752) |

No hardware slowdown, no power-brake, no thermal throttling in either run. Why the card clocked ~400 MHz higher in the evening was not investigated; it does not change the conclusion, and if anything it made the 750 W's job harder.

## Results — 1200 W

Every run below lost power partway through the first generation. The log line before each cut shows Ollama generating normally at ~61 tok/s; then nothing until the next boot.

| # | Time | What changed | Result |
|---|---|---|---|
| 1 | 15:46 | Native 12V-2x6 cable #1, default (multi-rail) | cut at ~13 s |
| 2 | 15:53 | Reseated the 16-pin at both ends | cut at ~12 s |
| 3 | 16:00 | Reseated again | cut at ~6–9 s |
| 4 | 16:35 | Second included cable, different PSU port | cut |
| 5 | 16:40 | OC Key → single-rail | cut at ~6 s |
| 6 | 16:45 | Smart plug removed from the mains path | cut |
| 7 | 17:13 | BIOS: CPU PCIe Link Speed Gen4 (link verified Gen4 ×16) | cut |
| 8 | 17:18 | One EPS cable instead of two; PSU 0 RPM fan mode off | cut |
| 9 | 17:39 | Cable straightened (it was bent within 40 mm of the GPU connector) | cut |
| 10 | 17:52 | GPU's 4×8-pin adapter on four separate PSU PCIe cables, multi-rail | cut |
| 11 | 17:56 | Adapter + single-rail | cut |
| 12 | 18:19 | 24-pin reseated (both PSU-side plugs), extra disks disconnected, single-rail | cut |

Constant across all twelve: no `NVRM`/Xid error, no machine-check, no PCIe AER, no BERT/GHES firmware error record at the next boot. The GPU link was healthy (Gen5 ×16, then Gen4 ×16 when capped). The box rebooted on its own each time.

## Why this points at the PSU and nothing else

- **Only one thing changed.** The GPU, CPU, board, BIOS, disks, wall wiring and software that failed on the 1200 W all passed on the 750 W, before and after.
- **Not capacity.** 430 W on the GPU plus ~100 W for the rest is under half of 1200 W, and the 750 W carried more.
- **Not a cable or port.** Two native cables, several ports, and an adapter on four other outputs all failed identically.
- **Not the rail mode.** The Dark Power 14 ships in multi-rail mode, where per-rail current limits can trip on a 5090 — the textbook cause, and the first suspect. Single-rail failed the same way.
- **Not the motherboard.** A firmware-initiated reset (PCIe or CPU fault) normally leaves an error record. A power loss leaves nothing, which is what every boot showed.
- **The automatic reboot fits too.** Either the PSU recovers after tripping and the board's AC BACK setting powers it on, or the 12 V rail sags and drops "power good" for a moment, which the board treats as a reset. Both point at the PSU's output behaviour.

The likely internal causes are an over-current/over-power sensing circuit tripping far too early, or poor transient response (the 5090's millisecond spikes pulling the 12 V rail down). It cannot be narrowed further from outside the case.

## Lessons

1. **A PSU that tolerates the load beats a bigger one that doesn't.** Wattage says what a unit *can* deliver, not whether it will stay on.
2. **Change one variable per test, and write it down.** Twelve runs only mean something because each changed one thing.
3. **A clean log is evidence.** Software crashes and GPU faults leave traces; power loss does not.
4. **Line-buffer your telemetry.** The first version of the sampler wrote through a buffer, so every power cut took the last seconds of samples with it. `psu_bench.sh` now uses `stdbuf -oL`.
5. **Test a new PSU under real load before trusting it with live data.** The box hosts databases; twelve hard power cuts is not something to repeat with them running.

## Next

- Return the 1200 W under warranty. Description for support: *Dark Power 14 1200 W. System powers off and restarts within 5–15 s of an RTX 5090 drawing ~430 W (system ~550 W). Reproduced 12 times: multi-rail and single-rail, both included 12V-2x6 cables on different ports, the 4×8-pin adapter on four separate PCIe cables, cable straight at the connector, 0 RPM mode on and off, one or two EPS cables, 24-pin reseated, extra disks disconnected, no smart plug, PCIe Gen4 and Gen5. The same system runs this load stably on a 750 W PSU.*
- Run `psu_bench.sh` on the replacement before the box goes back into service.
