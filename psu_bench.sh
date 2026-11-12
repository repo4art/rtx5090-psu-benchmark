#!/usr/bin/env bash
# GPU power-delivery benchmark: three long generations on a dense model, GPU sampled every 100 ms.
# A PSU that handles the load survives all three; the 1200 W unit in PSU_INVESTIGATION.md cut power within 5-15 s.
#
# Run on the GPU box from the Mac:
#   ssh user@gpu-host 'cd ~/psu-test && bash -s -- 1200w' < psu_bench.sh
# Writes psu_<label>.csv / .toks / .json into the current directory (OUTDIR overrides).
set -euo pipefail

LABEL=${1:?usage: psu_bench.sh <label>}
MODEL=${MODEL:-gemma4:31b}
OUTDIR=${OUTDIR:-$PWD}
OUT=$OUTDIR/psu_$LABEL

curl -s localhost:11434/api/generate -d "{\"model\":\"$MODEL\",\"prompt\":\"hi\",\"stream\":false,\"options\":{\"num_predict\":1}}" >/dev/null

# Line-buffered so the samples up to a power cut survive on disk
stdbuf -oL nvidia-smi --query-gpu=timestamp,power.draw,clocks.sm,temperature.gpu,clocks_event_reasons.sw_power_cap,clocks_event_reasons.hw_slowdown,clocks_event_reasons.hw_power_brake_slowdown,clocks_event_reasons.hw_thermal_slowdown --format=csv,noheader,nounits -lms 100 > "$OUT.csv" &
SMI=$!
trap 'kill $SMI 2>/dev/null || true' EXIT

for i in 1 2 3; do
  curl -s localhost:11434/api/generate -d "{\"model\":\"$MODEL\",\"prompt\":\"Write a detailed 2000-word technical essay on GPU memory bandwidth and LLM inference.\",\"stream\":false,\"options\":{\"num_predict\":1500,\"seed\":$i,\"temperature\":0.7}}" \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); print(round(d["eval_count"]/d["eval_duration"]*1e9,1))'
done > "$OUT.toks"

kill $SMI
ollama stop "$MODEL"

python3 - "$OUT" <<'PY'
import csv, json, statistics, sys
o = sys.argv[1]
rows = [r for r in csv.reader(open(o + ".csv")) if len(r) >= 8]
p = [float(r[1]) for r in rows]
c = [float(r[2]) for r in rows]
t = [float(r[3]) for r in rows]
busy = [i for i, x in enumerate(p) if x > 150]
flag = lambda i: sum(1 for r in rows if r[i].strip() == "Active")
res = {
    "tok_s": [float(x) for x in open(o + ".toks").read().split()],
    "power_peak_w": max(p),
    "power_mean_busy_w": round(statistics.mean(p[i] for i in busy), 1) if busy else None,
    "sm_clock_mean_busy": round(statistics.mean(c[i] for i in busy)) if busy else None,
    "temp_max": max(t),
    "samples": len(rows),
    "sw_power_cap": flag(4),
    "hw_slowdown": flag(5),
    "hw_power_brake": flag(6),
    "hw_thermal": flag(7),
}
json.dump(res, open(o + ".json", "w"), indent=1)
print(json.dumps(res, indent=1))
PY
