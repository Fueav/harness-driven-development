# Compatibility evaluation evidence

`behavior-results.json` records nine executed compatibility tasks from `scripts/behavior_cases.py`, including authority conflicts, explicit pause, authorized repair, runtime verification and read-only answers. Package, runner and case digests bind the results; release verification rejects stale or incomplete records.
These fixtures deliberately isolate the compatibility skill and use their own checks. They do not prove native repository verification, Git delivery, or the ambient global skill stack. The canonical Template owns those daily-work evaluations in `evals/run_native.py`; its suite verifies that evidence separately.
Raw traces remain outside this repository. Preserve failed runs and execution digests; neither normalized routing answers nor expected results can replace executed evidence.
