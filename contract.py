"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-fedex-office-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    POLICY_EXCEPTION_APPROVED = "POLICY_EXCEPTION_APPROVED"
    BUSINESS_GUEST_NOT_PREPAID = "BUSINESS_GUEST_NOT_PREPAID"
    PERSONAL_COST_PAID_BY_TRAVELER = "PERSONAL_COST_PAID_BY_TRAVELER"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    DENIED_BOARDING_NOT_ALLOWED = "DENIED_BOARDING_NOT_ALLOWED"
    EXTENDED_TRAVEL_SAVINGS = "EXTENDED_TRAVEL_SAVINGS"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: FedEx Office Travel and Business Expense Policy (updated January 19, 2015).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    ASPEN_WHARF = "aspen-wharf"
    BRIAR_COVE = "briar-cove"
    CINDER_HEATH = "cinder-heath"
    DOVER_MOSS = "dover-moss"
    ELM_GARNET = "elm-garnet"
    FERN_QUARRY = "fern-quarry"
    GULL_RIDGE = "gull-ridge"
    HAZEL_TARN = "hazel-tarn"
    IRIS_BROOK = "iris-brook"
    JUNIPER_SLATE = "juniper-slate"
    KESTREL_DUNE = "kestrel-dune"
    LARK_MEADOW = "lark-meadow"
    MALLOW_PIER = "mallow-pier"
    NETTLE_BAY = "nettle-bay"
    OAK_LANTERN = "oak-lantern"
    PLUME_SORREL = "plume-sorrel"
    QUINCE_HARBOR = "quince-harbor"
    ROWAN_FLINT = "rowan-flint"
    SEDGE_COPPER = "sedge-copper"
    THISTLE_MARSH = "thistle-marsh"
    UMBER_WICK = "umber-wick"
    VALE_PEWTER = "vale-pewter"
    WILLOW_CAIRN = "willow-cairn"
    YARROW_GLINT = "yarrow-glint"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    APPROVING_MANAGER = "APPROVING_MANAGER"
    SUPERVISOR = "SUPERVISOR"
    DISTRICT_MANAGER = "DISTRICT_MANAGER"
    DIRECTOR = "DIRECTOR"
    MANAGING_DIRECTOR = "MANAGING_DIRECTOR"
    VICE_PRESIDENT = "VICE_PRESIDENT"
    SENIOR_VICE_PRESIDENT = "SENIOR_VICE_PRESIDENT"
    CHIEF_EXECUTIVE = "CHIEF_EXECUTIVE"
    EVENTS_TEAM = "EVENTS_TEAM"
    TRAVEL_AGENCY = "TRAVEL_AGENCY"
    CONTROLLER = "CONTROLLER"
    HUMAN_RESOURCES = "HUMAN_RESOURCES"
    TRAVEL_MANAGER = "TRAVEL_MANAGER"


class Clause(Enum):
    """The handbook's sections, by heading."""

    POLICY_GENERAL = "POLICY_GENERAL"
    EXPENSE_APPROVAL = "EXPENSE_APPROVAL"
    EXCEPTIONS = "EXCEPTIONS"
    TRAVEL_ARRANGEMENTS = "TRAVEL_ARRANGEMENTS"
    BOOKING_FEES = "BOOKING_FEES"
    EN_ROUTE_CHANGES = "EN_ROUTE_CHANGES"
    TRAVELERS_WITH_DISABILITIES = "TRAVELERS_WITH_DISABILITIES"
    AIR_TRAVEL = "AIR_TRAVEL"
    DOMESTIC_TICKETS = "DOMESTIC_TICKETS"
    CONNECTING_FLIGHTS = "CONNECTING_FLIGHTS"
    CLASS_OF_SERVICE = "CLASS_OF_SERVICE"
    CANCELLATIONS = "CANCELLATIONS"
    SEAT_CHANGES = "SEAT_CHANGES"
    BAGGAGE_FEES = "BAGGAGE_FEES"
    DOMESTIC_MEALS = "DOMESTIC_MEALS"
    INTERNATIONAL_MEALS = "INTERNATIONAL_MEALS"
    MILEAGE_EXCEPTION = "MILEAGE_EXCEPTION"
    NON_PAID_LOYALTY = "NON_PAID_LOYALTY"
    CAR_INSURANCE = "CAR_INSURANCE"
    PERSONAL_WITH_BUSINESS = "PERSONAL_WITH_BUSINESS"
    DEPENDENT_TRAVEL = "DEPENDENT_TRAVEL"
    BUSINESS_GUESTS = "BUSINESS_GUESTS"
    GROUP_TRAVEL = "GROUP_TRAVEL"
    SIGNING_AUTHORITY = "SIGNING_AUTHORITY"
    REIMBURSABLE_SUMMARY = "REIMBURSABLE_SUMMARY"
    NON_REIMBURSABLE = "NON_REIMBURSABLE"
    ACCOUNTABILITY = "ACCOUNTABILITY"


