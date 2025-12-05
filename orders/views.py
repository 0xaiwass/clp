from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from carts.models import *
from .models import *
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

        # ✅ create a new order for this checkout
        order = Order.objects.create(
            user=request.user,
            paid_status=Order.Status.WAITING,
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

        messages.success(request, f"سفارش شما با موفقیت ثبت شد. شماره سفارش : {order.factor_code}")
        return redirect("orders:order_list")
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