import uuid
import yaml
from pathlib import Path
from .models import Event
from datetime import date, timedelta


# -------------------------
# LOAD PACKAGES FROM YAML
# -------------------------
BASE_DIR = Path(__file__).resolve().parent


def load_packages():
    with open(BASE_DIR / "packages.yaml", "r") as f:
        data = yaml.safe_load(f)
    return data.get("packages", {})


def get_all_packages():
    return load_packages()


def get_package(plan_id):
    return load_packages().get(plan_id)


def create_session_id():
    return str(uuid.uuid4())


# -------------------------
# LEAD SCORING
# -------------------------
def calculate_lead_score(user):
    events = Event.objects.filter(user=user)

    score = 0

    for e in events:
        if e.type == "plan_expanded":
            score += 2
            score += e.metadata.get("repeat_count", 1) - 1

        elif e.type == "return_visit":
            score += 3

        elif e.type == "return_after_gap":
            score += 4

        elif e.type == "lead_captured":
            score += 5

        elif e.type == "booking_requested":
            score += 10

    return score


def get_lead_label(score):
    if score >= 15:
        return "🔥 HOT"
    elif score >= 7:
        return "⚡ WARM"
    return "❄️ COLD"


# -------------------------
# MOST INTERESTED PLAN
# -------------------------
def get_most_interested_plan(user):
    events = Event.objects.filter(user=user, type="plan_expanded")

    plan_counts = {}

    for e in events:
        plan = e.metadata.get("plan")
        if not plan:
            continue

        plan_counts[plan] = plan_counts.get(plan, 0) + 1

    if not plan_counts:
        return None

    return max(plan_counts, key=plan_counts.get)


# -------------------------
# FOLLOW-UP LOGIC
# -------------------------
def needs_followup(user):
    events = Event.objects.filter(user=user)

    has_booking = events.filter(type="booking_requested").exists()

    return not has_booking


def generate_followup_message(user):
    plan = get_most_interested_plan(user) or "wedding"
    name = user.name or "there"

    return f"Hi {name}, saw you were checking our {plan} package. Need help with pricing or availability?"
    
from datetime import date, timedelta
from .models import DemandSlot


def get_demand_multiplier(event_date):
    slot = DemandSlot.objects.filter(event_date=event_date).first()
    count = slot.booking_count if slot else 0
    return 1 + (0.10 * count)


def get_price_calendar(base_price, start_date=None, days=30):
    if not start_date:
        start_date = date.today()

    calendar = []

    for i in range(days):
        d = start_date + timedelta(days=i)

        multiplier = get_demand_multiplier(d)
        price = int(base_price * multiplier)

        calendar.append({
            "date": d,
            "price": price,
            "price_display": format_price(price),  # 👈 ADD THIS
            "bookings": int((multiplier - 1) / 0.1),
            "is_surge": multiplier > 1
        })

    return calendar

def format_price(p):
    if p >= 100000:
        return f"{round(p/100000,2)}L"
    return str(p)