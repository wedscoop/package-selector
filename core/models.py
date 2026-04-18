from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'Unknown'} ({self.phone})"


class Session(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session_id


class Event(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=50)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.type == "plan_expanded":
            return f"Viewed {self.metadata.get('plan')} ({self.metadata.get('repeat_count')}x)"
        elif self.type == "return_visit":
            return "Returned to site"
        elif self.type == "return_after_gap":
            return f"Returned after {self.metadata.get('hours')} hrs"
        elif self.type == "phone_captured":
            return "Entered details"
        return self.type
        
class DemandSlot(models.Model):
    event_date = models.DateField(unique=True)
    booking_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.event_date} ({self.booking_count})"