# GPU power-delivery benchmark

A small benchmark for checking whether a power supply can sustain an RTX 5090 under LLM inference load, plus the raw data from a test where a 1200 W PSU cut power in 12 of 12 runs while a 750 W PSU passed.

Full write-up: see `PSU_INVESTIGATION.md`.

> **Warning.** This benchmark can make a faulty or incompatible PSU cut power abruptly, as it did twelve times in my tests. Stop databases and other services first, and do not run it on a machine holding data you can't afford to corrupt.

## What it does

`psu_bench.sh` warms up a model in Ollama, runs three 1,500-token generations, and samples the GPU with `nvidia-smi` every 100 ms (power, SM clock, temperature and throttle reasons). A pass means all three generations complete. It writes `psu_<label>.csv`, `.toks` and `.json` to the current directory.

## Requirements

- Linux with an NVIDIA GPU and `nvidia-smi`
- [Ollama](https://ollama.com) running on `localhost:11434` with the model pulled (default `gemma4:31b`; override with `MODEL=...`)
- `curl`, `python3`, `stdbuf` (coreutils)

## Usage

```bash
bash psu_bench.sh my-psu-label
# or, from another machine:
ssh user@gpu-host 'cd ~/psu-test && bash -s -- my-psu-label' < psu_bench.sh
```

Charts are rebuilt from `psu_data/` with `python3 make_figures.py` (needs matplotlib).

## Data

See `psu_data/README.md`. The 12 failed 1200 W runs have no sample files: the original sampler wrote through a buffer and each power cut discarded it. Only journal excerpts survive.

## Limitations

- One GPU, one board, one unit of each PSU. These results can't separate a faulty unit from a design that is sensitive to the RTX 5090's load transients.
- System power draw is estimated, not measured at the wall.

## License

MIT
