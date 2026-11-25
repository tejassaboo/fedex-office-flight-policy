"""Writes the FedEx Office scenario JSON files (an authoring aid, not a test; the JSON files are the truth).

    uv run python tests/build_scenarios.py

Flight numbers that a trip record refers to (a colleague's flight) are read from the shared world, so they
match what search_flights lists. Expected answers are hand-written here; tests/test_scenarios.py checks them
against rules.solve.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from plugin.world import pinned_offers

POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses the answers rest on -----
LOW_COSTS = keep(44, 45, "Book travel in advance and in such a manner to allow for the lowest costs.",
                 "the general duty: book for the lowest costs")
LOWEST = keep(135, 137, "The lowest logical coach airfare is to be used when traveling on company business.",
              "the default: the lowest logical coach airfare")
APPROVED = keep(760, 762, None, "air travel is authorized when booked through Global Travel and approved in advance")
CONNECT = keep(129, 133, None, "one connection when least expensive; accept it when it saves over $150 and delays no "
               "more than two hours")
VP_FIRST = keep(138, 138, "Vice Presidents and above may fly first class.", "first class for VPs and above")
CERTIFIED = keep(139, 144, None, "first class for a pre-certified physical need, certified by the VP or higher and sent "
                 "to Global Travel before booking")
SELF_PAY = keep(145, 149, None, "a Team Member may upgrade to first by paying the difference at ticketing")
NO_RIDE_ALONG = keep(150, 153, None, "no upgrade to sit with an eligible colleague for an inflight meeting")
BUSINESS = keep(154, 156, "Business class may be used for international travel, if actual flying time is more than 6 "
                "hours, not including connections or layovers.", "business class: international, over 6 hours flying")
EXCEPTIONS = keep(77, 80, None, "exceptions under $10,000 are approved by the department MD")
EXCEPTION_ROLE = keep(932, 934, None, "the SVP, VP and/or MD approve exception requests")
HIGH_COST = keep(298, 305, None, "the domestic meals list of high cost cities names Honolulu, Toronto and Vancouver")
CAR_CANADA = keep(515, 516, None, "the car-insurance rule groups the US and Canada together")
PERSONAL = keep(526, 531, None, "FXO pays the business-only routing; the traveller pays any additional cost")
DEPENDENT = keep(534, 536, None, "family travel is the Team Member's, unless communicated in advance for a "
                 "company-sponsored event")
DEPENDENT_LIST = keep(827, 828, None, "the non-reimbursable list repeats it")
GUEST = keep(538, 543, None, "a business guest's or supplier's air travel is not paid in advance; suppliers invoice")
INSIST = keep(820, 821, "Airfare if a Team Member insists on traveling on a specific airline instead of using a cheaper "
              "fare", "insisting on an airline instead of a cheaper fare is not reimbursed")
DOMESTIC_ADVANCE_ASIDE = aside(121, 122, "Team Members should make every attempt to book travel at least 14 days in "
                               "advance", "booking 14 days ahead is an attempt to make, not a ban, and not a cabin rule")

# ----- nearby clauses that must not change the answer -----
FREQUENT = aside(498, 498, "Team Members may retain frequent flyer program benefits.",
                 "the traveller keeps miles, but that does not choose the fare")
FEES = aside(125, 127, "Any fees associated with tickets changed, exchanged, canceled or refunded will be charged to "
             "the Team Member's American Express/One card.", "change fees, not booking")
SEAT_UPGRADE = aside(174, 175, "Team Members will not be reimbursed for fees charged for upgrades to a higher class of "
                     "service or for segment upgrades.", "the company does not pay upgrade fees: the traveller does")
NR_UPGRADES = aside(815, 815, "Upgrades on airline tickets, except for Vice Presidents and above",
                    "upgrades are not reimbursed; it does not stop a traveller paying their own")
SHUTTLE = aside(555, 557, "Airport shuttle service (i.e., Super Shuttle) or taxis may be a more economical option than "
                "airport parking for business trips longer than four days.", "a trip-length rule for parking")
BAGS = aside(822, 823, "Fees for additional baggage (over two) or baggage weighing over 50 pounds",
             "a baggage rule, not a fare rule")
LATE = aside(640, 641, "Any exception for payment of charges submitted after 90 days may require SVP approval.",
             "a day count for expense claims, not for booking")
INSURANCE = aside(515, 516, "Team Members are reimbursed for rental car insurance when the car is used outside the US "
                  "and Canada.", "a car-insurance rule")
ROOMS = aside(720, 720, "Needing 10 or more sleeping rooms per day", "what makes a meeting; not a booking rule")

# ----- builders -----


def trip(approver_name="Dana Whitfield", **fields):
    base = {
        "traveller_name": "", "traveller_title": "", "job_level": "MANAGER", "passenger": "EMPLOYEE",
        "accompanies": "", "home_country": "US", "origin": "", "destination": "", "travel_date": "",
        "business_travel_date": "", "return_date": "", "booking_date": "", "purpose": "",
        "purpose_kind": "CUSTOMER_VISIT", "requested_cabin": "ECONOMY", "requested_routing": "ANY",
        "requested_airline": "", "traveller_pays_difference": False, "physical_need_on_file": False,
        "told_company_beforehand": False, "sign_offs": None, "travelling_with": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    if not base["business_travel_date"]:
        base["business_travel_date"] = base["travel_date"]
    if base["sign_offs"] is None:
        base["sign_offs"] = []
    base["sign_offs"] = [approval(approver_name)] + base["sign_offs"]
    return base


def approval(name):
    return {"role": "APPROVING_MANAGER", "name": name, "subject": "TRIP",
            "covers": "The business trip, approved in advance", "on_file_with_agency": True}


def sign(role, name, subject, covers, on_file=True):
    return {"role": role, "name": name, "subject": subject, "covers": covers, "on_file_with_agency": on_file}


def offer(slot, flight, cabin, cents, seats=True, refundable=False):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    if refundable:
        data["refundable"] = True
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": slots, "cabins": cabins, "reason_codes": sorted(reasons),
            "approvers": sorted(approvers), "clauses": sorted(clauses), "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers, background=3, name="main"):
    return {"name": name, "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": background, "flights": flights, "offers": offers}


def first_flight(scenario_id, search_spec, slot):
    for name, made in pinned_offers(scenario_id, search_spec):
        if name == slot:
            return made.segments[0].flight_number
    raise KeyError(slot)


S = []


def scenario(id, category, overlays, request, trip_, searches, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    if isinstance(searches, dict):
        searches = [searches]
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": searches}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


AM = ["APPROVING_MANAGER", "NONE"]  # rule 4': the advance trip approval on file, or NONE
LOW_CLAUSES = ["AIR_TRAVEL", "CLASS_OF_SERVICE", "POLICY_GENERAL"]
CLASS = ["AIR_TRAVEL", "CLASS_OF_SERVICE"]
LOW = [LOWEST, LOW_COSTS, APPROVED]
CLEAR_CONNECTION = ["ALTERNATE_ROUTE_TOO_EXPENSIVE", "COST_SAVINGS", "LOWEST_FARE"]
OPEN_CONNECTION = ["ALTERNATE_ROUTE_WITHIN_MARGIN", "COST_SAVINGS", "LOWEST_FARE"]
NO_UPGRADE = ["UPGRADE_NOT_ELIGIBLE"]
NOT_LONG = ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"]
UNCLEAR_ROLES = ["MANAGING_DIRECTOR", "NOT_NAMED"]

# ===== easy (5) =====

scenario(
    "aspen-wharf", "easy", ["dearer_option"],
    "I'm flying Atlanta to Chicago O'Hare on January 14th for the regional operations review the next morning. First "
    "class, please.",
    trip(traveller_name="Marcus Bell", traveller_title="Senior Vice President, Retail Operations",
         job_level="SENIOR_VICE_PRESIDENT", origin="ATL", destination="ORD", travel_date="2027-01-14",
         booking_date="2026-12-02", purpose="Regional operations review in Chicago", purpose_kind="INTERNAL_MEETING",
         requested_cabin="FIRST", approver_name="Raymond Cho"),
    search("ATL", "ORD", "2027-01-14", {
        "early": {"carrier": "DL", "depart": "06:15"},
        "morning": {"carrier": "UA", "depart": "08:40"},
        "midday": {"carrier": "AA", "depart": "11:05"},
    }, [
        offer("early-economy", "early", "ECONOMY", 18900),
        offer("early-first", "early", "FIRST", 61500, seats=False),
        offer("morning-economy", "morning", "ECONOMY", 21400),
        offer("morning-first", "morning", "FIRST", 64800),
        offer("midday-economy", "midday", "ECONOMY", 22900),
        offer("midday-first", "midday", "FIRST", 69900),
    ]),
    expected("BOOK", ["morning-first"], ["FIRST"], ["SENIOR_ROLE_ENTITLEMENT"], AM, CLASS),
    [VP_FIRST, APPROVED],
    "A Senior Vice President is above a Vice President, and 'Vice Presidents and above may fly first class' (line 138); "
    "the traveller asks for it. The cheaper 06:15 first-class seat is sold out: the cheapest first-class fare that can "
    "be bought. The trip is approved in advance (lines 760-762).")

scenario(
    "briar-cove", "easy", ["multi_leg"],
    "Can you book me Boston to Phoenix on February 2nd for the customer kickoff the next morning? I don't mind "
    "connecting if it saves "
    "real money.",
    trip(traveller_name="Owen Pruitt", traveller_title="Account Executive", job_level="TEAM_MEMBER", origin="BOS",
         destination="PHX", travel_date="2027-02-02", booking_date="2026-12-29",
         purpose="Customer kickoff meeting in Phoenix"),
    search("BOS", "PHX", "2027-02-02", {
        "nonstop": {"carrier": "AA", "depart": "08:00", "minutes": [300]},
        "denver": {"carrier": "UA", "via": ["DEN"], "depart": "08:00", "minutes": [235, 95], "layovers": [65]},
    }, [
        offer("nonstop-economy", "nonstop", "ECONOMY", 41800),
        offer("denver-economy", "denver", "ECONOMY", 24800),
    ], background=0),
    expected("BOOK", ["denver-economy"], ["ECONOMY"], CLEAR_CONNECTION, AM, LOW_CLAUSES + ["CONNECTING_FLIGHTS"]),
    LOW + [CONNECT],
    "The one-stop through Denver saves $170 against the nonstop and, leaving at the same time, arrives 95 minutes later "
    "(elapsed 395 against 300): it is the least expensive option and inside the example of lines 129-133, so it is "
    "the lowest logical coach airfare.")

scenario(
    "cinder-heath", "easy", ["dearer_option"],
    "Chicago O'Hare to Frankfurt on March 9th for the print-technology partner summit. It's a long overnight flight, so "
    "I'd like business class please.",
    trip(traveller_name="Elena Varga", traveller_title="Senior Manager, Print Production", job_level="SENIOR_MANAGER",
         origin="ORD", destination="FRA", travel_date="2027-03-09", booking_date="2027-01-26",
         purpose="Print-technology partner summit in Frankfurt", purpose_kind="CONFERENCE",
         requested_cabin="BUSINESS"),
    search("ORD", "FRA", "2027-03-09", {
        "lufthansa": {"carrier": "LH", "depart": "17:40", "minutes": [520]},
        "united": {"carrier": "UA", "depart": "18:30", "minutes": [515]},
    }, [
        offer("lufthansa-economy", "lufthansa", "ECONOMY", 92400),
        offer("lufthansa-business", "lufthansa", "BUSINESS", 412000),
        offer("united-economy", "united", "ECONOMY", 89800),
        offer("united-business", "united", "BUSINESS", 398000),
    ], background=0),
    expected("BOOK", ["united-business"], ["BUSINESS"], ["INTERNATIONAL_LONG_FLIGHT"], AM, CLASS),
    [BUSINESS, APPROVED],
    "International nonstops of 515 and 520 scheduled minutes: more than 6 hours of flying, so business class may be used "
    "(lines 154-156) and the traveller asks for it: the cheaper business fare. No approver is named for it.")

scenario(
    "dover-moss", "easy", ["dearer_option"],
    "New York JFK to San Francisco on January 21st for the West region business review. I'd like first class.",
    trip(traveller_name="Patricia Lowell", traveller_title="Vice President, Retail Operations", job_level="VICE_PRESIDENT",
         origin="JFK", destination="SFO", travel_date="2027-01-21", booking_date="2026-12-17",
         purpose="West region quarterly business review", purpose_kind="INTERNAL_MEETING", requested_cabin="FIRST",
         approver_name="Raymond Cho"),
    search("JFK", "SFO", "2027-01-21", {
        "american": {"carrier": "AA", "depart": "07:00"},
        "united": {"carrier": "UA", "depart": "09:30"},
        "delta": {"carrier": "DL", "depart": "12:15"},
    }, [
        offer("american-economy", "american", "ECONOMY", 38900),
        offer("american-first", "american", "FIRST", 129000),
        offer("united-economy", "united", "ECONOMY", 36500),
        offer("united-first", "united", "FIRST", 118500),
        offer("delta-economy", "delta", "ECONOMY", 40100),
        offer("delta-first", "delta", "FIRST", 124000),
    ]),
    expected("BOOK", ["united-first"], ["FIRST"], ["SENIOR_ROLE_ENTITLEMENT"], AM, CLASS),
    [VP_FIRST, APPROVED],
    "A Vice President may fly first class (line 138) and asks for it: the cheapest first-class fare.")

scenario(
    "elm-garnet", "easy", ["upgrade_not_taken"],
    "San Francisco to Tokyo Narita on February 23rd for the Japan franchise workshop. I know a flight this long could "
    "go in business, but economy is fine. Cheapest you can find.",
    trip(traveller_name="Kenji Morales", traveller_title="Manager, International Franchise Support", origin="SFO",
         destination="NRT", travel_date="2027-02-23", booking_date="2027-01-12",
         purpose="Franchise operations workshop in Tokyo", purpose_kind="TRAINING"),
    search("SFO", "NRT", "2027-02-23", {
        "united": {"carrier": "UA", "depart": "11:00", "minutes": [655]},
        "japan": {"carrier": "JL", "depart": "13:20", "minutes": [650]},
        "ana": {"carrier": "NH", "depart": "16:45", "minutes": [660]},
    }, [
        offer("united-economy", "united", "ECONOMY", 96500),
        offer("united-business", "united", "BUSINESS", 520000),
        offer("japan-economy", "japan", "ECONOMY", 91200),
        offer("japan-business", "japan", "BUSINESS", 498000),
        offer("ana-economy", "ana", "ECONOMY", 93800),
        offer("ana-business", "ana", "BUSINESS", 505000),
    ], background=2),
    expected("BOOK", ["japan-economy"], ["ECONOMY"], ["LOWEST_FARE"], AM, LOW_CLAUSES),
    LOW,
    "Business class 'may be used' over 6 hours (lines 154-156): permitted, not required. The traveller asks for the "
    "cheapest economy fare: the lowest logical coach airfare.",
    distractors=[aside(154, 156, "Business class may be used for international travel",
                       "a permission the traveller does not take")])

# ===== boundary twins (6) =====

DUB_TRIP = {"origin": "BOS", "destination": "DUB", "travel_date": "2027-03-16", "booking_date": "2027-02-02",
            "purpose": "Quarterly review with the Dublin print-services team", "purpose_kind": "INTERNAL_MEETING",
            "requested_cabin": "BUSINESS", "job_level": "SENIOR_MANAGER"}
DUB_REQUEST = ("Boston to Dublin overnight on March 16th for the quarterly review with the Dublin team. Business class "
               "please, if the policy allows it.")


def dub(minutes):
    return search("BOS", "DUB", "2027-03-16", {
        "aerlingus": {"carrier": "EI", "depart": "18:25", "minutes": [minutes]},
        "delta": {"carrier": "DL", "depart": "21:10", "minutes": [minutes]},
    }, [
        offer("aerlingus-economy", "aerlingus", "ECONOMY", 61400),
        offer("aerlingus-business", "aerlingus", "BUSINESS", 289000),
        offer("delta-economy", "delta", "ECONOMY", 64800),
        offer("delta-business", "delta", "BUSINESS", 301000),
    ], background=0)


scenario(
    "fern-quarry", "boundary_twin", ["dearer_option"], DUB_REQUEST,
    trip(traveller_name="Siobhan Carter", traveller_title="Senior Manager, Print Services", **DUB_TRIP),
    dub(361),
    expected("BOOK", ["aerlingus-business"], ["BUSINESS"], ["INTERNATIONAL_LONG_FLIGHT"], AM, CLASS),
    [BUSINESS, APPROVED],
    "Both nonstops are scheduled at 361 minutes: more than 6 hours of flying (lines 154-156), so business class may be "
    "used; the cheaper business fare. Background is off so no filler routing can fall on the other side.",
    twin_of="gull-ridge", twin_fact="both nonstops scheduled at 361 or 360 minutes")

scenario(
    "gull-ridge", "boundary_twin", [], DUB_REQUEST,
    trip(traveller_name="Siobhan Carter", traveller_title="Senior Manager, Print Services", **DUB_TRIP),
    dub(360),
    expected("BOOK", ["aerlingus-economy"], ["ECONOMY"], NOT_LONG, AM, LOW_CLAUSES),
    [BUSINESS, LOWEST, LOW_COSTS, APPROVED],
    "Both nonstops are scheduled at exactly 360 minutes: not 'more than 6 hours' (lines 154-156), so business class is "
    "not available; the lowest logical coach airfare (lines 135-137).",
    twin_of="fern-quarry", twin_fact="both nonstops scheduled at 360 or 361 minutes")

CLT_TRIP = {"origin": "CLT", "destination": "DEN", "travel_date": "2027-02-10", "booking_date": "2027-01-06",
            "purpose": "Mountain district center visits", "purpose_kind": "CENTER_VISIT", "requested_routing": "NONSTOP"}
CLT_REQUEST = ("Charlotte to Denver on February 10th for the district center visits, which start the next morning. "
               "I'd really prefer the nonstop if I can have it.")


def clt(connection_cents):
    return search("CLT", "DEN", "2027-02-10", {
        "nonstop": {"carrier": "AA", "depart": "09:00", "minutes": [200]},
        "chicago": {"carrier": "UA", "via": ["ORD"], "depart": "09:00", "minutes": [110, 145], "layovers": [45]},
    }, [
        offer("nonstop-economy", "nonstop", "ECONOMY", 38600),
        offer("chicago-economy", "chicago", "ECONOMY", connection_cents),
    ], background=0)


scenario(
    "hazel-tarn", "boundary_twin", ["multi_leg"], CLT_REQUEST,
    trip(traveller_name="Andre Wallace", traveller_title="District Manager, Mountain District", **CLT_TRIP),
    clt(23500),
    expected("BOOK", ["chicago-economy"], ["ECONOMY"], CLEAR_CONNECTION, AM, LOW_CLAUSES + ["CONNECTING_FLIGHTS"]),
    LOW + [CONNECT],
    "The one-stop through Chicago saves $151 against the nonstop and arrives 100 minutes later (both leave 09:00; elapsed "
    "300 against 200). Savings exceed $150 and the delay is not more than two hours (lines 129-133): the connection is "
    "to be accepted, whatever the traveller prefers. Background is off: every case on the connecting-flights rule lists only "
    "its pinned nonstop and connection, so the delay and savings have one measure.",
    twin_of="iris-brook", twin_fact="the connection saves $151 or $150")

scenario(
    "iris-brook", "boundary_twin", ["multi_leg"], CLT_REQUEST,
    trip(traveller_name="Andre Wallace", traveller_title="District Manager, Mountain District", **CLT_TRIP),
    clt(23600),
    expected("BOOK", ["chicago-economy", "nonstop-economy"], ["ECONOMY"], OPEN_CONNECTION, AM,
             LOW_CLAUSES + ["CONNECTING_FLIGHTS"]),
    LOW + [CONNECT],
    "The connection saves exactly $150, which does not 'exceed $150' (lines 129-133). Outside the example the text "
    "only 'expects' the least expensive one-connection option, so for a traveller who asks for the nonstop both the "
    "requested nonstop and the cheaper connection are accepted (soft rule, accept set).",
    twin_of="hazel-tarn", twin_fact="the connection saves $150 or $151")

SEA_TRIP = {"origin": "SEA", "destination": "MCO", "travel_date": "2027-03-03", "booking_date": "2027-01-27",
            "purpose": "Southeast print-production training in Orlando", "purpose_kind": "TRAINING",
            "requested_routing": "NONSTOP", "job_level": "TEAM_MEMBER"}
SEA_REQUEST = ("Seattle to Orlando on March 3rd for the print-production training, which starts the next morning. A "
               "nonstop would be great, please.")


def sea(layover):
    return search("SEA", "MCO", "2027-03-03", {
        "nonstop": {"carrier": "AS", "depart": "07:00", "minutes": [330]},
        "atlanta": {"carrier": "DL", "via": ["ATL"], "depart": "07:00", "minutes": [270, 90], "layovers": [layover]},
    }, [
        offer("nonstop-economy", "nonstop", "ECONOMY", 45800),
        offer("atlanta-economy", "atlanta", "ECONOMY", 21800),
    ], background=0)


scenario(
    "juniper-slate", "boundary_twin", ["multi_leg"], SEA_REQUEST,
    trip(traveller_name="Grace Nakamura", traveller_title="Production Specialist", **SEA_TRIP),
    sea(90),
    expected("BOOK", ["atlanta-economy"], ["ECONOMY"], CLEAR_CONNECTION, AM, LOW_CLAUSES + ["CONNECTING_FLIGHTS"]),
    LOW + [CONNECT],
    "The one-stop through Atlanta saves $240 and, leaving at the same time, arrives exactly 120 minutes after the "
    "nonstop (elapsed 450 against 330). A delay of two hours is not 'more than two hours' (lines 129-133): the "
    "connection is to be accepted.",
    twin_of="kestrel-dune", twin_fact="the Atlanta layover is 90 or 91 minutes (delay 120 or 121)")

scenario(
    "kestrel-dune", "boundary_twin", ["multi_leg"], SEA_REQUEST,
    trip(traveller_name="Grace Nakamura", traveller_title="Production Specialist", **SEA_TRIP),
    sea(91),
    expected("BOOK", ["atlanta-economy", "nonstop-economy"], ["ECONOMY"], OPEN_CONNECTION + ["CONNECTION_TOO_LONG"], AM,
             LOW_CLAUSES + ["CONNECTING_FLIGHTS"]),
    LOW + [CONNECT],
    "The connection now arrives 121 minutes after the nonstop: more than two hours, outside the example of lines "
    "129-133, so for a traveller who asks for the nonstop both it and the cheaper connection are accepted.",
    twin_of="juniper-slate", twin_fact="the Atlanta layover is 91 or 90 minutes (delay 121 or 120)")

# ===== multi-rule (4) =====

scenario(
    "lark-meadow", "multi_rule", ["dearer_option"],
    "Atlanta to Seattle on January 26th for the Northwest store-design rollout. I'm six weeks out from hip surgery and "
    "my VP's certification for a first class seat is already with the travel agency. First class, please.",
    trip(traveller_name="Lorraine Fitch", traveller_title="Director, Store Design", job_level="DIRECTOR", origin="ATL",
         destination="SEA", travel_date="2027-01-26", booking_date="2026-12-21",
         purpose="Northwest store-design rollout", purpose_kind="INTERNAL_MEETING", requested_cabin="FIRST",
         physical_need_on_file=True,
         sign_offs=[sign("VICE_PRESIDENT", "Howard Simms", "FIRST_CLASS_CERTIFICATION",
                         "Certifies that recovery from hip surgery prevents the traveller from using coach seating")]),
    search("ATL", "SEA", "2027-01-26", {
        "delta": {"carrier": "DL", "depart": "08:10"},
        "alaska": {"carrier": "AS", "depart": "10:40"},
    }, [
        offer("delta-economy", "delta", "ECONOMY", 34500),
        offer("delta-first", "delta", "FIRST", 112000),
        offer("alaska-economy", "alaska", "ECONOMY", 33200),
        offer("alaska-first", "alaska", "FIRST", 98000),
    ], background=2),
    expected("BOOK", ["alaska-first"], ["FIRST"], ["MEDICAL_NEED"], AM + ["VICE_PRESIDENT"], CLASS),
    [CERTIFIED, APPROVED],
    "A Director is below 'Vice Presidents and above' (line 138), but a Team Member pre-certified for a physician-approved "
    "health condition may fly first class, the certification approved by the VP and submitted to Global Travel before "
    "booking (lines 139-144): both hold. The cheapest first-class fare.",
    distractors=[aside(113, 115, "Team Members who have physical disabilities should notify Global",
                       "the disabilities section: notifying the agency, not the cabin")])

scenario(
    "mallow-pier", "multi_rule", ["dearer_option"],
    "Los Angeles to New York JFK on the red-eye on February 17th for the investor-day setup. I'd love first class on "
    "this one and I'll pay the difference out of my own pocket.",
    trip(traveller_name="Tomas Reyes", traveller_title="Manager, Corporate Events", origin="LAX", destination="JFK",
         travel_date="2027-02-17", booking_date="2027-01-13", purpose="Investor-day event setup in New York",
         purpose_kind="INTERNAL_MEETING", requested_cabin="FIRST", traveller_pays_difference=True),
    search("LAX", "JFK", "2027-02-17", {
        "american": {"carrier": "AA", "depart": "22:15"},
        "delta": {"carrier": "DL", "depart": "23:00"},
    }, [
        offer("american-economy", "american", "ECONOMY", 35800),
        offer("american-first", "american", "FIRST", 121000),
        offer("delta-economy", "delta", "ECONOMY", 37200),
        offer("delta-first", "delta", "FIRST", 116500),
    ], background=2),
    expected("BOOK", ["delta-first"], ["FIRST"], ["TRAVELER_PAYS_UPGRADE"], AM, CLASS),
    [SELF_PAY, APPROVED],
    "Not a VP, but 'Team Members may upgrade to first class by personally paying the cost of the upgrade' at ticketing "
    "(lines 145-149): the cheapest first-class fare, the traveller paying the difference from coach. The "
    "non-reimbursement of upgrades (lines 174-175, 815) does not stop the traveller paying their own.",
    distractors=[SEAT_UPGRADE, NR_UPGRADES])

NETTLE_SEARCH = search("IAH", "SFO", "2027-02-04", {
    "united": {"carrier": "UA", "depart": "08:20"},
    "alaska": {"carrier": "AS", "depart": "11:15"},
}, [
    offer("united-economy", "united", "ECONOMY", 27400),
    offer("united-first", "united", "FIRST", 96000),
    offer("alaska-economy", "alaska", "ECONOMY", 29900),
    offer("alaska-first", "alaska", "FIRST", 101000),
], background=2)

scenario(
    "nettle-bay", "multi_rule", ["multi_traveller", "upgrade_not_taken"],
    "Houston to San Francisco on February 4th for the client pitch. Karen, our VP, is on the 8:20 United in first and "
    "wants me next to her so we can rehearse the pitch on the way. Can you put me in first beside her? If not, book "
    "what the policy allows; I have to be at the pitch.",
    trip(traveller_name="Daniel Ortiz", traveller_title="Director, Enterprise Sales", job_level="DIRECTOR", origin="IAH",
         destination="SFO", travel_date="2027-02-04", booking_date="2027-01-05",
         purpose="Enterprise client pitch in San Francisco", requested_cabin="FIRST",
         travelling_with=[{"name": "Karen Liu", "title": "Vice President, Enterprise Sales", "job_level": "VICE_PRESIDENT",
                           "flight_number": first_flight("nettle-bay", NETTLE_SEARCH, "united-first"),
                           "date": "2027-02-04", "cabin": "FIRST"}]),
    NETTLE_SEARCH,
    expected("BOOK", ["united-economy"], ["ECONOMY"], NO_UPGRADE, AM, LOW_CLAUSES),
    [NO_RIDE_ALONG, VP_FIRST, LOWEST, LOW_COSTS, APPROVED],
    "Only the VP may fly first (line 138). A Team Member ineligible for first class who travels with an eligible one "
    "cannot upgrade to first class to conduct an inflight meeting (lines 150-153), and the traveller does not offer to "
    "pay. The lowest logical coach airfare, which is on the VP's own flight.")

scenario(
    "oak-lantern", "multi_rule", [],
    "Newark to Honolulu on March 2nd for the Hawaii center openings. It's about eleven hours in the air, so I'd like "
    "business class, if the policy allows it.",
    trip(traveller_name="Rachel Kim", traveller_title="Manager, New Center Openings", origin="EWR", destination="HNL",
         travel_date="2027-03-02", booking_date="2027-01-19", purpose="New center openings in Honolulu",
         purpose_kind="CENTER_VISIT", requested_cabin="BUSINESS"),
    search("EWR", "HNL", "2027-03-02", {
        "morning": {"carrier": "UA", "depart": "08:00", "minutes": [655]},
        "late": {"carrier": "UA", "depart": "10:30", "minutes": [660]},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 68400),
        offer("morning-business", "morning", "BUSINESS", 289000),
        offer("late-economy", "late", "ECONOMY", 71900),
        offer("late-business", "late", "BUSINESS", 301000),
    ], background=0),
    expected("BOOK", ["morning-economy"], ["ECONOMY"], NOT_LONG, AM, LOW_CLAUSES + ["DOMESTIC_MEALS"]),
    [BUSINESS, HIGH_COST, LOWEST, LOW_COSTS, APPROVED],
    "Over 6 hours of flying, but business class is only for international travel (lines 154-156). Hawaii is a US state "
    "and the handbook lists Honolulu among its domestic high cost cities (lines 298-305): domestic, so the lowest "
    "logical coach airfare.")

# ===== hidden clause (2) =====

scenario(
    "plume-sorrel", "hidden_clause", ["outside_air_section", "dearer_option"],
    "Chicago O'Hare to Los Angeles on February 25th. Gloria, our managing director, signed a documented policy exception "
    "so I can fly first on this trip: I'm presenting to the board straight off the plane. Please book first.",
    trip(traveller_name="Nadia Petrov", traveller_title="Senior Manager, Strategic Accounts", job_level="SENIOR_MANAGER",
         origin="ORD", destination="LAX", travel_date="2027-02-25", booking_date="2027-01-21",
         purpose="Board presentation in Los Angeles", purpose_kind="INTERNAL_MEETING", requested_cabin="FIRST",
         sign_offs=[sign("MANAGING_DIRECTOR", "Gloria Hughes", "POLICY_EXCEPTION",
                         "A documented exception to the travel policy: first class for this trip")]),
    search("ORD", "LAX", "2027-02-25", {
        "united": {"carrier": "UA", "depart": "07:30"},
        "american": {"carrier": "AA", "depart": "09:45"},
    }, [
        offer("united-economy", "united", "ECONOMY", 31800),
        offer("united-first", "united", "FIRST", 102500),
        offer("american-economy", "american", "ECONOMY", 30400),
        offer("american-first", "american", "FIRST", 99000),
    ], background=2),
    expected("BOOK", ["american-first"], ["FIRST"], ["POLICY_EXCEPTION_APPROVED"], AM + ["MANAGING_DIRECTOR"],
             ["ACCOUNTABILITY", "EXCEPTIONS"]),
    [EXCEPTIONS, EXCEPTION_ROLE, APPROVED],
    "Not a VP and no certification, but the air section is not the whole story: exceptions to the policy under $10,000 "
    "are approved by the Team Member's department MD (lines 77-78, section 3.1.2), and the MD approves exception "
    "requests (lines 932-934). The first fare ($990) and its difference from coach are both far under $10,000.")

QUINCE_FRIDAY = search("DEN", "SEA", "2027-02-12", {
    "alaska": {"carrier": "AS", "depart": "09:00"},
    "united": {"carrier": "UA", "depart": "12:30"},
    "southwest": {"carrier": "WN", "depart": "15:10"},
}, [
    offer("alaska-friday", "alaska", "ECONOMY", 28900),
    offer("united-friday", "united", "ECONOMY", 31400),
    offer("southwest-friday", "southwest", "ECONOMY", 30200),
], background=0)
QUINCE_MONDAY = search("DEN", "SEA", "2027-02-15", {
    "alaska": {"carrier": "AS", "depart": "07:00"},
    "united": {"carrier": "UA", "depart": "08:30"},
}, [
    offer("alaska-monday", "alaska", "ECONOMY", 19800),
    offer("united-monday", "united", "ECONOMY", 21500),
], background=0, name="business-only")

scenario(
    "quince-harbor", "hidden_clause", ["personal_travel", "outside_air_section", "date_arithmetic"],
    "My client workshop in Seattle is Monday the 15th, but I'd like to fly up from Denver on Friday the 12th and spend "
    "the long weekend with my sister. I know Friday costs more than flying Monday morning; I'll pay the difference.",
    trip(traveller_name="Brian Holloway", traveller_title="Account Manager", job_level="TEAM_MEMBER", origin="DEN",
         destination="SEA", travel_date="2027-02-12", business_travel_date="2027-02-15", booking_date="2027-01-18",
         purpose="Client workshop in Seattle on Monday, with a personal weekend before it",
         traveller_pays_difference=True),
    [QUINCE_FRIDAY, QUINCE_MONDAY],
    expected("BOOK", ["alaska-friday"], ["ECONOMY"], ["LOWEST_FARE", "PERSONAL_COST_PAID_BY_TRAVELER"], AM,
             ["PERSONAL_WITH_BUSINESS"]),
    [PERSONAL, APPROVED],
    "Personal days combined with approved business travel (lines 526-531): FXO pays the least expensive business-only "
    "routing ($198 on Monday) and the traveller pays the $91 more of the cheapest Friday fare, which is the ticket "
    "booked. Both dates are pinned searches.",
    distractors=[aside(825, 826, "Any additional change fees for personal travel combined with business travel",
                       "change fees, not the fare")])

# ===== distractor (2) =====

scenario(
    "rowan-flint", "distractor", ["date_arithmetic", "month_end"],
    "Short notice, sorry: the European center audit in Amsterdam starts Tuesday December 8th, and I'll fly out of "
    "Minneapolis overnight on Sunday December 6th. Business class please, if the policy allows it.",
    trip(traveller_name="Heidi Brandt", traveller_title="Senior Manager, Loss Prevention", job_level="SENIOR_MANAGER",
         origin="MSP", destination="AMS", travel_date="2026-12-06", booking_date="2026-11-27",
         purpose="European center audit in Amsterdam", purpose_kind="CENTER_VISIT", requested_cabin="BUSINESS"),
    search("MSP", "AMS", "2026-12-06", {
        "delta": {"carrier": "DL", "depart": "15:40", "minutes": [500]},
        "klm": {"carrier": "KL", "depart": "18:10", "minutes": [505]},
    }, [
        offer("delta-economy", "delta", "ECONOMY", 84500),
        offer("delta-business", "delta", "BUSINESS", 362000),
        offer("klm-economy", "klm", "ECONOMY", 86900),
        offer("klm-business", "klm", "BUSINESS", 348000),
    ], background=0),
    expected("BOOK", ["klm-business"], ["BUSINESS"], ["INTERNATIONAL_LONG_FLIGHT"], AM, CLASS),
    [BUSINESS, APPROVED],
    "Booked 9 days ahead (November 27 to December 6). Lines 121-124 ask Team Members to 'make every attempt' to book "
    "14 days ahead (under Domestic Airline Tickets) and note that non-refundable fares usually need it, but that is no "
    "ban and does not touch the cabin. International nonstops of 500 and 505 scheduled minutes: more than 6 hours, so "
    "business class may be used (lines 154-156) and the traveller asks for it: the cheaper business fare.",
    distractors=[DOMESTIC_ADVANCE_ASIDE, FEES, LATE])

scenario(
    "sedge-copper", "distractor", ["outside_air_section", "upgrade_not_taken"],
    "Philadelphia to Los Angeles on January 28th for the West Coast supplier review. Economy is fine for me, but please "
    "put me on United: I'm a few flights short of keeping my status. If United isn't possible, book what the "
    "policy allows; I have to be at the review.",
    trip(traveller_name="Victor Alvarez", traveller_title="Vice President, Supply Chain", job_level="VICE_PRESIDENT",
         origin="PHL", destination="LAX", travel_date="2027-01-28", booking_date="2026-12-22",
         purpose="West Coast supplier review", purpose_kind="SUPPLIER_VISIT", requested_airline="United Airlines",
         approver_name="Marjorie Haynes"),
    search("PHL", "LAX", "2027-01-28", {
        "united": {"carrier": "UA", "depart": "08:15"},
        "american": {"carrier": "AA", "depart": "09:30"},
        "delta": {"carrier": "DL", "depart": "11:00"},
    }, [
        offer("united-economy", "united", "ECONOMY", 36200),
        offer("united-first", "united", "FIRST", 112000),
        offer("american-economy", "american", "ECONOMY", 33900),
        offer("american-first", "american", "FIRST", 98500),
        offer("delta-economy", "delta", "ECONOMY", 35100),
    ]),
    expected("BOOK", ["american-economy"], ["ECONOMY"], ["LOWEST_FARE", "LOYALTY_PROGRAM_PREFERENCE"], AM,
             LOW_CLAUSES + ["NON_REIMBURSABLE"]),
    LOW + [INSIST],
    "The VP could fly first (line 138) but asks for economy. Keeping frequent flyer benefits is allowed (line 498), but "
    "airfare is not reimbursed when a Team Member insists on a specific airline instead of a cheaper fare (lines "
    "820-821): the cheaper American fare, not United.",
    distractors=[FREQUENT, aside(138, 138, "Vice Presidents and above may fly first class.",
                                 "a permission the traveller does not take")])

# ===== refusal (2) =====

scenario(
    "thistle-marsh", "refusal", ["outside_air_section"],
    "Please book a flight for Marco Bellini from our press supplier, Charlotte to Chicago O'Hare on January 20th, so he "
    "can join our install review. We'd like to cover his ticket.",
    trip(traveller_name="Marco Bellini", traveller_title="Field Engineer, Halvorsen Press Systems (supplier)",
         job_level="NOT_EMPLOYEE", passenger="SUPPLIER", accompanies="Jill Sanders, Production Manager", origin="CLT",
         destination="ORD", travel_date="2027-01-20", booking_date="2026-12-16",
         purpose="Press install review with the Chicago production team", purpose_kind="SUPPLIER_VISIT"),
    search("CLT", "ORD", "2027-01-20", {
        "american": {"carrier": "AA", "depart": "07:45"},
        "united": {"carrier": "UA", "depart": "10:20"},
    }, [
        offer("american-economy", "american", "ECONOMY", 24300),
        offer("united-economy", "united", "ECONOMY", 26100),
    ]),
    expected("REFUSE", [], ["NONE"], ["BUSINESS_GUEST_NOT_PREPAID", "OUTSIDE_POLICY_SCOPE"], AM, ["BUSINESS_GUESTS"]),
    [GUEST],
    "Air travel expenses for a business guest or supplier 'will not be paid in advance by FXO' (lines 538-540); a "
    "supplier whose expenses are reimbursed sends an invoice (lines 541-543). The company buys no ticket. The visit's "
    "approval on file is not what the refusal uses (NONE or the approving manager).")

scenario(
    "umber-wick", "refusal", ["personal_travel", "outside_air_section", "multi_traveller"],
    "My husband wants to come along on my customer trip to San Diego on February 9th. Could you book his flight from "
    "Austin on the same day as mine?",
    trip(traveller_name="Paul Jensen", traveller_title="Husband of Laura Jensen, Regional Sales Manager",
         job_level="NOT_EMPLOYEE", passenger="SPOUSE_OR_FAMILY", accompanies="Laura Jensen, Regional Sales Manager",
         origin="AUS", destination="SAN", travel_date="2027-02-09", booking_date="2027-01-08",
         purpose="Accompanying the employee on her customer visits in San Diego"),
    search("AUS", "SAN", "2027-02-09", {
        "southwest": {"carrier": "WN", "depart": "07:35"},
        "alaska": {"carrier": "AS", "depart": "10:50"},
    }, [
        offer("southwest-economy", "southwest", "ECONOMY", 21900),
        offer("alaska-economy", "alaska", "ECONOMY", 24600),
    ]),
    expected("REFUSE", [], ["NONE"], ["COMPANION_NOT_COVERED", "PERSONAL_TRAVEL_NOT_COVERED"], AM,
             ["DEPENDENT_TRAVEL", "NON_REIMBURSABLE"]),
    [DEPENDENT, DEPENDENT_LIST],
    "Travel expenses for family or significant others are the Team Member's own and are not reimbursed, unless "
    "communicated in advance for a company-sponsored event (lines 534-536, 827-828); a customer visit is not one. The "
    "company buys no ticket. The employee's trip approval is not what the refusal uses.")

# ===== flag (3) =====

scenario(
    "vale-pewter", "flag", ["multi_leg", "unclear_phrase"],
    "Denver to Bogota on March 4th for the Latin America franchise launch. It's over seven hours of flying with the "
    "Miami connection, so business class please.",
    trip(traveller_name="Camila Restrepo", traveller_title="Senior Manager, Franchise Development",
         job_level="SENIOR_MANAGER", origin="DEN", destination="BOG", travel_date="2027-03-04",
         booking_date="2027-01-28", purpose="Franchise launch in Bogota", purpose_kind="CONFERENCE",
         requested_cabin="BUSINESS"),
    search("DEN", "BOG", "2027-03-04", {
        "early": {"carrier": "AA", "via": ["MIA"], "depart": "06:30", "minutes": [235, 205], "layovers": [75]},
        "late": {"carrier": "AA", "via": ["MIA"], "depart": "11:45", "minutes": [235, 205], "layovers": [80]},
    }, [
        offer("early-economy", "early", "ECONOMY", 52800),
        offer("early-business", "early", "BUSINESS", 198000),
        offer("late-economy", "late", "ECONOMY", 55400),
        offer("late-business", "late", "BUSINESS", 212000),
    ], background=0),
    expected("FLAG_FOR_APPROVAL", ["early-business"], ["BUSINESS"], ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], UNCLEAR_ROLES, CLASS,
             phrase="not including connections or layovers"),
    [BUSINESS, EXCEPTIONS, APPROVED],
    "Only connections through Miami: 235 + 205 = 440 flying minutes, but no single flight over 360. Lines 154-156 count "
    "'actual flying time ... not including connections or layovers': if the flights are added (only ground time left "
    "out), business may be used; if 'connections' means the connecting flights are not combined, it may not. Hold the "
    "cheapest business fare. No role is named; under the per-flight reading business would be an exception for the "
    "department MD (lines 77-78).",
    flag_twins=["cinder-heath", "gull-ridge"],
    ambiguity={"phrase": "not including connections or layovers",
               "readings": [("the flights' minutes are added and only the ground time between them is left out: 440 "
                            "minutes, business class may be used"),
                            ("each flight is measured on its own ('connections' are not combined): no flight is over "
                            "360 minutes, coach")]})

scenario(
    "willow-cairn", "flag", ["unclear_phrase", "outside_air_section"],
    "Miami to Vancouver on February 18th for the Canadian franchise partners' meeting. It's a six-and-a-quarter-hour "
    "nonstop, so I'd like business class.",
    trip(traveller_name="Jordan Pierce", traveller_title="Manager, Franchise Partnerships", origin="MIA",
         destination="YVR", travel_date="2027-02-18", booking_date="2027-01-14",
         purpose="Canadian franchise partners' meeting in Vancouver", purpose_kind="INTERNAL_MEETING",
         requested_cabin="BUSINESS"),
    search("MIA", "YVR", "2027-02-18", {
        "aircanada": {"carrier": "AC", "depart": "09:15", "minutes": [375]},
        "american": {"carrier": "AA", "depart": "12:40", "minutes": [375]},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 48600),
        offer("aircanada-business", "aircanada", "BUSINESS", 186000),
        offer("american-economy", "american", "ECONOMY", 51200),
        offer("american-business", "american", "BUSINESS", 199000),
    ], background=0),
    expected("FLAG_FOR_APPROVAL", ["aircanada-business"], ["BUSINESS"], ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], UNCLEAR_ROLES,
             CLASS + ["DOMESTIC_MEALS"], phrase="international travel"),
    [BUSINESS, HIGH_COST, CAR_CANADA, EXCEPTIONS, APPROVED],
    "375-minute nonstops: over 6 hours of flying. Business class is for 'international travel' (lines 154-156), which "
    "the handbook never defines; it lists Toronto and Vancouver among the high cost cities of 3.6.1 Domestic Travel "
    "Meals (lines 298-305) and groups the US and Canada together (lines 515-516). A flight to Canada is international "
    "on one reading and treated as domestic on the other: hold the cheapest business fare.",
    flag_twins=["cinder-heath", "oak-lantern"],
    ambiguity={"phrase": "international travel",
               "readings": [("a flight from the US to Canada crosses a border, so it is international travel: business "
                            "class may be used"),
                            ("the handbook files Toronto and Vancouver under domestic travel and groups the US with "
                            "Canada, so the trip is domestic: coach")]})

scenario(
    "yarrow-glint", "flag", ["approval_required"],
    "Dallas to Boston on February 11th for the New England center reviews. After my back surgery I can't sit in coach, "
    "and my director signed the certification for a first class seat; it's with the travel agency. First class, "
    "please.",
    trip(traveller_name="Gregory Nash", traveller_title="Senior Manager, Center Operations", job_level="SENIOR_MANAGER",
         origin="DFW", destination="BOS", travel_date="2027-02-11", booking_date="2027-01-07",
         purpose="New England center operations reviews", purpose_kind="CENTER_VISIT", requested_cabin="FIRST",
         physical_need_on_file=True,
         sign_offs=[sign("DIRECTOR", "Monica Feld", "FIRST_CLASS_CERTIFICATION",
                         "Certifies that recovery from back surgery prevents the traveller from using coach seating")]),
    search("DFW", "BOS", "2027-02-11", {
        "american": {"carrier": "AA", "depart": "07:45"},
        "delta": {"carrier": "DL", "depart": "10:05"},
    }, [
        offer("american-economy", "american", "ECONOMY", 29800),
        offer("american-first", "american", "FIRST", 89500),
        offer("delta-economy", "delta", "ECONOMY", 31200),
        offer("delta-first", "delta", "FIRST", 94000),
    ], background=2),
    expected("FLAG_FOR_APPROVAL", ["american-first"], ["FIRST"], ["APPROVAL_REQUIRED", "MEDICAL_NEED"],
             ["SENIOR_VICE_PRESIDENT", "VICE_PRESIDENT"], CLASS),
    [CERTIFIED, APPROVED],
    "A pre-certified physical need allows first class, but the certification 'must be approved by their VP or higher "
    "level management' before booking (lines 142-144); a Director signed it. Hold the cheapest first-class fare for "
    "the VP (or higher). Approval required, not 'no compliant offer'.",
    flag_twins=["lark-meadow", "nettle-bay"],
    ambiguity="none: an approval by the VP or higher is required and missing; the text is clear")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
