"""The answer key's rules for the FedEx Office Travel and Business Expense Policy (updated January 19, 2015), as
exact integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only modules a
verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The duration hook. Lines 154-156: "Business class may be used for international travel, if actual flying
time is more than 6 hours, not including connections or layovers." The limit is strict ("more than"): over
at 361 scheduled minutes, not at 360. The ground time between flights never counts. The text does not say
whether the flying time of an itinerary with a connection is its flights added together or each flight on
its own ("not including connections" may mean the connecting flights): when one flight alone is over 360
minutes every reading agrees (over); when the flights added together are 360 or less every reading agrees
(not over); otherwise the reading is unclear (None). A nonstop is never unclear. The world's scheduled
minutes stand for "actual flying time": nothing else is known when the ticket is bought.

The other numbers of the air section are not flight durations and are coded below: the connecting-flights
example of lines 129-133 ("savings exceed $150", strict; "a delay of more than two hours travel time", so
120 minutes is still within) and the exceptions limit of lines 77-80.

Approvers. Line 760-762 make air travel an authorized expense only "if booked through Global Travel and
approved in advance"; every trip record holds that advance approval by the traveller's approving manager.
Under the template's rule 4' (SYNC_NOTES.md), a booking whose sign-offs are already on file accepts each of
those roles and NONE; a refusal does not use the trip approval, so it too accepts NONE and APPROVING_MANAGER
(rule 4(b)); a hold accepts only the role it awaits (NOT_NAMED where the handbook names none).
"""

from contract import (
    Approver,
    Cabin,
    Clause,
    Decision,
    JobLevel,
    Passenger,
    Purpose,
    ReasonCode,
    Routing,
    SignOffSubject,
)

from .world import days_between, utc_minute

HANDBOOK = "FedEx Office Travel and Business Expense Policy, updated January 19, 2015"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.POLICY_GENERAL: "3.1 Travel and Business Expense Policy",
    Clause.EXPENSE_APPROVAL: "3.1.1 Expense Reporting and Approval Process",
    Clause.EXCEPTIONS: "3.1.2 Exceptions",
    Clause.TRAVEL_ARRANGEMENTS: "3.2 Travel Arrangements and Expenses",
    Clause.BOOKING_FEES: "3.2.3 Booking Fees",
    Clause.EN_ROUTE_CHANGES: "3.2.4 Emergency/En Route Changes",
    Clause.TRAVELERS_WITH_DISABILITIES: "3.2.5 Travelers with Disabilities",
    Clause.AIR_TRAVEL: "3.3 Air Travel",
    Clause.DOMESTIC_TICKETS: "3.3.1 Domestic Airline Tickets",
    Clause.CONNECTING_FLIGHTS: "3.3.2 Connecting Flights",
    Clause.CLASS_OF_SERVICE: "3.3.3 Domestic, International Class of Service and Upgrades",
    Clause.CANCELLATIONS: "3.3.4 Cancellations",
    Clause.SEAT_CHANGES: "3.3.5 Seat Changes",
    Clause.BAGGAGE_FEES: "3.3.6 Baggage Fees",
    Clause.DOMESTIC_MEALS: "3.6.1 Domestic Travel Meals",
    Clause.INTERNATIONAL_MEALS: "3.6.2 International Travel Meals",
    Clause.MILEAGE_EXCEPTION: "EXCEPTION to Mileage Reimbursement:",
    Clause.NON_PAID_LOYALTY: "3.8.3 Non-paid Loyalty Clubs",
    Clause.CAR_INSURANCE: "3.9.1 Car",
    Clause.PERSONAL_WITH_BUSINESS: "3.10.1 Personal Travel with Business Travel",
    Clause.DEPENDENT_TRAVEL: "3.10.2 Dependent Travel",
    Clause.BUSINESS_GUESTS: "3.10.3 Business Guests/Suppliers",
    Clause.GROUP_TRAVEL: "3.13 Group, Meeting and Training Travel",
    Clause.SIGNING_AUTHORITY: "3.13.3 Contract signing authority:",
    Clause.REIMBURSABLE_SUMMARY: "3.15 Summary Reimbursable Charges",
    Clause.NON_REIMBURSABLE: "3.16 Non-Reimbursable Charges",
    Clause.ACCOUNTABILITY: "4.2.1 Senior Vice President, Vice President and/or Managing Director",
}

