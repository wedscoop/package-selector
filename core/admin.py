from django.contrib import admin
from django.utils.html import format_html
from .models import User, Session, Event
from .logic import (
    calculate_lead_score,
    get_lead_label,
    get_most_interested_plan,
    needs_followup,
    generate_followup_message,
)

from .models import DemandSlot

admin.site.register(DemandSlot)

class EventInline(admin.TabularInline):
    model = Event
    extra = 0
    readonly_fields = ("display_event", "created_at")
    fields = ("display_event", "created_at")

    def display_event(self, obj):
        return str(obj)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "interested_plan",
        "lead_score",
        "lead_status",
        "followup_status",
        "send_whatsapp",
        "created_at",
    )

    search_fields = ("name", "phone")
    ordering = ("-created_at",)
    inlines = [EventInline]

    def lead_score(self, obj):
        return calculate_lead_score(obj)

    def lead_status(self, obj):
        return get_lead_label(self.lead_score(obj))

    def interested_plan(self, obj):
        return get_most_interested_plan(obj)

    def followup_status(self, obj):
        return "❗ Needs Follow-up" if needs_followup(obj) else "—"

    def send_whatsapp(self, obj):
        if not needs_followup(obj):
            return "—"

        message = generate_followup_message(obj)
        url = f"https://wa.me/91{obj.phone}?text={message}"

        return format_html(f'<a href="{url}" target="_blank">📩 Send</a>')

    send_whatsapp.short_description = "Follow-up"


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "user",
        "is_lost_lead",
        "top_plan",
        "drop_off_stage",
        "event_count",
        "created_at",
    )

    def is_lost_lead(self, obj):
        if obj.user:
            return "❌ No"

        has_activity = Event.objects.filter(session=obj, type="plan_expanded").exists()
        return "🔥 YES" if has_activity else "—"

    def drop_off_stage(self, obj):
        events = Event.objects.filter(session=obj)

        has_plan = events.filter(type="plan_expanded").exists()
        has_phone = obj.user is not None

        if has_plan and not has_phone:
            return "❗ Dropped after viewing plan"

        if has_plan and has_phone:
            return "✅ Converted"

        return "—"

    def event_count(self, obj):
        return Event.objects.filter(session=obj).count()

    def top_plan(self, obj):
        events = Event.objects.filter(session=obj, type="plan_expanded")

        plan_counts = {}
        for e in events:
            plan = e.metadata.get("plan")
            if not plan:
                continue

            plan_counts[plan] = plan_counts.get(plan, 0) + 1

        if not plan_counts:
            return None

        return max(plan_counts, key=plan_counts.get)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("type", "session", "user", "created_at")
    list_filter = ("type",)