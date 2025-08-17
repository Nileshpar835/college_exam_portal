from django import forms
from .models import Quiz, Question

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'duration', 'passing_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter quiz title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter quiz description'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Duration in minutes'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'placeholder': 'Passing score percentage'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_1', 'option_2', 'option_3', 'option_4', 'correct_answer', 'marks']

QuestionFormSet = forms.inlineformset_factory(
    Quiz, Question, form=QuestionForm,
    extra=1, can_delete=True, min_num=1
)
