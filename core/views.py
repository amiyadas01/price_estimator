from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from .models import SearchQuery
from .services import fetch_market_prices
from .scraper import scrape_fallback_all, get_price_range
from authlib.integrations.django_client import OAuth
from urllib.parse import quote_plus, urlencode

oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.session.get("user")
        return context

class HistoryView(TemplateView):
    template_name = "core/history.html"

    def get(self, request, *args, **kwargs):
        user_info = request.session.get('user')
        if not user_info:
            return redirect('login')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_info = self.request.session.get('user')
        email = user_info.get('email')
        context["searches"] = SearchQuery.objects.filter(user_email=email)[:20]
        context["user"] = user_info
        return context

def search(request):
    query_text = request.GET.get('q', '').strip()
    if not query_text:
        return redirect('home')
    
    # 1. Try API first (PRIMARY)
    results = fetch_market_prices(query_text)
    
    # 2. If API returns nothing, use Scraper (FALLBACK)
    if not results:
        results = scrape_fallback_all(query_text)
        
    # Calculate price range from results
    price_min, price_max = get_price_range(results)
    
    # Save search query to DB
    user_info = request.session.get('user')
    search_query = SearchQuery(
        query=query_text,
        result_count=len(results),
        price_min=price_min,
        price_max=price_max
    )
    
    if user_info:
        search_query.user_email = user_info.get('email')
    else:
        if not request.session.session_key:
            request.session.create()
        search_query.user_session = request.session.session_key
    
    search_query.save()
    
    return render(
        request,
        "core/search_results.html",
        context={
            "query": query_text,
            "results": results,
            "price_min": price_min,
            "price_max": price_max,
            "user": user_info
        }
    )

def login_view(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback_view(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token.get("userinfo")
    return redirect("home")

def logout_view(request):
    request.session.flush()
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": settings.AUTH0_LOGOUT_REDIRECT,
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        )
    )
