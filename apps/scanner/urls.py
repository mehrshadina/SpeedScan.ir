from django.urls import path
from .views import *

app_name = "scanner"

urlpatterns = [
    path('', index, name='index'),
    path('pagespeed-check/', pagespeed_check, name='pagespeed_check'),  # نمایش نتیجه تست
    #path('about/', about, name='about'),
    #path('faq/', faq, name='faq'),
    #path('contact/', contact, name='contact'),
    #path('blog/', blog, name='blog'),

    # API
    #path('api/pagespeed/', api_pagespeed, name='api_pagespeed'),
]