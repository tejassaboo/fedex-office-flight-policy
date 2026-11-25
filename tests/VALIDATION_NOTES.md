# Validation notes: fedex-office-flight-policy (paid wave 2 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w2_2026-11-25/fedex-office-flight-policy@w2/`,
arm `full`, DeepSeek V4 Flash, temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin head
fc2c78e. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

19/24 valid (79.2%), **easy 4/5** (cinder-heath fails). By category: boundary 5/6, distractor 2/2, easy 4/5,
flag 1/3, hidden 2/2, multi 3/4, refusal 2/2. Re-scoring the stored submissions under the fixed keys (this
commit's verifier, no paid call) gives **22/24 (91.7%), easy 5/5**; only the two flag slips stay wrong.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| cinder-heath | **easy** | right offer (United business), cabin, approver, clause; reason LONG_FLIGHT_APPROVED; key INTERNATIONAL_LONG_FLIGHT only | **grader defect** | It applied lines 154-156 correctly ("515-520 minutes ... more than 6 hours, so business class is permitted") and then weighed the two codes: "The reason code is INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED ... Both seem plausible." The shared code list gives neither a description, and the two name the same ground here. 24 other plugins' long-flight business keys accept both (Carter's briar-cove, Blackbaud, NJC, LSU, DNDi, ...); only FedEx, Goodman and Anixter accepted one. Q2: the always-cheapest agent books coach, so this changes nothing for it. The same gap was latent on fern-quarry and rowan-flint. |
| juniper-slate | boundary_twin | right offer (Atlanta connection), reason ALTERNATE_ROUTE_WITHIN_MARGIN; key ALTERNATE_ROUTE_TOO_EXPENSIVE, COST_SAVINGS or LOWEST_FARE | **grader defect** | "Savings $240 > $150 ... delay is exactly 2 hours (not more than 2 hours) ... 'ALTERNATE_ROUTE_WITHIN_MARGIN' - the alternate (connecting) route is within the acceptable margin per policy". Lines 131-133 are a margin test, and this plugin's own open-connection keys (iris-brook, kestrel-dune) and Carter's indigo-wharf use exactly this code for the same fact. The twin kestrel-dune (121 minutes) is still told apart by the offer. Latent on briar-cove and hazel-tarn (same branch). |
| mallow-pier | multi_rule | BOOK American first 9QEW-3QKH ($1,210), TRAVELER_PAYS_UPGRADE; key Delta first G6NS-FULL ($1,165) | **grader defect (key too narrow)** | It anchored on line 135: "the company should book the lowest logical coach fare. The lowest coach red-eye is AA $358 ... book AA First", the traveller paying the difference. Lines 145-147 make the traveller pay "the difference between first class and the best available coach", which reads as the lowest coach fare overall or the upgraded flight's own coach fare. On the second reading the Delta upgrade costs FXO $372, more than the lowest logical coach fare; the American upgrade costs FXO $358 on both readings. The key's "cheapest first-class fare" is defensible too, so both are accepted. Q3: both are first-class seats a self-paying Team Member may take. |
| vale-pewter | flag | BOOK business 4C37-T6HH, LONG_FLIGHT_APPROVED; key FLAG, UNCLEAR_POLICY_TEXT / APPROVAL_REQUIRED | model slip (borderline) | "235 + 205 = 440 min = 7.33 hours > 6 hours. So business allowed." It quoted "not including connections or layovers" (line 155) but read "connections" only as ground time and never weighed the reading that connecting flights are not added (no single flight over 360 minutes). The summing reading is the more natural one; if a re-run books business again, consider making this a BOOK under a new id. |
| willow-cairn | flag | BOOK Air Canada business, INTERNATIONAL_LONG_FLIGHT; key FLAG, UNCLEAR_POLICY_TEXT / APPROVAL_REQUIRED | model slip | "This is international (US to Canada) travel." It never weighed that the handbook files Vancouver under 3.6.1 Domestic Travel Meals (lines 298-305) and groups the US and Canada (lines 515-516), the hidden second reading of "international travel" (line 154). |

## Fixes (this commit)

`src/plugin/rules.py` and the byte-identical `verifier/rules.py`, `tests/build_scenarios.py`, README rows,
regenerated scenario JSON. No id, world, decision or category changed.

1. **Long-flight business (cinder-heath, fern-quarry, rowan-flint):** `LONG_FLIGHT_APPROVED` accepted beside
   `INTERNATIONAL_LONG_FLIGHT`.
2. **Required connection (juniper-slate, briar-cove, hazel-tarn; `CLEAR_CONNECTION`):** `ALTERNATE_ROUTE_WITHIN_MARGIN`
   accepted beside the three codes.
3. **Self-paid first class (mallow-pier, the only case of the branch):** the key also accepts first class on the
   flight that carries the lowest coach fare (`american-first`).

Not loosened: vale-pewter, willow-cairn.

## Q2

The always-cheapest agent books the cheapest seat with `LOWEST_FARE`; none of the fixes add an economy offer or
`LOWEST_FARE` anywhere, so its count is unchanged: **7/24 (29%)** (`MAX_PASS_ALWAYS_LOWEST = 7`).

## Re-run

None strictly needed: all three fixes are grader-only and the stored submissions re-score valid (cinder-heath,
juniper-slate, mallow-pier). Optional confirmation run: cinder-heath (the easy case). Watch vale-pewter.

## Checks

`uv run pytest -q` (208 passed), `uv run ruff check .`, `uv lock --check`, `check_shared.py`,
`tools/stock_verify.py` (24 scenarios, 0 failures), stock `nanoagent plugin inspect .` (exit 0).
