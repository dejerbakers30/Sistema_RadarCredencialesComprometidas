# Tabla 4 — Idempotencia

| case_id | repetitions | initial_hits | new_hits_total | final_hits | duplicate_events_sent | duplicates_suppressed | duplicate_suppression_rate | duration_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| account-exists | 5 | 1 | 0 | 1 | 4 | 4 | 1.0 | 9.703 |
| multiple-breaches | 5 | 3 | 0 | 3 | 4 | 4 | 1.0 | 8.004 |
| not-active-and-active-breach | 5 | 1 | 0 | 1 | 4 | 4 | 1.0 | 6.298 |
| sensitive-and-other-breaches | 5 | 2 | 0 | 2 | 4 | 4 | 1.0 | 6.508 |
| spam-list-only | 5 | 1 | 0 | 1 | 4 | 4 | 1.0 | 6.254 |
| spam-list-and-others | 5 | 3 | 0 | 3 | 4 | 4 | 1.0 | 8.332 |
| subscription-free-and-other-breaches | 5 | 2 | 0 | 2 | 4 | 4 | 1.0 | 7.212 |
| stealer-log | 5 | 1 | 0 | 1 | 4 | 4 | 1.0 | 5.602 |
| subscription-free-breach | 5 | 0 | 0 | 0 | 4 | 4 | 1.0 | 4.368 |
| unverified-breach | 5 | 1 | 0 | 1 | 4 | 4 | 1.0 | 5.221 |
