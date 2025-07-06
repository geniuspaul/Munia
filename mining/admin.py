# admin.py

from django.contrib import admin
from .models import (
    QuizQuestion,
    DailyQuiz,
    DailySignIn,
    QuizSubmission,
    SocialTask,
    SocialTaskSubmission,
    MiningSession
)
from audit.mixins import ExcelExportMixin


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('id', 'question', 'correct_option', 'created_at')
    search_fields = ('question',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    actions = ['export_selected_to_excel']
    excel_export_fields = ['id', 'question', 'correct_option', 'created_at']


@admin.register(DailyQuiz)
class DailyQuizAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('id', 'date', 'quiz')
    list_filter = ('date',)
    search_fields = ('quiz__question',)
    ordering = ('-date',)
    actions = ['export_selected_to_excel']
    excel_export_fields = ['id', 'date', 'quiz']


@admin.register(DailySignIn)
class DailySignInAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('id', 'user', 'mining_session', 'date')
    list_filter = ('date',)
    search_fields = ('user__username',)
    ordering = ('-date',)
    actions = ['export_selected_to_excel']
    excel_export_fields = ['id', 'user', 'mining_session', 'date']


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('id', 'user', 'quiz', 'selected_option', 'is_correct', 'mining_session', 'submitted_at')
    list_filter = ('is_correct', 'submitted_at')
    search_fields = ('user__username', 'quiz__question')
    ordering = ('-submitted_at',)
    actions = ['export_selected_to_excel']
    excel_export_fields = [
        'id', 'user', 'quiz', 'selected_option', 'is_correct', 'mining_session', 'submitted_at'
    ]


@admin.register(SocialTask)
class SocialTaskAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('id', 'title', 'task_type', 'reward', 'active', 'created_at')
    list_filter = ('task_type', 'active')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    actions = ['export_selected_to_excel']
    excel_export_fields = ['id', 'title', 'task_type', 'reward', 'active', 'created_at']


@admin.register(SocialTaskSubmission)
class SocialTaskSubmissionAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = ('id', 'user', 'task', 'approved', 'mining_session', 'submitted_at')
    list_filter = ('approved', 'submitted_at')
    search_fields = ('user__username', 'task__title', 'proof')
    ordering = ('-submitted_at',)
    actions = ['export_selected_to_excel', 'approve_selected', 'reject_selected']
    excel_export_fields = [
        'id', 'user', 'task', 'proof', 'approved', 'mining_session', 'submitted_at'
    ]

    @admin.action(description="Approve selected submissions")
    def approve_selected(self, request, queryset):
        queryset.update(approved=True)

    @admin.action(description="Reject selected submissions")
    def reject_selected(self, request, queryset):
        queryset.update(approved=False)


@admin.register(MiningSession)
class MiningSessionAdmin(admin.ModelAdmin, ExcelExportMixin):
    list_display = (
        'user', 'session_id', 'device_hash', 'ip_address',
        'status', 'start_time', 'end_time'
    )
    list_filter = ('status', 'start_time', 'end_time')
    search_fields = ('user__email', 'session_id', 'ip_address', 'device_hash')
    ordering = ('-start_time',)
    actions = ['mark_as_expired', 'mark_as_active', 'export_selected_to_excel']
    readonly_fields = ('session_id', 'start_time')
    excel_export_fields = [
        'id', 'user', 'session_id', 'device_hash', 'ip_address',
        'status', 'start_time', 'end_time'
    ]

    @admin.action(description="Mark selected sessions as expired")
    def mark_as_expired(self, request, queryset):
        updated = queryset.update(status='expired')
        self.message_user(request, f"{updated} session(s) marked as expired.")

    @admin.action(description="Mark selected sessions as active")
    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} session(s) marked as active.")
