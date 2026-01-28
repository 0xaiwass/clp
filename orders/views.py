from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from carts.models import *
from .models import *
from django.urls import reverse
from django.http import HttpResponse
from .zarinpal_service import create_payment, zarinpal
##########################################################################################
class CreateOrderView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            cart = request.user.cart  # get the user's cart
        except Cart.DoesNotExist:
            messages.error(request, "سبد خرید شما خالی است.")
            return redirect("carts:cart_items")

        if not cart.items.exists():
            messages.error(request, "سبد خرید شما خالی است.")
            return redirect("carts:cart_items")

        # ✅ calculate total price from cart items
        total_price = 0
        for cart_item in cart.items.all():
            product = cart_item.product
            if product:
                total_price += product.offer_price * cart_item.quantity

        # ✅ create a new order for this checkout
        order = Order.objects.create(
            user=request.user,
            paid_status=Order.Status.WAITING,
            total_amount=total_price,
        )

        # ✅ copy cart items into the order
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_type=cart_item.product_type,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
            )

        # ✅ delete the cart after creating the order
        cart.delete()

        # ✅ initiate payment with Zarinpal
        callback_url = request.build_absolute_uri(
            reverse("orders:verify_payment", args=[order.id])
        )
        result = create_payment(
             amount=order.total_amount,
             description=f"Order #{order.factor_code}",
             callback_url=callback_url,
             email=request.user.email,
        )
        if "url" in result:
            return redirect(result["url"])
        else:
            return HttpResponse("Error creating payment: " + str(result))
##########################################################################################
class VerifyPaymentView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        authority = request.GET.get("Authority")
        status = request.GET.get("Status")
        if status == "OK":
            result = zarinpal.payment_gateway.verify({ 
            "amount": order.total_amount,
            "authority": authority,
        })
            if result.get("code") == 100:
                order.paid_status = Order.Status.PAID
                order.save()
                messages.success(request, f"Payment successful! RefID: {result.get('ref_id')}")
                return redirect("orders:order_detail", order_id=order.id)
            else:
                messages.error(request, f"Payment failed. Code: {result.get('code')}")
        else:
            messages.error(request, "Transaction canceled by user.")
        return redirect("orders:order_detail", order_id=order.id)
##########################################################################################
class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects.prefetch_related("items"),  # ✅ only prefetch 'items'
            id=order_id,
            user=request.user
        )

        # Get all items, and access their related product manually in template via `item.content_object`
        items = order.items.all()

        return render(request, "orders/order_detail.html", {
            "order": order,
            "items": items,
        })
##########################################################################################
class OrdersListView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items')
        return render(request, 'orders/orders.html', {'orders': orders})
##########################################################################################
class OrderDeleteView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if order:
            order.delete()
            messages.success(request, "سفارش با موفقیت حذف شد.")
        else:
            messages.error(request, "سفارشی یافت نشد.")
        return redirect("orders:order_list")
##########################################################################################
class RemoveOrderItemView(View):
    def get(self, request, item_id):
        # Get the item safely
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
        order = item.order

        # Delete the item
        item.delete()

        # If no more items left in the order, delete the order itself
        if not order.items.exists():
            order.delete()
            messages.info(request, "تمام محصولات این سفارش حذف شد. سفارش نیز حذف شد.")
            return redirect("orders:order_list")

        # Otherwise, redirect back to order detail
        return redirect("orders:order_detail", order_id=order.id)  # Change to your orders list page name
##########################################################################################
