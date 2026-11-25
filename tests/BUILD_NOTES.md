# Build notes: fedex-office-flight-policy (wave 2, 2026-11-24)

Built to `pilot_work/tier_plan/build/WAVE2_BUILD_BRIEF.md` from the frozen handbook
`pilot_work/originals/fedex-office/frozen/fedex-office_policy.txt` (7,361 words, 965 lines, sha256 b9e3873f...b2770f1;
under 10,000 words, so 24 scenarios). Made with `_template/instantiate.py --slug fedex-office --task-id
book-fedex-office-flight --currency USD --background 0 --scenarios 24`. The user was asleep; every choice below is
the recommended one, taken without asking.

## Flight rules the handbook supports (frozen line numbers)

| Clause | Lines | Operator / kind | Used by |
|---|---|---|---|
| Lowest logical coach airfare is to be used | 135-137 | mandatory default | every economy case |
| Book for the lowest costs | 44-45 | general duty | accepted section on lowest-fare cases |
| One connection when least expensive; accept it when savings exceed $150 and the delay is not more than two hours | 129-133 | "exceed" strict, "not more than" inclusive; "expected to"/"should" | twins hazel-tarn/iris-brook, juniper-slate/kestrel-dune; briar-cove |
| VPs and above may fly first class | 138 | permission | dover-moss, sedge-copper (not taken), nettle-bay |
| First class for a pre-certified physical need, certified by VP or higher and sent to Global Travel | 139-144 | mandatory approver | lark-meadow, yarrow-glint |
| Upgrade to first by paying the difference | 145-149 | permission | mallow-pier |
| No upgrade to sit with an eligible colleague | 150-153 | prohibition | nettle-bay |
| Business class: international, actual flying time more than 6 hours, not including connections or layovers | 154-156 | "more than" strict | cinder-heath, fern-quarry/gull-ridge, oak-lantern, vale-pewter, willow-cairn |
| Exceptions under $10,000 by department MD, over by VP | 77-80 (+ 932-934) | mandatory approver; exactly $10,000 is a gap | plume-sorrel |
| 14-day advance booking | 121-124 | "should make every attempt" (soft) | rowan-flint (distractor) |
| Personal travel combined with business | 526-531 | payment rule | quince-harbor |
| Dependent travel not reimbursed unless communicated in advance for a company-sponsored event | 534-536, 827-828 | mandatory | umber-wick |
| Business guest/supplier air travel not paid in advance | 538-543 | mandatory | thistle-marsh |
| Airfare not reimbursed when insisting on a specific airline instead of a cheaper fare | 820-821 | mandatory | sedge-copper |
| Air travel authorized if booked through Global Travel and approved in advance | 760-762 | precondition | every trip record holds the approving manager's advance approval |

No overnight-stop, advance-purchase-ban, preferred-carrier, refundable-ban, rail or driving rule for flights exists, so
none is tested (no overnight overlay is required). The mileage "EXCEPTION" (lines 353-359) prefers flying over
driving but only matters for several Team Members driving together; it is in the clause list but no scenario uses it.

## Decisions taken (recommended choices)

1. **Duration measure** (lines 154-156). Strict "more than 6 hours" on scheduled minutes (the only flying time known
   at booking). Ground time never counts. Whether "not including connections" means the connecting flights are not
   added is unclear: one flight over 360 is over on every reading, flights summing to 360 or less are under on every
   reading, between is a flag (`vale-pewter`, the only scenario there).
2. **"International travel"** is undefined; Canada is listed under 3.6.1 *Domestic* Travel Meals and grouped with the
   US for car insurance. A Canada trip over 6 hours is a flag (`willow-cairn`). Puerto Rico (line 516, "outside the US
   and Canada ... includes Puerto Rico") is the same phrase, so no scenario goes there (one scenario per phrase).
   Hawaii is a US state and Honolulu is in the domestic meals list: domestic (`oak-lantern`).
3. **Connecting-flights rule is soft outside its example.** "Expected to" plus "For Example ... should accept": inside
   the example (savings > $150, delay <= 120) only the connection is accepted; outside it, for a traveller asking for
   the nonstop, both offers are accepted (EDGE_CASES fairness test 4). Delay is measured two ways (elapsed difference
   and arrival difference); every scenario makes them equal (same departure time) and `rules` raises if they ever
   disagree. Background offers are 0 on every connecting-flights case, so there is one nonstop to compare against
   (a first draft had background nonstops 70 minutes faster than the pinned one, which changed the delay; caught in
   the blind read and fixed).
4. **Rank.** "Vice Presidents and above": the trip record gives a `job_level`; VP, SVP, EVP and CEO are at or above. A
   Managing Director is ranked below a Vice-President by lines 729-739, but no traveller is an MD, so the case is never
   tested.
5. **Advance approval on every trip** (lines 760-762). Approvers follow SYNC_NOTES rule 4' (lead's message during the
   build): a BOOK accepts each sign-off on file it relies on (APPROVING_MANAGER; plus VICE_PRESIDENT in lark-meadow and
   MANAGING_DIRECTOR in plume-sorrel) and NONE; a REFUSE accepts NONE and APPROVING_MANAGER (4(b)); a hold accepts
   only the awaited role: VICE_PRESIDENT or SENIOR_VICE_PRESIDENT ("VP or higher level management") in yarrow-glint,
   NOT_NAMED or MANAGING_DIRECTOR (the exceptions approver under $10,000) in the two unclear holds.
