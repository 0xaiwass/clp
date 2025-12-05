from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import *
from .models import *
from django.http import JsonResponse
######################################################################################
class CartView(LoginRequiredMixin, View):
    def get(self, request):
        product_model = request.GET.get("product_model")
        product_id = request.GET.get("product_id")
        try:
            quantity = int(request.GET.get("quantity", 1))
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1

        model_map = {
            "clp": CLP,
            "amp": AMP,
            "equipment": Equipment,
            "guitarstrings": GuitarStrings,
        }

        model = model_map.get(product_model.lower())
        if not model:
            messages.error(request, "محصول یافت نشد.", extra_tags="danger")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        try:
            product = model.objects.get(pk=product_id)
        except model.DoesNotExist:
            messages.error(request, "محصول یافت نشد.", extra_tags="danger")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # ✅ Get or create the user's cart
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # ✅ Add or update item
        content_type = ContentType.objects.get_for_model(product)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_type=content_type,
            product_id=product.id,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity = quantity
            cart_item.save()

        messages.success(request, "محصول به سبدخرید اضافه شد.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
######################################################################################
class CartItemsView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product_type')
        items_data = []
        total = 0
        for item in cart_items:
            product = item.product
            if not product:
                continue
            items_data.append({
                'id': item.id,
                'name': product.name,
                'image': product.image.url if product.image else '',
                'quantity': item.quantity,
                'price': product.offer_price,
            })
            total += product.offer_price * item.quantity
        return JsonResponse({
            'items': items_data,
            'total': total
        })
######################################################################################
class CartItemDeleteView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return JsonResponse({'success': True})