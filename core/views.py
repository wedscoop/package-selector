from django.shortcuts import render, redirect
from datetime import datetime
from .models import Session, Event, User
from .logic import get_package, create_session_id, get_most_interested_plan
from .logic import get_all_packages
from .logic import get_price_calendar
    

def get_or_create_session(request):
    sid = request.COOKIES.get("sid")

    if not sid:
        sid = create_session_id()
        session = Session.objects.create(session_id=sid)
    else:
        session, _ = Session.objects.get_or_create(session_id=sid)

    return session, sid


def log_event(session, event_type, metadata=None):
    Event.objects.create(
        session=session,
        user=session.user,
        type=event_type,
        metadata=metadata or {},
    )


def home(request):
    session, sid = get_or_create_session(request)
    packages = get_all_packages()
    user = session.user
    is_returning = False

    last_event = Event.objects.filter(session=session).order_by("-created_at").first()

    if last_event:
        gap = datetime.now(last_event.created_at.tzinfo) - last_event.created_at
        hours = round(gap.total_seconds() / 3600, 1)

        if hours > 1:
            log_event(session, "return_after_gap", {"hours": hours})
            is_returning = True

    if user:
        log_event(session, "return_visit")

    last_plan = request.session.get("last_plan")
    event_date = request.session.get("event_date")

    if event_date:
        try:
            event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
        except:
            event_date = None


    response = render(request, "home.html", {
        "user": user,
        "is_returning": is_returning,
        "last_plan": last_plan,
        "event_date": event_date,
        "packages": packages,
    })

    response.set_cookie("sid", sid)
    return response


def view_plan(request, plan_id):
    from datetime import datetime
    from .logic import get_demand_multiplier, get_price_calendar

    session, _ = get_or_create_session(request)

    plan = get_package(plan_id)
    if not plan:
        return redirect("/")

    # -------------------------
    # DATE HANDLING
    # -------------------------
    event_date = request.GET.get("event_date")

    parsed_date = None
    if event_date:
        try:
            parsed_date = datetime.strptime(event_date, "%Y-%m-%d").date()
        except:
            parsed_date = None

    # -------------------------
    # DEMAND PRICING
    # -------------------------
    multiplier = get_demand_multiplier(parsed_date) if parsed_date else 1

    price_value = int(plan["price"] * multiplier)

    def format_price(p):
        if p >= 100000:
            return f"{round(p/100000,1)}L"
        return str(p)

    price = format_price(price_value)

    # -------------------------
    # CALENDAR
    # -------------------------
    calendar = get_price_calendar(plan["price"])
    min_price = min([d["price"] for d in calendar]) if calendar else None

    # -------------------------
    # TRACKING
    # -------------------------
    previous_views = Event.objects.filter(
        session=session,
        type="plan_expanded",
        metadata__plan=plan_id
    ).count()

    current_count = previous_views + 1

    log_event(session, "plan_expanded", {
        "plan": plan_id,
        "repeat_count": current_count
    })

    force_capture = current_count >= 5 and session.user is None

    return render(request, "partials/plan.html", {
        "plan": plan,
        "plan_id": plan_id,
        "price": price,
        "price_value": price_value,
        "event_date": parsed_date,
        "calendar": calendar,
        "min_price": min_price,
        "repeat_count": current_count,
        "user": session.user,
        "force_capture": force_capture
    })


# -------------------------
# LEAD CAPTURE (NO REDIRECT)
# -------------------------
def capture_phone(request):
    session, _ = get_or_create_session(request)

    phone = request.POST.get("phone")
    name = request.POST.get("name")
    plan_id = request.POST.get("plan_id")

    if not phone or not plan_id:
        return redirect("/")

    user, _ = User.objects.get_or_create(phone=phone)

    if name:
        user.name = name
        user.save()

    session.user = user
    session.save()

    # ✅ store last viewed plan
    request.session["last_plan"] = plan_id
    event_date = request.POST.get("event_date")
    request.session["event_date"] = event_date
    log_event(session, "lead_captured")

    return redirect("/")  # back to home


# -------------------------
# FINAL INTENT (WHATSAPP)
# -------------------------
def request_booking(request):
    session, _ = get_or_create_session(request)

    user = session.user
    if not user:
        return redirect("/")

    plan_id = request.GET.get("plan_id")
    event_date = request.GET.get("event_date")
    price = request.GET.get("price")

    if not plan_id:
        return redirect("/")

    plan = get_package(plan_id)

    from datetime import datetime
    import urllib.parse

    import urllib.parse

    message = f"Hi, I’m {user.name}.\n\n"
    message += "I’m interested in the following package:\n\n"

    message += f"*PACKAGE:* {plan['name']}\n"

    if price:
        message += f"*PRICE:* ₹{price}\n"

    if event_date:
        message += f"*DATE:* {event_date}\n"

    message += "\n*Coverage:*\n"
    for d in plan["days"]:
        events = ", ".join(d["events"])
        message += f"- {d['day']}: {events}\n"

    if plan.get("deliverables"):
        message += "\n*Deliverables:*\n"
        for d in plan["deliverables"]:
            message += f"- {d}\n"

    message += "\nCould you please confirm availability for this date?"

    encoded = urllib.parse.quote_plus(message)

    log_event(session, "booking_requested")

    return redirect(f"https://wa.me/91{7982921411}?text={encoded}")