6. **Exceptions** (plume-sorrel). A documented exception from the department MD lets a non-VP fly first; the first
   fare ($990) and its difference from coach are both far under $10,000, so the measure of an exception's amount
   (whole fare or difference) and the exactly-$10,000 gap never matter.
7. **Personal travel** (quince-harbor). The ticket is the one the traveller will fly (Friday); FXO pays the Monday
   business-only fare and the traveller pays the $91 more, so BOOK the cheapest Friday fare. Both dates are pinned
   searches; the trip record's `business_travel_date` names the business-only date.
8. **Reason codes.** Handbook codes: POLICY_EXCEPTION_APPROVED, BUSINESS_GUEST_NOT_PREPAID,
   PERSONAL_COST_PAID_BY_TRAVELER. Decoys (subjects grepped in the frozen text, none present or defensible):
   FLY_AMERICA_US_CARRIER_REQUIRED, OPEN_SKIES_AGREEMENT, CHANCELLOR_WRITTEN_AUTHORIZATION, CREATIVE_TICKETING,
   DOUBLE_BOOKING_PROHIBITED, PRIVATE_AIRCRAFT_NOT_APPROVED, DENIED_BOARDING_NOT_ALLOWED, EXTENDED_TRAVEL_SAVINGS.
   Dropped as decoys because the text touches their subject: WEEKEND_* (a personal weekend appears), NEXT_OF_KIN_TRAVEL
   (family travel), TRAVEL_PACKAGE_NOT_ITEMIZED (Global Travel Vacations packages), CANDIDATE_TRIP_NOT_COVERED
   (recruiting meals), AGENCY_EXEMPTION_NOT_MET (booking-agency rules), SAME_CLASS_AS_CUSTOMER ("same class of
   service", line 171).
9. **No round trips.** Every case is one way; `return_date` is empty everywhere.
10. **Degenerate baselines.** Always-flag passes 2 (the two unclear holds). Always-cheapest with LOWEST_FARE/NONE passes
    12 (every cheapest-economy case), the cost of rule 4' accepting NONE on bookings. `MAX_PASS_ALWAYS_LOWEST = 12`.

## Hosted-cap estimate

0.2 tokens a character of policy plus 1,800 (Thornton/NJC paid calibration): call 1 about 11,100 input tokens,
call 2 about 11,700, call 3 12,800-14,300; a 3-call run about 36,000-37,500 input tokens, about 52,000 with the final
message and output. Under the 65,536 hosted cap with about 13,000 to spare; one extra tool call reaches the cap.

## Blind read (non-flag scenarios), from the handbook text and the tool outputs only

I re-derived each answer from the frozen text and a dump of `get_trip`/`search_flights` (every offer, background
included), not from rules.py, after the background fix of decision 3.

| Scenario | My reading | Agrees |
|---|---|---|
| aspen-wharf | DL 06:15 sold out; cheapest seat UA 08:40 $214 economy (135-137) | yes |
| briar-cove | UA via DEN $248 vs AA nonstop $418: saves $170, arrives 95 min later; traveller is open to connecting: connection | yes |
| cinder-heath | ORD-FRA nonstops 515/520 min, international > 6 h, business asked: UA business $3,980 | yes |
| dover-moss | VP asks first: cheapest first UA $1,185 (138) | yes |
| elm-garnet | 650+ min international, but economy asked: JL $912 | yes |
| fern-quarry | 361 min > 360: business, EI $2,890 | yes |
| gull-ridge | 360 min not more than 6 h: economy EI $614 | yes |
| hazel-tarn | saves $151 (> $150), 100 min later (<= 2 h): connection only, despite nonstop wish | yes |
| iris-brook | saves exactly $150 (not over): outside the example; nonstop wish: nonstop or connection | yes |
| juniper-slate | saves $240, exactly 120 min later (not more than two hours): connection only | yes |
| kestrel-dune | 121 min later: outside the example; nonstop or connection | yes |
| lark-meadow | Director, physical need, VP certification sent to agency: first, AS $980 (139-144) | yes |
| mallow-pier | Manager pays the difference: first, DL $1,165 (145-149) | yes |
| nettle-bay | Director with VP for an inflight meeting, not paying: coach, UA $274 on the VP's flight (150-153) | yes |
| oak-lantern | Honolulu is domestic (US state; domestic meals list): coach UA $684 though 655 min | yes |
| plume-sorrel | Department MD documented exception, under $10,000: first AA $990 (77-78) | yes |
| quince-harbor | personal Friday, pays the difference over Monday's $198: cheapest Friday AS $289 (526-531) | yes |
| rowan-flint | 9 days ahead is soft (121-124): cheapest non-refundable DL $268 | yes |
| sedge-copper | VP asks economy on United; cheaper AA $339 (820-821); FF benefits (498) do not change it | yes |
| thistle-marsh | supplier: not paid in advance, invoice later (538-543): REFUSE | yes |
| umber-wick | husband on a customer trip, not a company-sponsored event: REFUSE (534-536) | yes |

All 21 non-flag scenarios agree. Least certain (two-reader risk): plume-sorrel (a reader might hold the MD exception
as not overriding 3.3.3, though 3.1.2 and 4.2.1 give the MD that power) and quince-harbor (a reader might book the
Monday business-only fare; the traveller will not fly it).

## Template change requests

None blocking. Observation: the shared lint and `tests/test_duration.py` only model absolute duration thresholds, so
the connecting-flights delay ("more than two hours" later than the nonstop) is coded as a constant in rules.py and
tested only through its twin pair; a shared hook for relative delays could help other handbooks with the same clause.

## Acceptance outputs (final)

```
$ uv run pytest -q
208 passed in 1.93s
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 9ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .  (stock checkout)
exit 0 ; id fedex-office-flight-policy tools 4 tasks 3
$ nanoagent plugin pack . /tmp/fedex-office-flight-policy.tar.gz  (stock checkout)
packed . into /tmp/fedex-office-flight-policy.tar.gz (168283 bytes)
$ python ../_template/tools/stock_verify.py .  (stock checkout Python)
aspen-wharf          right=True score=1.00 identical=True wrong-decision-rejected=True
briar-cove           right=True score=1.00 identical=True wrong-decision-rejected=True
cinder-heath         right=True score=1.00 identical=True wrong-decision-rejected=True
dover-moss           right=True score=1.00 identical=True wrong-decision-rejected=True
elm-garnet           right=True score=1.00 identical=True wrong-decision-rejected=True
fern-quarry          right=True score=1.00 identical=True wrong-decision-rejected=True
gull-ridge           right=True score=1.00 identical=True wrong-decision-rejected=True
hazel-tarn           right=True score=1.00 identical=True wrong-decision-rejected=True
iris-brook           right=True score=1.00 identical=True wrong-decision-rejected=True
juniper-slate        right=True score=1.00 identical=True wrong-decision-rejected=True
kestrel-dune         right=True score=1.00 identical=True wrong-decision-rejected=True
lark-meadow          right=True score=1.00 identical=True wrong-decision-rejected=True
mallow-pier          right=True score=1.00 identical=True wrong-decision-rejected=True
nettle-bay           right=True score=1.00 identical=True wrong-decision-rejected=True
oak-lantern          right=True score=1.00 identical=True wrong-decision-rejected=True
plume-sorrel         right=True score=1.00 identical=True wrong-decision-rejected=True
quince-harbor        right=True score=1.00 identical=True wrong-decision-rejected=True
rowan-flint          right=True score=1.00 identical=True wrong-decision-rejected=True
sedge-copper         right=True score=1.00 identical=True wrong-decision-rejected=True
thistle-marsh        right=True score=1.00 identical=True wrong-decision-rejected=True
umber-wick           right=True score=1.00 identical=True wrong-decision-rejected=True
vale-pewter          right=True score=1.00 identical=True wrong-decision-rejected=True
willow-cairn         right=True score=1.00 identical=True wrong-decision-rejected=True
yarrow-glint         right=True score=1.00 identical=True wrong-decision-rejected=True
24 scenarios, 0 failures
```
