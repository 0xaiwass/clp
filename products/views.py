from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import *
from django.db.models import Q
from itertools import chain
########################################################
class ProductsListView(View):
    def get(self, request):
        clp_qs = CLP.objects.filter(is_active=True)
        amp_qs = AMP.objects.filter(is_active=True)
        equipment_qs = Equipment.objects.filter(is_active=True)
        string_eq = GuitarStrings.objects.filter(is_active=True)

        # GET params
        q = request.GET.get('q')
        ct = request.GET.get('category')
        order = request.GET.get('ordering')
        srs = request.GET.get("series")
        typ = request.GET.get("type")

        # --- Category filtering ---
        if ct == "clp":
            products = clp_qs
            if srs:
                products = products.filter(clp_series=srs)

        elif ct == "amp":
            products = amp_qs
            if typ:
                products = products.filter(type=typ)

        elif ct == "equipment":
            products = equipment_qs
            if typ:
                products = products.filter(equipment_series=typ)


        elif ct == "guitarstrings":
            products = string_eq
            if typ:
                products = products.filter(string_type=typ)

        else:
            # "All products" → combine into a list
            products = list(chain(clp_qs, amp_qs, equipment_qs, string_eq))

        # --- Search filtering ---
        if q:
            if isinstance(products, list):
                # Python-side filter for lists
                products = [
                    p for p in products if
                    q.lower() in (p.name or "").lower() or
                    q.lower() in (p.tags or "").lower() or
                    q.lower() in (p.description or "").lower()
                ]
            else:
                # DB-side filter for querysets
                products = products.filter(
                    Q(name__icontains=q) |
                    Q(tags__icontains=q) |
                    Q(description__icontains=q)
                )

        # --- Ordering ---
        if isinstance(products, list):
            if order == "cheap":
                products = sorted(products, key=lambda x: x.offer_price or 0)
            elif order == "expensive":
                products = sorted(products, key=lambda x: x.offer_price or 0, reverse=True)
            elif order == "new":
                products = sorted(products, key=lambda x: x.created_at, reverse=True)
        else:
            if order == "cheap":
                products = products.order_by("offer_price")
            elif order == "expensive":
                products = products.order_by("-offer_price")
            elif order == "new":
                products = products.order_by("-created_at")

        # --- Pagination ---
        paginator = Paginator(products, 6)  # 6 per page
        page = request.GET.get("page")

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        # --- Menu Context ---
        menu_items = [
            {"label": "CLP", "url": "?category=clp"},
            {"label": "Amps", "url": "?category=amp"},
            {"label": "Equipment", "url": "?category=equipment"},
            {"label": "Strings", "url": "?category=guitarstrings"},
        ]
        # --- Final context ---
        context = {
            "products": products,
            "page_obj": page_obj,
            "paginator": paginator,
            "is_paginated": page_obj.has_other_pages(),
            "menu_items": menu_items, # <--- now available in template
        }
        return render(request, "products/products.html", context)
########################################################
class ProductDetailView(View):
    model_map = {
        "clp": CLP,
        "amp": AMP,
        "equipment": Equipment,
        "guitarstrings": GuitarStrings,
    }

    def get(self, request, category, slug):
        # Pick correct model
        model = self.model_map.get(category)
        if not model:
            return redirect("products:products")

        # Get the current product
        product = get_object_or_404(model, slug=slug, is_active=True)

        # Related products (all active)
        clp_products = list(CLP.objects.filter(is_active=True))
        amp_products = list(AMP.objects.filter(is_active=True))
        equipment_products = list(Equipment.objects.filter(is_active=True))
        guitarstring_products = list(GuitarStrings.objects.filter(is_active=True))

        all_products = clp_products + amp_products + equipment_products + guitarstring_products

        # ✅ Filter most_selling products for the BestSelling slider
        best_selling_products = [p for p in all_products if getattr(p, "most_selling", False)]
        best_selling_products.sort(key=lambda x: x.created_at, reverse=True)  # newest first
        best_selling_slider = best_selling_products[:12]  # only top 12

        # Prepare specs dynamically
        exclude_fields = [
            "id", "slug", "tags", "old_price", "offer_price",
            "off_percent", "image", "description", "is_active",
            "is_offer", "is_new", "most_selling", "created_at"
        ]

        specs = []
        for field in product._meta.get_fields():
            if field.name in exclude_fields:
                continue
            if field.is_relation and not field.many_to_one:
                continue
            value = getattr(product, field.name, None)
            if value not in [None, "", 0, False]:
                display_name = getattr(field, "verbose_name", field.name)
                specs.append((display_name, value))

        context = {
            "product": product,                        # current product
            "related_products": all_products,          # full related products
            "latest_products": best_selling_slider,
            "category": category,
            "model_name": product._meta.model_name,
            "verbose_name": product.__class__.__name__,
            "specs": specs,                            # dynamic specs
        }

        return render(request, "products/products_detail.html", context)
########################################################