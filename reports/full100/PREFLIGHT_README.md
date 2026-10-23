# What the preflight files mean

`preflight.json` and `nonfreq_preflight.json` record early import/indicator/signal
checks on a short historical training-era sample. They are **not backtests**, do
not provide investment results, and do not count as successfully tested strategies.
Passing preflight does not guarantee completion of the full historical audit.

`inventory.csv` is the final full-dataset status authority. `period_results.csv`
contains only candidates that actually completed the full signal, causality,
training and scoring pipeline. Candidate JSON files retain failures and the
source-code review evidence. Old intermediate successful artifacts for a later
quarantined candidate are removed.
