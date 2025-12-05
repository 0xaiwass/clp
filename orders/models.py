import random
import uuid
from django.db import models
from accounts.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
########################################################################################

def generate_order_code():
    """Generate 8-digit random factor code."""
    return random.randint(10_000_000, 99_999_999)

# --------------------------------------------------------------------------
# 📦 ORDER MODELS
# --------------------------------------------------------------------------
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    factor_code = models.PositiveIntegerField(default=generate_order_code, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Status(models.TextChoices):
        PAID = 'paid', 'پرداخت شده'
        WAITING = 'waiting', 'پرداخت نشده'
    paid_status = models.CharField(
        max_length=15,
        choices=Status.choices,
        verbose_name='وضعیت پرداختی',
        default=Status.WAITING
    )

    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ID #{self.id} Order #{self.factor_code} - {self.user.phone}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
########################################################################################
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    product = GenericForeignKey("product_type", "product_id")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("order", "product_type", "product_id")

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def total_price(self):
        return self.product.offer_price * self.quantity
########################################################################################