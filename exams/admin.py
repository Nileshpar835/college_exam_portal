from django.contrib import admin
from .models import Quiz, Question, Result

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'duration', 'created_at')
    inlines = [QuestionInline]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Result)