# The handbook's duration thresholds (the per-handbook duration hook; tests/test_duration.py tests both
# sides of each). ">" is strict ("more than").
DURATION_RULES = (
    {"name": "international-business", "minutes": 360, "operator": ">", "lines": [154, 156],
     "quote": "Business class may be used for international travel, if actual flying time is more than 6 hours, "
              "not including connections or layovers."},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Lines 129-133: "Team Members should accept a connecting flight when the savings exceed $150 and the
# connection does not cause a delay of more than two hours travel time" (one connection per trip).
SAVINGS_CENTS = 15_000
DELAY_MINUTES = 120
MOST_CONNECTIONS = 1
# Lines 77-80: exceptions "less than $10,000" are approved by the department MD, "greater than $10,000" by
# the department VP.
EXCEPTION_LIMIT_CENTS = 1_000_000
# Line 138: "Vice Presidents and above may fly first class." The ranks at or above Vice President (lines
# 729-739 rank a Managing Director below a Vice-President).
SENIOR_LEVELS = (JobLevel.VICE_PRESIDENT, JobLevel.SENIOR_VICE_PRESIDENT, JobLevel.EXECUTIVE_VICE_PRESIDENT,
                 JobLevel.CHIEF_EXECUTIVE)
# Lines 142-144: a first-class certification "must be approved by their VP or higher level management".
CERTIFIERS = (Approver.VICE_PRESIDENT, Approver.SENIOR_VICE_PRESIDENT, Approver.CHIEF_EXECUTIVE)
# Lines 298-305: the "High Cost Cities" list of 3.6.1 Domestic Travel Meals names Anchorage and Honolulu.
LISTED_DOMESTIC = ("ANC", "HNL")

UNCLEAR_REASONS = [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED]
CONNECTIONS_PHRASE = "not including connections or layovers"
INTERNATIONAL_PHRASE = "international travel"


def over(rule, offer):
    """True, False or None (unclear): whether ``offer``'s flights out are over the handbook's ``rule``."""
    if rule != "international-business":
        raise ValueError(f"unknown duration rule {rule!r}")
    if offer.return_segments:
        raise ValueError("a round trip is not modelled by this handbook's scenarios")
    limit = LIMITS[rule]
    flights = [segment.scheduled_minutes for segment in offer.segments]
    if max(flights) > limit:
        return True
    return False if sum(flights) <= limit else None


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def one(offers, what):
    if len(offers) != 1:
        raise ValueError(f"{what}: {len(offers)} offers tie or none is listed; not modelled")
    return offers[0]


def signed(trip, subject):
    return [record for record in trip.sign_offs if record.subject == subject]


def on_route(trip, offers, date):
    return [offer for offer in offers if offer.segments[0].origin == trip.origin.code
            and offer.segments[-1].destination == trip.destination.code and offer.segments[0].depart_local[:10] == date]


def connection_choice(trip, economy):
    """The economy offers the handbook accepts and their reasons and extra sections. Lines 135-137: the lowest
    logical coach airfare. Lines 129-133: one connection per trip is expected when it is the least expensive
    option, and a connection is to be accepted when it saves more than $150 and delays the travel by no more
    than two hours. Outside that example the text gives no rule, so for a traveller who asks for the nonstop
    both the cheaper connection and the nonstop are accepted."""
    low = cheapest(economy)
    if not low:
        raise ValueError("no economy offer can be bought")
    if any(offer.stops > MOST_CONNECTIONS for offer in low):
        raise ValueError("a cheapest fare with two or more connections is not modelled")
    nonstops = cheapest([offer for offer in economy if offer.stops == 0])
    if all(offer.stops == 0 for offer in low) or not nonstops:
        return low, [ReasonCode.LOWEST_FARE], [], "lines 135-137: the lowest logical coach airfare"
    connection, nonstop = one(low, "cheapest connection"), one(nonstops, "cheapest nonstop")
    savings = nonstop.fare_cents - connection.fare_cents
    delays = {connection.elapsed_minutes - nonstop.elapsed_minutes,
              utc_minute(connection.segments[-1].arrive_utc) - utc_minute(nonstop.segments[-1].arrive_utc)}
    if len({delay <= DELAY_MINUTES for delay in delays}) != 1:
        raise ValueError("a delay that is within two hours on one measure and over on another is not modelled")
    delay = max(delays)
    if savings > SAVINGS_CENTS and delay <= DELAY_MINUTES:
        reasons = [ReasonCode.COST_SAVINGS, ReasonCode.ALTERNATE_ROUTE_TOO_EXPENSIVE]
        # A nonstop the traveller asked for is declined on the example's savings and delay test (a $150 saving
        # alone keeps it, iris-brook), so the reason names that test and LOWEST_FARE is not accepted; a traveller
        # who asked for nothing gets the lowest logical fare, and LOWEST_FARE names it.
        if trip.requested_routing != Routing.NONSTOP:
            reasons.append(ReasonCode.LOWEST_FARE)
        return ([connection], reasons, [Clause.CONNECTING_FLIGHTS],
                (f"lines 129-133: the one-connection fare saves {savings} cents (more than $150) and delays the travel "
                f"{delay} minutes (not more than two hours), so the connection is to be accepted"))
    if trip.requested_routing != Routing.NONSTOP:
        raise ValueError("a cheaper connection outside the example, for a traveller who did not ask for the nonstop, "
                         "is not modelled")
    reasons = [ReasonCode.LOWEST_FARE, ReasonCode.COST_SAVINGS, ReasonCode.ALTERNATE_ROUTE_WITHIN_MARGIN]
    if delay > DELAY_MINUTES:
        reasons.append(ReasonCode.CONNECTION_TOO_LONG)
    return ([connection, nonstop], reasons, [Clause.CONNECTING_FLIGHTS],
            (f"lines 129-133: the connection saves {savings} cents and delays the travel {delay} minutes, outside the "
            "handbook's example (savings over $150 and no more than two hours), so the requested nonstop and the "
            "cheaper connection are both accepted"))


LOWEST_CLAUSES = [Clause.CLASS_OF_SERVICE, Clause.AIR_TRAVEL, Clause.POLICY_GENERAL]
CLASS_CLAUSES = [Clause.CLASS_OF_SERVICE, Clause.AIR_TRAVEL]


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its searches: the decision, and every accepted offer id,
    cabin, reason, approver and section. ``hidden`` (the scenario's answer_key_inputs) is unused by this
    handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if trip.return_date:
        raise ValueError("a round-trip ticket is not modelled")
    trip_roles = [record.role for record in signed(trip, SignOffSubject.TRIP)]
    if trip_roles != [Approver.APPROVING_MANAGER]:
        raise ValueError("every case holds one advance trip approval by the approving manager (lines 760-762)")
    unused = [Approver.NONE, *trip_roles]
    # Rule 4': a booking accepts NONE beside every sign-off on file that it relies on.
    trip_roles = [Approver.NONE, *trip_roles]
    if trip.passenger in (Passenger.SUPPLIER, Passenger.BUSINESS_GUEST):
        return answer(Decision.REFUSE, [], [ReasonCode.BUSINESS_GUEST_NOT_PREPAID, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      unused, [Clause.BUSINESS_GUESTS],
                      "Lines 538-540: air travel expenses for a business guest or supplier will not be paid in advance "
                      "by FXO; lines 541-543: a supplier invoices the company afterwards. The company buys no ticket.")
    if trip.passenger == Passenger.SPOUSE_OR_FAMILY:
        if trip.purpose_kind == Purpose.COMPANY_SPONSORED_EVENT and trip.told_company_beforehand:
            raise ValueError("a family member at a company-sponsored event, told in advance, is not modelled")
        return answer(Decision.REFUSE, [], [ReasonCode.COMPANION_NOT_COVERED, ReasonCode.PERSONAL_TRAVEL_NOT_COVERED],
                      unused, [Clause.DEPENDENT_TRAVEL, Clause.NON_REIMBURSABLE],
                      "Lines 534-536 and 827-828: travel expenses for family or significant others are the Team "
                      "Member's own, unless communicated in advance for a company-sponsored event, which this is not. "
                      "The company buys no ticket.")
    if trip.passenger != Passenger.EMPLOYEE or trip.purpose_kind == Purpose.PERSONAL:
        raise ValueError("only employees on company business are modelled beyond the two refusals")
    if trip.origin.country != trip.home_country:
        raise ValueError("a trip that does not start in the traveller's home country is not modelled")
    travel = on_route(trip, offers, trip.travel_date)
    seated = [offer for offer in travel if offer.seats_available]
    economy = [offer for offer in seated if offer.cabin == Cabin.ECONOMY]
    if trip.business_travel_date != trip.travel_date:
        return personal(trip, offers, economy, trip_roles)
    if trip.requested_cabin == Cabin.FIRST:
        return first_request(trip, seated, economy, trip_roles)
    if trip.requested_cabin == Cabin.BUSINESS:
        return business_request(trip, seated, economy, trip_roles)
    if trip.requested_cabin != Cabin.ECONOMY or trip.traveller_pays_difference:
        raise ValueError("this economy request is not modelled")
    return economy_request(trip, economy, trip_roles)


def economy_request(trip, economy, trip_roles):
    chosen, reasons, clauses, note = connection_choice(trip, economy)
    clauses = [*LOWEST_CLAUSES, *clauses]
    notes = [note]
    if trip.requested_airline:
        # Lines 820-821 decline the airline because a cheaper fare exists: the ground is the lowest-fare rule itself,
        # so LOWEST_FARE stays beside LOYALTY_PROGRAM_PREFERENCE.
        if all(offer.carrier == trip.requested_airline for offer in chosen):
            raise ValueError("an airline wish that the lowest fare already meets is not modelled")
        reasons.append(ReasonCode.LOYALTY_PROGRAM_PREFERENCE)
        clauses.append(Clause.NON_REIMBURSABLE)
        notes.append("lines 820-821: airfare is not reimbursed when a Team Member insists on a specific airline "
                     "instead of a cheaper fare")
    domestic = trip.origin.country == trip.destination.country == trip.home_country
    if domestic and days_between(trip.booking_date, trip.travel_date) < 14:
        clauses.append(Clause.DOMESTIC_TICKETS)
        notes.append("lines 121-124: booking 14 days ahead is something to attempt, not a ban, and the cheapest fare "
                     "listed can still be bought")
    return answer(Decision.BOOK, chosen, reasons, trip_roles, clauses, "; ".join(notes) + "; lines 760-762: the trip "
                  "is approved in advance.")


def ineligible(trip, economy, trip_roles, why):
    """A better cabin the traveller may not have: the lowest logical coach airfare instead."""
    chosen, reasons, clauses, note = connection_choice(trip, economy)
    if clauses or reasons != [ReasonCode.LOWEST_FARE]:
        raise ValueError("a refused upgrade whose coach fare turns on the connecting-flights rule is not modelled")
    # The reason names why the cabin is declined, so LOWEST_FARE (the coach fare's own reason) is not accepted.
    return answer(Decision.BOOK, chosen, [ReasonCode.UPGRADE_NOT_ELIGIBLE], trip_roles,
                  [*LOWEST_CLAUSES], f"{why}; {note}.")


def first_request(trip, seated, economy, trip_roles):
    """Lines 138-153: who may fly first class."""
    first = cheapest([offer for offer in seated if offer.cabin == Cabin.FIRST])
    if not first:
        raise ValueError("a first-class request with no first-class seat is not modelled")
    if trip.job_level in SENIOR_LEVELS:
        return answer(Decision.BOOK, first, [ReasonCode.SENIOR_ROLE_ENTITLEMENT], trip_roles, CLASS_CLAUSES,
                      "Line 138: Vice Presidents and above may fly first class; the cheapest first-class fare.")
    certificates = signed(trip, SignOffSubject.FIRST_CLASS_CERTIFICATION)
    if trip.physical_need_on_file or certificates:
        if not (trip.physical_need_on_file and certificates and all(c.on_file_with_agency for c in certificates)):
            raise ValueError("a physical need without a certification sent to the agency is not modelled")
        valid = [record.role for record in certificates if record.role in CERTIFIERS]
        if valid:
            return answer(Decision.BOOK, first, [ReasonCode.MEDICAL_NEED], [*trip_roles, *valid], CLASS_CLAUSES,
                          "Lines 139-144: the traveller is pre-certified for first class on a physical condition, the "
                          "certification approved by their VP and sent to the travel agency before booking.")
        return answer(Decision.FLAG_FOR_APPROVAL, first, [ReasonCode.APPROVAL_REQUIRED, ReasonCode.MEDICAL_NEED],
                      [Approver.VICE_PRESIDENT, Approver.SENIOR_VICE_PRESIDENT], CLASS_CLAUSES,
                      "Lines 142-144: the first-class certification must be approved by the traveller's VP or higher "
                      "level management before a flight can be booked in a higher class; it was approved by someone "
                      "below VP, so hold the first-class fare for the VP.")
    if trip.traveller_pays_difference:
        return answer(Decision.BOOK, first, [ReasonCode.TRAVELER_PAYS_UPGRADE], trip_roles, CLASS_CLAUSES,
                      "Lines 145-149: a Team Member may upgrade to first class by personally paying the difference from "
                      "the best available coach fare at ticketing; the cheapest first-class fare.")
    exceptions = signed(trip, SignOffSubject.POLICY_EXCEPTION)
    if exceptions:
        coach = cheapest(economy)
        if [record.role for record in exceptions] != [Approver.MANAGING_DIRECTOR] or not coach:
            raise ValueError("an exception not signed by the department MD alone is not modelled")
        if first[0].fare_cents >= EXCEPTION_LIMIT_CENTS:
            raise ValueError("an exception of $10,000 or more is not modelled")
        return answer(Decision.BOOK, first, [ReasonCode.POLICY_EXCEPTION_APPROVED],
                      [*trip_roles, Approver.MANAGING_DIRECTOR], [Clause.EXCEPTIONS, Clause.ACCOUNTABILITY],
                      "Lines 77-78: an exception to the policy of less than $10,000 (the whole first-class fare and its "
                      "difference from coach are both under it) approved by the Team Member's department MD; lines "
                      "932-934: the MD approves exception requests.")
    why = "Line 138: only Vice Presidents and above may fly first class, and no certification, own payment or exception applies"
    if any(colleague.job_level in SENIOR_LEVELS for colleague in trip.travelling_with):
        why = ("Lines 150-153: a Team Member ineligible for first class who travels with an eligible one cannot upgrade "
               "to first class to conduct an inflight meeting")
    return ineligible(trip, economy, trip_roles, why)


def business_request(trip, seated, economy, trip_roles):
    """Lines 154-156: business class for international travel of more than 6 hours of flying time."""
    if trip.job_level in SENIOR_LEVELS or trip.traveller_pays_difference:
        raise ValueError("a business request from a first-class-eligible or paying traveller is not modelled")
    countries = {trip.origin.country, trip.destination.country}
    if countries == {trip.home_country}:
        result = ineligible(trip, economy, trip_roles,
                            "Lines 154-156: business class is for international travel; this trip is domestic")
        if trip.destination.code in LISTED_DOMESTIC:
            result["clauses"] = by_value([*result["clauses"], Clause.DOMESTIC_MEALS])
            result["explanation"] += " Lines 298-305 list the destination among the domestic high cost cities."
        result["reason_codes"] = by_value([*result["reason_codes"], ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET])
        return result
    verdicts = {over("international-business", offer) for offer in seated}
    if len(verdicts) != 1:
        raise ValueError("offers on different sides of the 6-hour limit are not modelled (set background 0)")
    verdict = verdicts.pop()
    business = cheapest([offer for offer in seated if offer.cabin == Cabin.BUSINESS])
    unclear_roles = [Approver.NOT_NAMED, Approver.MANAGING_DIRECTOR]
    # A hold over unclear words that names the MD as the role it may await may also give APPROVAL_REQUIRED.
    if trip.home_country == "US" and countries == {"US", "CA"}:
        if verdict is not True or not business:
            raise ValueError("a Canada trip within 6 hours, or without business seats, is not modelled")
        return answer(Decision.FLAG_FOR_APPROVAL, business, UNCLEAR_REASONS, unclear_roles,
                      [*CLASS_CLAUSES, Clause.DOMESTIC_MEALS],
                      "Lines 154-156 allow business class for international travel over 6 hours of flying, but the "
                      "handbook does not define international, lists Toronto and Vancouver among the high cost cities "
                      "of 3.6.1 Domestic Travel Meals (lines 298-305) and groups the US and Canada together (lines "
                      "515-516): a flight to Canada may be international or domestic. No role is named; under the "
                      "domestic reading business would be an exception for the department MD (lines 77-78).",
                      phrase=INTERNATIONAL_PHRASE)
    if verdict is False:
        result = ineligible(trip, economy, trip_roles,
                            "Lines 154-156: the flying time is not more than 6 hours, so business class is not available")
        result["reason_codes"] = by_value([*result["reason_codes"], ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET])
        return result
    if not business:
        raise ValueError("a business request with no business seat is not modelled")
    if verdict is None:
        return answer(Decision.FLAG_FOR_APPROVAL, business, UNCLEAR_REASONS, unclear_roles,
                      CLASS_CLAUSES,
                      "Lines 154-156: no single flight is over 6 hours, but the flights added together are; the handbook "
                      "says the flying time does 'not include connections or layovers' and does not say whether the "
                      "connecting flights are added. No role is named; under the per-flight reading business would be "
                      "an exception for the department MD (lines 77-78).", phrase=CONNECTIONS_PHRASE)
    if any(offer.stops for offer in business):
        raise ValueError("a business fare on a connection is not modelled")
    return answer(Decision.BOOK, business, [ReasonCode.INTERNATIONAL_LONG_FLIGHT], trip_roles, CLASS_CLAUSES,
                  "Lines 154-156: international travel with more than 6 hours of flying time may use business class; "
                  "the cheapest business fare.")


def personal(trip, offers, economy, trip_roles):
    """Lines 525-531: personal travel combined with business travel. FXO pays the least expensive routing for
    the business trip as if no personal travel were included; any additional cost is the Team Member's."""
    if trip.requested_cabin != Cabin.ECONOMY or trip.requested_airline:
        raise ValueError("a personal combination outside economy is not modelled")
    wanted = cheapest(economy)
    if not wanted or any(offer.stops for offer in wanted):
        raise ValueError("a personal-date fare that is not a nonstop is not modelled")
    alone = [offer for offer in on_route(trip, offers, trip.business_travel_date)
             if offer.seats_available and offer.cabin == Cabin.ECONOMY]
    base = cheapest(alone)
    if not base:
        raise ValueError("the business-only fare must be on a pinned search")
    if wanted[0].fare_cents <= base[0].fare_cents or not trip.traveller_pays_difference:
        raise ValueError("only a dearer personal date with the traveller paying the difference is modelled")
    extra = wanted[0].fare_cents - base[0].fare_cents
    return answer(Decision.BOOK, wanted, [ReasonCode.PERSONAL_COST_PAID_BY_TRAVELER, ReasonCode.LOWEST_FARE], trip_roles,
                  [Clause.PERSONAL_WITH_BUSINESS],
                  f"Lines 525-531: the traveller combines personal days with the approved business trip; FXO pays the "
                  f"least expensive business-only fare ({base[0].fare_cents} cents) and the traveller pays the "
                  f"{extra} cents more of the cheapest fare on the day they choose, which is the ticket booked.")