class JobLevel(Enum):
    TEAM_MEMBER = "TEAM_MEMBER"
    MANAGER = "MANAGER"
    SENIOR_MANAGER = "SENIOR_MANAGER"
    DIRECTOR = "DIRECTOR"
    MANAGING_DIRECTOR = "MANAGING_DIRECTOR"
    VICE_PRESIDENT = "VICE_PRESIDENT"
    SENIOR_VICE_PRESIDENT = "SENIOR_VICE_PRESIDENT"
    EXECUTIVE_VICE_PRESIDENT = "EXECUTIVE_VICE_PRESIDENT"
    CHIEF_EXECUTIVE = "CHIEF_EXECUTIVE"
    NOT_EMPLOYEE = "NOT_EMPLOYEE"


class Passenger(Enum):
    EMPLOYEE = "EMPLOYEE"
    SPOUSE_OR_FAMILY = "SPOUSE_OR_FAMILY"
    BUSINESS_GUEST = "BUSINESS_GUEST"
    SUPPLIER = "SUPPLIER"


class Purpose(Enum):
    CUSTOMER_VISIT = "CUSTOMER_VISIT"
    CENTER_VISIT = "CENTER_VISIT"
    INTERNAL_MEETING = "INTERNAL_MEETING"
    TRAINING = "TRAINING"
    CONFERENCE = "CONFERENCE"
    COMPANY_SPONSORED_EVENT = "COMPANY_SPONSORED_EVENT"
    SUPPLIER_VISIT = "SUPPLIER_VISIT"
    PERSONAL = "PERSONAL"


class Routing(Enum):
    ANY = "ANY"
    NONSTOP = "NONSTOP"


class SignOffSubject(Enum):
    TRIP = "TRIP"
    FIRST_CLASS_CERTIFICATION = "FIRST_CLASS_CERTIFICATION"
    POLICY_EXCEPTION = "POLICY_EXCEPTION"


@dataclass
class SignOff(Output):
    role: Annotated[Approver, "The signer's role, in the traveller's own department and reporting line"]
    name: Annotated[str, "Their name"]
    subject: Annotated[SignOffSubject, "What they signed: the trip itself, a certification that the traveller needs a first class seat, or an exception to the handbook"]
    covers: Annotated[str, "What the sign-off says, in plain words"]
    on_file_with_agency: Annotated[bool, "Whether the company's booking agency has received a copy"]


@dataclass
class Colleague(Output):
    name: Annotated[str, "The colleague's name"]
    title: Annotated[str, "Their job title"]
    job_level: Annotated[JobLevel, "Their level in the company"]
    flight_number: Annotated[str, "The flight they are already ticketed on, as search_flights lists it"]
    date: Annotated[str, "That flight's local departure date, YYYY-MM-DD"]
    cabin: Annotated[Cabin, "The cabin they are ticketed in"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title, or their relation to the employee they go with"]
    job_level: Annotated[JobLevel, "The traveller's level in the company; NOT_EMPLOYEE for someone who does not work there"]
    passenger: Annotated[Passenger, "What the person flying is to the company"]
    accompanies: Annotated[str, "The employee this person goes with or visits, when the person flying is not an employee; empty otherwise"]
    home_country: Annotated[str, "The country the traveller is based in, as an ISO code"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where it goes"]
    travel_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    business_travel_date: Annotated[str, "The day the work itself would need the flight, YYYY-MM-DD; the same as travel_date unless the traveller adds days of their own"]
    return_date: Annotated[str, "For a round trip bought as one fare, the day to fly back, YYYY-MM-DD; empty for one way"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    purpose_kind: Annotated[Purpose, "The kind of trip"]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    requested_routing: Annotated[Routing, "NONSTOP when the traveller asks for a nonstop flight; ANY otherwise"]
    requested_airline: Annotated[str, "The airline the traveller asks for, as search_flights names airlines; empty when none"]
    traveller_pays_difference: Annotated[bool, "Whether the traveller offers to pay, out of pocket, what the requested ticket costs above the one the company would buy"]
    physical_need_on_file: Annotated[bool, "Whether a physical or health condition of the traveller that affects seating is on file"]
    told_company_beforehand: Annotated[bool, "For a family member, whether the company was told ahead of time that they travel; false otherwise"]
    sign_offs: Annotated[list[SignOff], "Sign-offs already on file for this trip, each given before today"]
    travelling_with: Annotated[list[Colleague], "Colleagues on the same trip who are already ticketed; empty when none"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
