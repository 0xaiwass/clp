from django.shortcuts import render
from django.views import View
from products.models import *
from itertools import chain
from blogs.models import *
from django.http import HttpResponseNotFound
#-----------------------------------------------------------------------
class HomeView(View):
    def get(self, request):
        clp = CLP.objects.filter(is_active=True, is_offer=True )
        equipments = Equipment.objects.filter(is_active=True, is_offer=True )
        amp = AMP.objects.filter(is_active=True, is_offer=True )
        guitar_string = GuitarStrings.objects.filter(is_active=True, is_offer=True )

        offers = list(chain(clp, equipments, guitar_string, amp))

        # Sort by creation date (latest first) and limit to 6
        offers = sorted(offers, key=lambda p: p.created_at, reverse=True)[:15]

        ####################################################################

        ## Filter to New Products
        clp_new = CLP.objects.filter(is_active=True, is_new=True)
        amp_new = AMP.objects.filter(is_active=True, is_new=True)
        guitarstrings_new = GuitarStrings.objects.filter(is_active=True, is_new=True)
        equipments_new = Equipment.objects.filter(is_active=True, is_new=True)

        new = list(chain(clp_new, amp_new, guitarstrings_new, equipments_new))

        # sort items
        new = sorted(new, key=lambda p: p.created_at, reverse=True)[:15]

        ####################################################################
        c = CLP.objects.filter(is_active=True, most_selling=True)
        a = AMP.objects.filter(is_active=True, most_selling=True)
        g = GuitarStrings.objects.filter(is_active=True, most_selling=True)
        e = Equipment.objects.filter(is_active=True, most_selling=True)

        most_sell = list(chain(c, a, g, e))

        most_sell = sorted(most_sell, key=lambda p: p.created_at, reverse=True)[:15]

        ####################################################################
        # Filter for Blogs Post
        b = BlogPost.objects.filter(published=True).order_by('-created_at')[:15]
        ####################################################################

        context = {
            "offers": offers,
            "new":new,
            "most_sell":most_sell,
            "blog":b,
        }
        return render(request, 'home/home.html', context)
#-----------------------------------------------------------------------
class AboutUsView(View):
    def get(self, request):
        return render(request, 'home/aboutus.html')
#-----------------------------------------------------------------------
def custom_404(request, exception):
    return render(request, '404.html', status=404)
#-----------------------------------------------------------------------
