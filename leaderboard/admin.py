# leaderboard/admin.py
from django.contrib import admin
from .models import TopEarner, TopReferral

@admin.register(TopEarner)
class TopEarnerAdmin(admin.ModelAdmin):
    list_display = ('rank', 'user', 'total_earnings', 'last_updated')
    search_fields = ('user__email',)
    ordering = ('rank',)

@admin.register(TopReferral)
class TopReferralAdmin(admin.ModelAdmin):
    list_display = ('rank', 'user', 'total_referrals', 'last_updated')
    search_fields = ('user__email',)
    ordering = ('rank',)
