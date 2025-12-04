"""
pagespeed_translator_clean.py

🔥 ویژگی‌ها:
- کلیدهای پاسخ PageSpeed تغییر نمی‌کنند
- score یا numericValue یا هر مقدار دیگر دست‌کاری نمی‌شود
- فقط یک نقشه (MAP) فارسی لایت‌هاوس تعریف می‌شود
- تابع ترجمه یک ساختار جدید می‌سازد که:
    {
        "original": { ... JSON اصلی ... },
        "translated": { ... ترجمه فارسی فقط برای عنوان/توضیح ... }
    }

نحوه‌ی استفاده:
from pagespeed_translator_clean import translate_pagespeed

result = translate_pagespeed(pagespeed_json)
print(result["original"])   # همان JSON اصلی
print(result["translated"]) # ترجمه فارسی
"""

from typing import Dict, Any

# ======================== ترجمه فارسی آدیت‌ها و فیلدهای مهم ========================

TRANSLATION_MAP: Dict[str, Dict[str, str]] = {
    "first-contentful-paint": {
        "title_fa": "اولین رندر محتوا (FCP)",
        "description_fa": "زمانی که اولین محتوای صفحه برای کاربر ظاهر می‌شود."
    },
    "largest-contentful-paint": {
        "title_fa": "بزرگ‌ترین رندر محتوا (LCP)",
        "description_fa": "بزرگ‌ترین عنصر بصری که در viewport نمایش داده می‌شود."
    },
    "cumulative-layout-shift": {
        "title_fa": "تغییر چیدمان تجمعی (CLS)",
        "description_fa": "میزان جابه‌جایی ناخواسته عناصر حین بارگذاری."
    },
    "speed-index": {
        "title_fa": "شاخص سرعت (SI)",
        "description_fa": "سرعت قابل مشاهده بودن محتوا برای کاربر."
    },
    "total-blocking-time": {
        "title_fa": "زمان مسدودشدگی کل (TBT)",
        "description_fa": "زمان بین FCP تا TTI که صفحه پاسخگو نیست."
    },
    "interactive": {
        "title_fa": "زمان تا تعامل‌پذیری (TTI)",
        "description_fa": "زمان لازم برای اینکه صفحه قابل تعامل شود."
    },
    "first-input-delay": {
        "title_fa": "تاخیر اولین ورودی (FID)",
        "description_fa": "زمان پاسخ صفحه به اولین تعامل کاربر."
    },
    "server-response-time": {
        "title_fa": "زمان پاسخ سرور",
        "description_fa": "مدت زمانی که سرور برای پاسخ اولیه نیاز دارد."
    },
    # دسته‌بندی‌ها
    "performance": {
        "title_fa": "عملکرد",
        "description_fa": "معیارهای عملکرد و سرعت صفحه"
    },
    "accessibility": {
        "title_fa": "دسترس‌پذیری",
        "description_fa": "شاخص‌های مربوط به دسترس‌پذیری محتوا"
    },
    "seo": {
        "title_fa": "سئو",
        "description_fa": "شاخص‌های بهینه‌سازی برای موتور جستجو"
    },
    "best-practices": {
        "title_fa": "بهترین شیوه‌ها",
        "description_fa": "رعایت اصول صحیح توسعه وب"
    }
}

# ======================== تابع ترجمه ========================

def translate_pagespeed(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    هیچ تغییری در JSON اصلی نمی‌دهد.
    فقط ترجمه فارسی کنار آن تولید می‌کند.

    خروجی:
    {
        "original": {...},
        "translated": {
            "audits": {
                "first-contentful-paint": {
                    "title_fa": "...",
                    "description_fa": "..."
                },
                ...
            },
            "categories": {
                "performance": { ... },
                ...
            }
        }
    }
    """
    translated = {
        "audits": {},
        "categories": {},
        "meta": {}
    }

    # ترجمه audits
    audits = data.get("lighthouseResult", {}).get("audits", {})
    for audit_id, audit_data in audits.items():
        if audit_id in TRANSLATION_MAP:
            translated["audits"][audit_id] = {
                "title_fa": TRANSLATION_MAP[audit_id]["title_fa"],
                "description_fa": TRANSLATION_MAP[audit_id]["description_fa"],
                "original_title": audit_data.get("title"),
                "original_description": audit_data.get("description")
            }

    # ترجمه categories
    categories = data.get("lighthouseResult", {}).get("categories", {})
    for cat_id, cat_data in categories.items():
        if cat_id in TRANSLATION_MAP:
            translated["categories"][cat_id] = {
                "title_fa": TRANSLATION_MAP[cat_id]["title_fa"],
                "description_fa": TRANSLATION_MAP[cat_id]["description_fa"],
                "original_title": cat_data.get("title")
            }

    # اضافه کردن اطلاعات متا
    translated["meta"]["url"] = data.get("id")
    translated["meta"]["final_url"] = data.get("lighthouseResult", {}).get("finalUrl")
    translated["meta"]["fetch_time"] = data.get("lighthouseResult", {}).get("fetchTime")
    translated["meta"]["lighthouse_version"] = data.get("lighthouseResult", {}).get("lighthouseVersion")

    return {
        "original": data,       # JSON بدون تغییر
        "translated": translated  # ترجمه فارسی
    }


# ======================== نمونه استفاده ========================

if __name__ == "__main__":
    import json

    sample_json = {
        "id": "https://example.com",
        "finalUrl": "https://example.com/",
        "fetchTime": "2025-12-04T10:00:00Z",
        "lighthouseVersion": "10.0.0",
        "categories": {
            "performance": {"score": 0.88, "title": "Performance"},
            "accessibility": {"score": 0.95, "title": "Accessibility"}
        },
        "audits": {
            "first-contentful-paint": {
                "id": "first-contentful-paint",
                "title": "First Contentful Paint",
                "description": "Time to first contentful paint",
                "score": 0.9,
                "numericValue": 1234
            },
            "largest-contentful-paint": {
                "id": "largest-contentful-paint",
                "title": "Largest Contentful Paint",
                "score": 0.7,
                "numericValue": 2500
            }
        },
        "loadingExperience": {
            "metrics": {
                "first_contentful_paint": {"percentile": 1200, "category": "FAST"},
                "first_input_delay": {"percentile": 15, "category": "FAST"}
            }
        }
    }

    translated_json = translate_pagespeed_values(sample_json)
    print(json.dumps(translated_json, ensure_ascii=False, indent=2))
