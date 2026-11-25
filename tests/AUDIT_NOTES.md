# Independent audit: fedex-office-flight-policy (2026-11-24)

Audited build 07195c2 against MASTER_PLAN section 4, EDGE_CASES sections 1-3 and 5, `_template/SYNC_NOTES.md`
(including 4') and the defect classes of the paid runs (Thornton/NJC VALIDATION.md, the LSU, NJC and Anixter
REVALIDATION_NOTES). I read the frozen handbook in full (sha256 b9e3873f...b2770f1, identical to the bundled
`policy.txt`) and dumped `get_trip` and every pinned `search_flights` output, then re-derived each answer from the
handbook and those outputs only, before reading `rules.py`.

**Verdict: pass after fixes.** The answer keys were right on all 24 scenarios. The defects were in request wording,
one trip-record sentence, two narrow reason sets, and, at the lead's request, a baseline that passed too many cases.
No defect needed a change to the duration rule or the world.

## Defects found and fixed

| Scenario | Problem | Fix |
|---|---|---|
| sedge-copper | The request names only United, the airline lines 820-821 rule out, and gives no fallback. This is the Anixter zinnia-loch class: the model refused. | Request adds "If United isn't possible, book what the policy allows; I have to be at the review." Answer unchanged. |
| nettle-bay | The request asks only for first beside the VP, which lines 150-153 forbid, and gives no fallback (vesper-dale class). | Request adds "If not, book what the policy allows; I have to be at the pitch." Answer unchanged. |
| oak-lantern | "I'd like business class" with business not allowed on a domestic flight, and no fallback. | Request adds "if the policy allows it", the same as the Dublin twins. Answer unchanged. |
| briar-cove, hazel-tarn, iris-brook, juniper-slate, kestrel-dune | Each key takes a connection that lands 95 to 120 minutes after the nonstop on the day of the work, with no deadline given. This is the LSU tupelo-wren class: a reader could call the later arrival not "logical" (line 135). | Each request now says the kickoff, visits or training "start(s) the next morning". The wording is the same in both twins of each pair, so every twin still differs in one fact. Answers unchanged. |
| plume-sorrel | The MD's exception "covers: first class on this flight" without naming the flight, so a reader could doubt that it covers the cheapest first fare. | Changed to "first class for this trip". Answer unchanged. |
| vale-pewter, willow-cairn | The keys name the department MD (lines 77-78) as a role the hold may await, but accept only UNCLEAR_POLICY_TEXT. That is the NJC iron-plover class (a hold that also awaits a sign-off), and the template's answer.py allows APPROVAL_REQUIRED on an unclear hold. | `rules.UNCLEAR_REASONS` = [UNCLEAR_POLICY_TEXT, APPROVAL_REQUIRED] (both rules.py copies). The always-flag baseline still passes 2. |
| (baseline, lead's target) | The always-cheapest agent (cheapest economy, LOWEST_FARE, NONE) passed 12 of 24. | See the next section: it now passes 10. |

## Baseline: always-cheapest goes from 12 to 10

The lead's target was at most about 10. I changed two cases with no twin, keeping their category and overlays:

- **aspen-wharf (easy).** The traveller is now a Senior Vice President who asks for first class. Line 138 covers
  "Vice Presidents and above". The 06:15 first-class seat is sold out, which keeps the case's sold-out wrinkle, so
  the key is the cheapest first-class seat that can be bought: UA 08:40 at $648 (`morning-first`). Overlay
  `dearer_option` added.
- **rowan-flint (distractor).** The trip is now a short-notice MSP to Amsterdam overnight flight (booked November 27,
  leaving December 6, so it still crosses a month end). The audit starts Tuesday December 8, so the arrival time does
  not matter. The nonstops are scheduled at 500 and 505 minutes and the traveller asks for business "if the policy
  allows it", so the key is the cheapest business fare: KLM at $3,480 (`klm-business`). The 14-day "make every
  attempt" clause (lines 121-122) remains the distractor, now as an aside rather than a `must_keep`. Background
  offers are 0.

`MAX_PASS_ALWAYS_LOWEST` = 10. The 10 it still passes are briar-cove, elm-garnet, gull-ridge, hazel-tarn, iris-brook,
juniper-slate, kestrel-dune, nettle-bay, oak-lantern and sedge-copper. In six of them (gull-ridge, hazel-tarn,
juniper-slate, nettle-bay, oak-lantern, sedge-copper) the request pulls away from the cheapest seat, so the handbook
still decides the answer. Decisions are now 19 BOOK (5 first, 3 business, 11 economy), 2 REFUSE and 3 FLAG.

## Checked and left as built

- **plume-sorrel.** BOOK is right. Line 77 gives exceptions under $10,000 to the department MD, and 924-926 and
  932-934 confirm it. The record names the MD in the traveller's own line, and the fare is $990. The clause set stays
  EXCEPTIONS/ACCOUNTABILITY. Adding CLASS_OF_SERVICE would leave only the reason code to test the hidden clause.
  Risk: low to medium.
- **quince-harbor.** BOOK the cheapest Friday fare (lines 526-531). The traveller will fly that ticket, and booking
  Monday makes no sense. The booking is the same as the always-cheapest one, so only the reason and clause test the
  personal-travel rule. I kept the clause set to PERSONAL_WITH_BUSINESS on purpose.
- **Soft connecting-flights reading.** "Expected to" plus "For Example ... should accept". Accepting only the
  connection inside the example and both offers outside it is the reading that fits the operator words. Both delay
  measures agree in every case.
- **Approvers.** Every BOOK accepts APPROVING_MANAGER and NONE, plus VICE_PRESIDENT in lark-meadow and
  MANAGING_DIRECTOR in plume-sorrel (4'(a')). Refusals accept NONE and APPROVING_MANAGER (4(b)). yarrow-glint accepts
  only VP/SVP, and the unclear holds accept only MD or NOT_NAMED. This all conforms to 4'.
