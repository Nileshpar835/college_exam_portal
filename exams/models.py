from django.db import models
from django.conf import settings

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_quizzes')
    assigned_faculty = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    passing_score = models.IntegerField(default=40)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    option_1 = models.CharField(max_length=200)
    option_2 = models.CharField(max_length=200)
    option_3 = models.CharField(max_length=200)
    option_4 = models.CharField(max_length=200)
    correct_answer = models.IntegerField(choices=[(1,1), (2,2), (3,3), (4,4)])
    marks = models.IntegerField(default=1)

class Result(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    passed = models.BooleanField(default=False)
    submission_reason = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual Submission'),
            ('time_up', 'Time Expired'),
            ('tab_switch_violation', 'Tab Switch Violation'),
        ],
        default='manual'
    )