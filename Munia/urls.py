
from django.contrib import admin
from django.urls import path, include
from django.utils.module_loading import import_string

home = import_string('core.views.home')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include("core.urls")),
    path('wallet/', include("wallet.urls")),
    path('mining/', include("mining.urls")),
    path('referral/', include("referral.urls")),
    path('leaderboard/', include("leaderboard.urls")),
    
    path("", home),
]