- **Flags.** "not including connections or layovers" (vale-pewter): "connections" beside "layovers" can mean the
  connecting flights, so this is genuinely open. "international travel" (willow-cairn): undefined, while 3.6.1
  *Domestic* Travel Meals lists Toronto and Vancouver, so this is genuinely open, though weaker. Each flag has one
  phrase and clear twins on both sides. yarrow-glint is an approval hold, not an unclear text.
- **Twins.** fern-quarry/gull-ridge (361 against 360), hazel-tarn/iris-brook ($151 against $150) and
  juniper-slate/kestrel-dune (layover 90 against 91) each differ in one fact. Flight numbers and offer ids differ
  only cosmetically.
- **Residual risk, not fixed.** Lines 154-156 say "actual flying time", but the world gives scheduled minutes. The
  quote test rules out outside knowledge of taxi time, and the rule's docstring records the convention. A model
  could still balk at the 1-minute margin of fern-quarry.
- **Leaks.** No rule wording appears in task or tool text (`test_lint` passes), and the conventions line is the
  template's.

## Other changes

- `BUILD_NOTES.md` moved to `tests/` (stock `plugin inspect` rejects extra root files), and this file sits beside
  it. The README layout list is updated. BUILD_NOTES' blind-read rows for aspen-wharf and rowan-flint describe the
  pre-audit scenarios.
- README table rows for aspen-wharf, rowan-flint, vale-pewter and willow-cairn, the decision counts and the baseline
  sentence are updated.

## Acceptance outputs

```
uv run pytest -q                        208 passed
uv run ruff check .                     All checks passed!
uv lock --check                         Resolved 42 packages
python3 ../_template/check_shared.py .  : ok
nanoagent plugin inspect . (stock)      exit 0
nanoagent plugin pack . (stock)         packed (172,656 bytes)
stock_verify.py . (stock Python)        24 scenarios, 0 failures
```
