# FedEx Office Travel Policy Flight Booking

**No affiliation with FedEx Office or FedEx Corporation.** The handbook is the company's *Travel and Business
Expense* policy (updated January 19, 2015), a PDF hosted publicly on an events site, bundled verbatim for research.
Do not publish this plugin before the course staff confirm that a verbatim corporate handbook may be redistributed
(MASTER_PLAN section 4: corporate plugins wait for the instructor's answer).

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the company's real travel
policy: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and policy section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the policy's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 7,361 words, 965 lines, sha256 `b9e3873f...b2770f1`, equal to
`pilot_work/originals/fedex-office/frozen/SHA256SUMS`) is never paraphrased, and the task text restates no rule.
Under stock NanoAgent the agent does not see it: the plugin then runs as the `off` baseline. The `harness.policy`
switch of the NanoAgent fork (github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system
prompt: `harness.policy: full` adds all of it, and the selection methods add parts of it. These plugins are meant to
run with `query: instructions+input`, so a selector sees the traveller's request.

**Size.** Calibrated on the paid Thornton and NJC validation runs (DeepSeek tokens, about 0.2 a character of
handbook plus 1,800 for the rest of the first prompt), the first call under `full` is about 11,100 input tokens
(46,721 characters of policy), the second about 11,700 (plus the trip record) and the third 12,800 to 14,300 (plus
the search results, 2 to 11 offers). A 3-call run (`get_trip`, `search_flights`, `submit`) is about 36,000 to
37,500 input tokens, and the final message after `submit` starts at about 15,000, so the run ends near 52,000 with
output tokens: under the hosted cap of 65,536. One extra tool call before `submit` (for example a second search) adds
about 14,500 and brings the run to the cap.

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date, then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is the template's shared list
  (codes for rules this policy lacks) plus `POLICY_EXCEPTION_APPROVED`, `BUSINESS_GUEST_NOT_PREPAID` and
  `PERSONAL_COST_PAID_BY_TRAVELER`, and decoy codes from other handbooks' rules. Fares are in cents of US dollars.
- **Success:** every field is one the answer key accepts; the cabin is graded as the chosen offer's own. Score =
  fields right / 6.
- **Reasons on a declined request.** The task instructions say that when the booking is not what the traveller asked
  for, the reason code gives why the request is declined. Such a booking accepts only the codes that name the
  handbook's ground, not `LOWEST_FARE`: a refused first or business cabin (`gull-ridge`, `nettle-bay`, `oak-lantern`).
  A nonstop declined because the cheaper connection passes the handbook's specific savings or margin test, part of its lowest-logical-fare rule, accepts `LOWEST_FARE` beside the specific codes (lead's decision, the same in every plugin): `hazel-tarn` and `juniper-slate` (the savings and delay test of lines 129-133).
  `sedge-copper` keeps `LOWEST_FARE` beside `LOYALTY_PROGRAM_PREFERENCE`: lines 820-821 decline the airline because
  a cheaper fare exists. `iris-brook` and `kestrel-dune` keep it too: outside the example the only ground for the
  connection is that it is "the least expensive option" (lines 129-130), and the nonstop is accepted as well.
- **No hidden facts:** no scenario has `answer_key_inputs`. Every trip record holds the trip's advance approval by
  the traveller's approving manager (lines 760-762: air travel is authorized "if booked through Global Travel and
  approved in advance").

