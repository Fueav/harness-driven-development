# Historical compatibility evidence

`behavior-results.json` retains the original nine executed compatibility-task results unchanged. Raw traces remain at their original external locations; this retirement does not modify them or repeat those experiments.

`historical/` preserves the exact bytes of the former release metadata and six evaluation/validation scripts from commit `4c1daa9600f10a0d703ae20c34bd994d407ea2b9`. Scripts use non-executable `.py.txt` names so they remain source audit material rather than current entrypoints. The complete original plugin payload and directory layout remain available in that Git revision.

These results describe the historical skill only. They do not prove the current native execution environment, independent product acceptance, or a releasable plugin. No current release validation consumes this archive.
