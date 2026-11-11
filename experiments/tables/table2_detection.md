# Tabla 2 — Detección

| case_id | email | expected_positive | observed_breach_count | radar_match | new_leak_hits | leak_hit_id | is_correct | duration_ms | execution_id | error | retrieved_at |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| account-exists | account-exists@hibp-integration-tests.com | True | 1 | True | 1 | 98c477ca-f8bd-48b3-8fcd-91b2c751ded9 | True | 44.582 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.654495Z |
| multiple-breaches | multiple-breaches@hibp-integration-tests.com | True | 3 | True | 3 | 106fabb9-2fa5-40a9-8d1a-4a54e145164b | True | 6.331 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.660847Z |
| not-active-and-active-breach | not-active-and-active-breach@hibp-integration-tests.com | True | 1 | True | 1 | 26246ead-ec77-4e75-81cc-8ac8b8b2b423 | True | 5.747 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.666609Z |
| not-active-breach | not-active-breach@hibp-integration-tests.com | False | 0 | False | 0 |  | True | 3.225 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.669848Z |
| opt-out | opt-out@hibp-integration-tests.com | False | 0 | False | 0 |  | True | 2.918 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.672776Z |
| opt-out-breach | opt-out-breach@hibp-integration-tests.com | False | 0 | False | 0 |  | True | 2.897 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.675683Z |
| paste-sensitive-breach | paste-sensitive-breach@hibp-integration-tests.com | False | 0 | False | 0 |  | True | 2.999 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.678694Z |
| permanent-opt-out | permanent-opt-out@hibp-integration-tests.com | False | 0 | False | 0 |  | True | 3.542 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.682250Z |
| sensitive-and-other-breaches | sensitive-and-other-breaches@hibp-integration-tests.com | True | 2 | True | 2 | f7dede76-b7f3-43db-a712-5c16ba0d882c | True | 4.837 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.687099Z |
| sensitive-breach | sensitive-breach@hibp-integration-tests.com | False | 0 | False | 0 |  | True | 3.309 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.690420Z |
| spam-list-only | spam-list-only@hibp-integration-tests.com | True | 1 | True | 1 | 41d858ae-bff9-470c-91c3-09840298e440 | True | 6.54 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.696979Z |
| spam-list-and-others | spam-list-and-others@hibp-integration-tests.com | True | 3 | True | 3 | 9760fd13-4734-4e96-b3aa-96ae150a7d21 | True | 7.303 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.704304Z |
| subscription-free-and-other-breaches | subscription-free-and-other-breaches@hibp-integration-tests.com | True | 2 | True | 2 | f02f60ee-b470-4fe4-8930-dd9faba6ce64 | True | 6.035 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.710357Z |
| stealer-log | stealer-log@hibp-integration-tests.com | True | 1 | True | 1 | 6a602166-849c-4543-8edf-2276db5bb920 | True | 5.281 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.715653Z |
| subscription-free-breach | subscription-free-breach@hibp-integration-tests.com | True | 0 | False | 0 |  | False | 3.256 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.718922Z |
| unverified-breach | unverified-breach@hibp-integration-tests.com | True | 1 | True | 1 | 41850a77-f120-4d4a-9042-04d4e0d85f97 | True | 3.869 | NO MEDIDA (backend service invocation; no n8n execution) |  | 2026-11-05T16:14:28.722802Z |