| Scenario | Category | Expected decision (offer; cabin) | Reason | Approver | Clause (frozen lines of must_keep) |
|---|---|---|---|---|---|
| `aspen-wharf` | easy | BOOK (morning-first; FIRST) | SENIOR_ROLE_ENTITLEMENT | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE (138, 760-762) |
| `briar-cove` | easy | BOOK (denver-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or CONNECTING_FLIGHTS or POLICY_GENERAL (135-137, 44-45, 760-762, 129-133) |
| `cinder-heath` | easy | BOOK (united-business; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE (154-156, 760-762) |
| `dover-moss` | easy | BOOK (united-first; FIRST) | SENIOR_ROLE_ENTITLEMENT | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE (138, 760-762) |
| `elm-garnet` | easy | BOOK (japan-economy; ECONOMY) | LOWEST_FARE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or POLICY_GENERAL (135-137, 44-45, 760-762) |
| `fern-quarry` | boundary_twin | BOOK (aerlingus-business; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE (154-156, 760-762) |
| `gull-ridge` | boundary_twin | BOOK (aerlingus-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or POLICY_GENERAL (154-156, 135-137, 44-45, 760-762) |
| `hazel-tarn` | boundary_twin | BOOK (chicago-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or CONNECTING_FLIGHTS or POLICY_GENERAL (135-137, 44-45, 760-762, 129-133) |
| `iris-brook` | boundary_twin | BOOK (chicago-economy or nonstop-economy; ECONOMY) | ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or CONNECTING_FLIGHTS or POLICY_GENERAL (135-137, 44-45, 760-762, 129-133) |
| `juniper-slate` | boundary_twin | BOOK (atlanta-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or CONNECTING_FLIGHTS or POLICY_GENERAL (135-137, 44-45, 760-762, 129-133) |
| `kestrel-dune` | boundary_twin | BOOK (atlanta-economy or nonstop-economy; ECONOMY) | ALTERNATE_ROUTE_WITHIN_MARGIN or CONNECTION_TOO_LONG or COST_SAVINGS or LOWEST_FARE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or CONNECTING_FLIGHTS or POLICY_GENERAL (135-137, 44-45, 760-762, 129-133) |
| `lark-meadow` | multi_rule | BOOK (alaska-first; FIRST) | MEDICAL_NEED | APPROVING_MANAGER or NONE or VICE_PRESIDENT | AIR_TRAVEL or CLASS_OF_SERVICE (139-144, 760-762) |
| `mallow-pier` | multi_rule | BOOK (american-first, delta-first; FIRST) | TRAVELER_PAYS_UPGRADE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE (145-149, 760-762) |
| `nettle-bay` | multi_rule | BOOK (united-economy; ECONOMY) | UPGRADE_NOT_ELIGIBLE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or POLICY_GENERAL (150-153, 138, 135-137, 44-45, 760-762) |
| `oak-lantern` | multi_rule | BOOK (morning-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or DOMESTIC_MEALS or POLICY_GENERAL (154-156, 298-305, 135-137, 44-45, 760-762) |
| `plume-sorrel` | hidden_clause | BOOK (american-first; FIRST) | POLICY_EXCEPTION_APPROVED | APPROVING_MANAGER or MANAGING_DIRECTOR or NONE | ACCOUNTABILITY or EXCEPTIONS (77-80, 932-934, 760-762) |
| `quince-harbor` | hidden_clause | BOOK (alaska-friday; ECONOMY) | LOWEST_FARE or PERSONAL_COST_PAID_BY_TRAVELER | APPROVING_MANAGER or NONE | PERSONAL_WITH_BUSINESS (526-531, 760-762) |
| `rowan-flint` | distractor | BOOK (klm-business; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE (154-156, 760-762) |
| `sedge-copper` | distractor | BOOK (american-economy; ECONOMY) | LOWEST_FARE or LOYALTY_PROGRAM_PREFERENCE | APPROVING_MANAGER or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or NON_REIMBURSABLE or POLICY_GENERAL (135-137, 44-45, 760-762, 820-821) |
| `thistle-marsh` | refusal | REFUSE (none; NONE) | BUSINESS_GUEST_NOT_PREPAID or OUTSIDE_POLICY_SCOPE | APPROVING_MANAGER or NONE | BUSINESS_GUESTS (538-543) |
| `umber-wick` | refusal | REFUSE (none; NONE) | COMPANION_NOT_COVERED or PERSONAL_TRAVEL_NOT_COVERED | APPROVING_MANAGER or NONE | DEPENDENT_TRAVEL or NON_REIMBURSABLE (534-536, 827-828) |
| `vale-pewter` | flag | FLAG_FOR_APPROVAL (early-business; BUSINESS) | UNCLEAR_POLICY_TEXT or APPROVAL_REQUIRED | MANAGING_DIRECTOR or NOT_NAMED | AIR_TRAVEL or CLASS_OF_SERVICE (154-156, 77-80, 760-762) |
| `willow-cairn` | flag | FLAG_FOR_APPROVAL (aircanada-business; BUSINESS) | UNCLEAR_POLICY_TEXT or APPROVAL_REQUIRED | MANAGING_DIRECTOR or NOT_NAMED | AIR_TRAVEL or CLASS_OF_SERVICE or DOMESTIC_MEALS (154-156, 298-305, 515-516, 77-80, 760-762) |
| `yarrow-glint` | flag | FLAG_FOR_APPROVAL (american-first; FIRST) | APPROVAL_REQUIRED or MEDICAL_NEED | SENIOR_VICE_PRESIDENT or VICE_PRESIDENT | AIR_TRAVEL or CLASS_OF_SERVICE (139-144, 760-762) |

Mix (EDGE_CASES.md 5.2, 24 row): 5 easy, 6 boundary twins, 4 multi-rule, 2 hidden clause, 2 distractor, 2 refusal,
3 flags (12.5%; the 15% cap is 3). Decisions: 19 BOOK (5 first, 3 business, 11 economy), 2 REFUSE, 3
FLAG_FOR_APPROVAL. Twin pairs: 361 against 360 scheduled minutes on international nonstops (`fern-quarry`,
`gull-ridge`); a connection saving $151 against $150 (`hazel-tarn`, `iris-brook`); a connection arriving 120 against
121 minutes after the nonstop (`juniper-slate`, `kestrel-dune`).

Each unclear point of the text is one flag with clear twins on both sides:

- **"not including connections or layovers"** (lines 154-156): whether the flying time of a connection adds its
  flights. `vale-pewter` (235 + 205 minutes through Miami, no flight over 360); twins `cinder-heath` (business) and
  `gull-ridge` (coach).
- **"international travel"** (lines 154-156): never defined, while 3.6.1 Domestic Travel Meals lists Toronto and
  Vancouver (lines 298-305) and lines 515-516 group the US with Canada. `willow-cairn` (Miami to Vancouver, 375
  minutes); twins `cinder-heath` (Frankfurt: business) and `oak-lantern` (Honolulu: coach).
- **Approval required.** `yarrow-glint`: the first-class certification was signed by a Director, and lines 142-144 need
  the VP or higher. Hold the first-class fare for the VP; twins `lark-meadow` (VP certified: first) and `nettle-bay`
  (no certification: coach).

Accept sets. The connecting-flights clause (lines 129-133) is an example inside an "expected to" rule: inside the
example (savings over $150 and no more than two hours later) only the connection is accepted; outside it, for a
traveller who asks for the nonstop, both the nonstop and the cheaper connection are. Approvers follow the template's
rule 4' (SYNC_NOTES.md): a booking accepts every sign-off on file it relies on (the approving manager's trip approval,
and the VP's certification or the MD's exception where used) and `NONE`; a refusal accepts `NONE` and the approving
manager; a hold accepts only the awaited role (`VICE_PRESIDENT` or `SENIOR_VICE_PRESIDENT` for the certification;
`NOT_NAMED` or `MANAGING_DIRECTOR`, the department MD who approves exceptions under $10,000, for an unclear clause).

**Duration (`rules.over`).** "international-business": over when one flight alone is scheduled at more than 360
minutes, not over when the flights added together are 360 or less, unclear (`None`) between; ground time never
counts. It applies to international trips only; a domestic flight is coach whatever its length (`oak-lantern`).
Background offers are 0 on every search where a filler itinerary could fall on the other side of a rule (every
international business case and every connecting-flights case); `handbook.json` `background_offers` is 0, so a search
the case does not pin lists nothing.

Degenerate agents (`tests/test_verifier.py`): one that always holds the right offer as unclear passes 2 cases
(`vale-pewter`, `willow-cairn`); one that always books the cheapest seat with `LOWEST_FARE`, `NONE` and the right
section passes 7 (`briar-cove`, `elm-garnet`, `hazel-tarn`, `iris-brook`, `juniper-slate`, `kestrel-dune`,
`sedge-copper`; it fails every first, business, personal, refusal and hold case, and every declined cabin).

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller and level, route, dates, purpose, requested cabin, routing and airline, sign-offs, colleagues already ticketed | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the pinned scenario offers plus seeded background offers on those searches only; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-fedex-office-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this policy's scenario ids, approvers, sections, three reason
  codes and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  policy's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this policy's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: decisions taken during the build, the blind read and the acceptance outputs.
- `tests/AUDIT_NOTES.md`: the independent audit: defects found and fixed.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/fedex-office-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py .
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
