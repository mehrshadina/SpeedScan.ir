import json
import requests
from django.conf import settings
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def pagespeed_check(request):
    url = request.GET.get("url")
    strategy = request.POST.get("strategy", "mobile")
    api_key = getattr(settings, "PAGESPEED_API_KEY", None)

    params = {
        "url": url,
        "strategy": strategy,
        "category": ["performance","accessibility","best-practices","seo","pwa"],
    }
    if api_key:
        params["key"] = api_key

    try:
        resp = requests.get(settings.GOOGLE_PAGESPEED_API_URL, params=params, timeout=40)
        resp.raise_for_status()
        print(resp.url)
        data = resp.json()
    except Exception as e:
        return render(request, "result.html", {"error": str(e), "url": url})

    # تبدیل به JSON رشته‌ای برای JS
    raw_json = json.dumps(data, ensure_ascii=False)

    return render(request, "result.html", {"raw_json": raw_json})
