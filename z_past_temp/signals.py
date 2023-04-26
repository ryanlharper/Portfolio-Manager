from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Strategy, Position

@receiver(post_save, sender=Strategy)
def create_position(sender, instance, created, **kwargs):
    if created:
        # Create a new Position object for the user's strategy with 100% allocation to cash
        position = Position.objects.create(
            user=instance.user,
            strategy=instance,
            symbol='*USD',
            description='Cash',
            cost=1.00,
            quantity=100,
        )
        position.save()
