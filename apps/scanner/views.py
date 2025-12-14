import os, json, requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import PagesSpeedTests
from django.utils import timezone

def index(request):
    return render(request, 'index.html')

def pagespeed_result(request, access_link):
    try:
        # پیدا کردن رکورد با UUID
        test_record = get_object_or_404(PagesSpeedTests, access_link=access_link)

        # چک کردن وجود فایل
        if not os.path.exists(test_record.result_file):
            return render(request, "error.html", {
                "title": "نتیجه پیدا نشد",
                "message": "فایل نتیجه تست پیدا نشد یا حذف شده است."
            })

        # خواندن فایل JSON
        with open(test_record.result_file, "r", encoding="utf-8") as f:
            try:
                result_data = json.load(f)
            except json.JSONDecodeError:
                return render(request, "error.html", {
                    "title": "خطای فایل",
                    "message": "فایل نتیجه تست خراب است و نمی‌توان آن را بارگذاری کرد."
                })

        # رندر template با داده‌ها
        return render(request, "result.html", {
            #"site_url": test_record.site_url,
            #"created_at": test_record.created_at,
            "result_data": json.dumps(result_data),
            #"success": test_record.success
        })

    except PagesSpeedTests.DoesNotExist:
        return render(request, "error.html", {
            "title": "لینک اشتباه است",
            "message": "نتیجه تست با این لینک پیدا نشد."
        })

    except Exception as e:
        # خطای ناشناخته
        return render(request, "error.html", {
            "title": "خطای داخلی",
            "message": "خطای ناشناخته‌ای رخ داد. لطفاً دوباره تلاش کنید."
        })

def pagespeed_check_api(request):
    url = request.GET.get("url")

    # Normalize URL
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        response.raise_for_status()
        url = response.url

        for site in {'google.com', 'www.google.com', 'facebook.com', 'www.facebook.com'}:
            if site in url:
                return JsonResponse(
                    {"error": "تحلیل سایت‌های گوگل و فیسبوک مجاز نیست."},
                    status=403
                )

    except requests.exceptions.MissingSchema:
        return JsonResponse(
            {"error": "آدرس سایت ناقص است. http یا https وارد نشده است."},
            status=400
        )

    except requests.exceptions.InvalidURL:
        return JsonResponse(
            {"error": "فرمت آدرس سایت نادرست است."},
            status=400
        )

    except requests.exceptions.Timeout:
        return JsonResponse(
            {"error": "سایت در زمان مشخص پاسخ نداد (Timeout)."},
            status=504
        )

    except requests.exceptions.SSLError:
        return JsonResponse(
            {"error": "گواهی SSL سایت معتبر نیست."},
            status=526
        )

    except requests.exceptions.TooManyRedirects:
        return JsonResponse(
            {"error": "سایت دچار ریدایرکت نامحدود است."},
            status=508
        )

    except requests.exceptions.ConnectionError:
        return JsonResponse(
            {"error": "اتصال به سایت ممکن نیست. دامنه اشتباه یا سرور در دسترس نیست."},
            status=503
        )

    except requests.exceptions.HTTPError as e:
        return JsonResponse(
            {
                "error": "سایت پاسخ خطا داد.",
                "status_code": e.response.status_code
            },
            status=502
        )

    except Exception:
        return JsonResponse(
            {"error": "خطای غیرمنتظره‌ای هنگام بررسی سایت رخ داد."},
            status=500
        )


    api_key = getattr(settings, "PAGESPEED_API_KEY", None)

    # Base parameters for remote analysis
    params = {
        "url": url,
        "strategy": "mobile",
        "category": ["performance", "accessibility", "best-practices", "seo", "pwa"],
    }

    if api_key:
        params["key"] = api_key

    try:
        # Perform remote analysis request
        resp = requests.get(settings.GOOGLE_PAGESPEED_API_URL, params=params, timeout=40)
        resp.raise_for_status()
        data = resp.json()

    # ---------------- NETWORK ERRORS ----------------
    except requests.exceptions.Timeout:
        return JsonResponse(
            {"error": "سرور تحلیل به‌موقع پاسخ نداد. لطفاً دوباره تلاش کنید."},
            status=504
        )

    except requests.exceptions.ConnectionError:
        return JsonResponse(
            {"error": "برقراری ارتباط با سرویس تحلیل امکان‌پذیر نبود."},
            status=503
        )

    except requests.exceptions.HTTPError:
        return JsonResponse(
            {"error": "در هنگام دریافت اطلاعات از سرویس تحلیل مشکلی رخ داد."},
            status=500
        )

    except Exception:
        return JsonResponse(
            {"error": "مشکلی پیش آمده و درخواست کامل انجام نشد."},
            status=500
        )
    
    # ---------------- LOGICAL & SOFT ERRORS ----------------
    lighthouse = data.get("lighthouseResult")
    if lighthouse is None:
        # No analysis data returned
        return JsonResponse(
            {"error": "امکان تحلیل این آدرس وجود نداشت. لطفاً آدرس را بررسی کرده و دوباره تست کنید."},
            status=422
        )

    audits = lighthouse.get("audits", {})
    if not audits:
        # Analysis started but returned no audits at all
        return JsonResponse(
            {"error": "امکان تکمیل فرایند تحلیل وجود نداشت. احتمالاً سایت موقتاً پاسخگو نبوده است."},
            status=422
        )

    # Check internal audit errors (CAPTCHA, blocked resources, failed audits)
    internal_errors = []
    for key, audit in audits.items():
        if isinstance(audit, dict):
            err = audit.get("errorMessage") or audit.get("warning")
            if err:
                internal_errors.append(err)

    if internal_errors:
        # Do not expose backend/internal error messages
        return JsonResponse(
            {
                "error": "تحلیل به‌طور کامل انجام نشد. لطفاً چند لحظه بعد دوباره تلاش کنید."
            },
            status=422
        )

    # Missing categories (incomplete or corrupted data)
    if "categories" not in lighthouse:
        return JsonResponse(
            {"error": "اطلاعات کامل برای تحلیل دریافت نشد."},
            status=422
        )

    # ---------------- SAVE RESULT ----------------
    website_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join(settings.BASE_DIR, "data", website_name)
    os.makedirs(folder_path, exist_ok=True)

    file_name = f"{timestamp}.json"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ---------------- SAVE DATABASE RECORD----------------
    user_ip = get_client_ip(request)
    test_record = PagesSpeedTests.objects.create(
        site_url=url,
        user_ip=user_ip,
        result_file=file_path,
        #success=True
    )

    # لینک اختصاصی برای مشاهده نتیجه
    return JsonResponse({"access_link": test_record.access_link}, status=200)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip