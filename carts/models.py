import random
import uuid
from django.db import models
from accounts.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
##############################################################################

def generate_cart_code():
    """Generate 5-digit random cart code."""
    return random.randint(10_000, 99_999)

# --------------------------------------------------------------------------
# 🛒 CART MODELS
# --------------------------------------------------------------------------

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    cart_code = models.PositiveIntegerField(default=generate_cart_code, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ID #{self.id} Cart ID #{self.cart_code} for {self.user.phone}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
##############################################################################
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    product = GenericForeignKey("product_type", "product_id")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product_type", "product_id")

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def total_price(self):
        return self.product.offer_price * self.quantity
##############################################################################