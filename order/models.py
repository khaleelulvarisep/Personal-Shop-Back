from django.db import models
from django.db import models
from django.conf import settings


class Order(models.Model):

    URGENCY_CHOICES = [
        ('2_hours', 'Standard (2 Hours)'),
        ('1_hour', 'Priority (1 Hour)'),
        ('30_mins', 'Flash (30 Minutes)')
    ]

    STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('shopping', 'Shopping'),
    ('on_the_way', 'On The Way'),
    ('delivered', 'Delivered'),
]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    items_text = models.TextField()

    note = models.TextField(blank=True, null=True)

    budget = models.DecimalField(max_digits=8, decimal_places=2)

    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default='2_hours'
    )

    phone_number = models.CharField(max_length=15)

    address_text = models.CharField()

    latitude = models.FloatField()

    longitude = models.FloatField()

    status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='pending'
)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer.email}"
# Create your models here.
