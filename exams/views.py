from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Result
from .forms import QuizForm, QuestionFormSet
from django.contrib import messages

@login_required
def quiz_list(request):
    if request.user.role == 'STUDENT':
        quizzes = Quiz.objects.filter(assigned_faculty__isnull=False)
        # Add user results to each quiz for students
        for quiz in quizzes:
            try:
                quiz.user_results = Result.objects.get(user=request.user, quiz=quiz)
            except Result.DoesNotExist:
                quiz.user_results = None
    else:
        quizzes = Quiz.objects.all()
    return render(request, 'exams/quiz_list.html', {'quizzes': quizzes})

@login_required
def quiz_create(request):
    if request.user.role == 'STUDENT':
        messages.error(request, 'Students cannot create quizzes.')
        return redirect('exams:quiz_list')
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.creator = request.user
            quiz.save()
            
            # Process questions
            question_count = 0
            for key in request.POST.keys():
                if key.startswith('questions-') and key.endswith('-text'):
                    index = key.split('-')[1]
                    text = request.POST.get(f'questions-{index}-text')
                    option_1 = request.POST.get(f'questions-{index}-option_1')
                    option_2 = request.POST.get(f'questions-{index}-option_2')
                    option_3 = request.POST.get(f'questions-{index}-option_3')
                    option_4 = request.POST.get(f'questions-{index}-option_4')
                    correct_answer = request.POST.get(f'questions-{index}-correct_answer')
                    marks = request.POST.get(f'questions-{index}-marks', 1)
                    
                    if all([text, option_1, option_2, option_3, option_4, correct_answer]):
                        Question.objects.create(
                            quiz=quiz,
                            text=text,
                            option_1=option_1,
                            option_2=option_2,
                            option_3=option_3,
                            option_4=option_4,
                            correct_answer=int(correct_answer),
                            marks=int(marks)
                        )
                        question_count += 1
            
            if question_count > 0:
                messages.success(request, f'Quiz created successfully with {question_count} questions!')
                return redirect('exams:quiz_list')
            else:
                quiz.delete()
                messages.error(request, 'Please add at least one question to the quiz.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuizForm()
    
    return render(request, 'exams/quiz_create.html', {'form': form})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    # Add user result for students
    if request.user.role == 'STUDENT':
        try:
            quiz.user_results = Result.objects.get(user=request.user, quiz=quiz)
        except Result.DoesNotExist:
            quiz.user_results = None
    return render(request, 'exams/quiz_detail.html', {'quiz': quiz})

@login_required

def quiz_attempt(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if student has already taken this quiz
    if request.user.role == 'STUDENT':
        existing_result = Result.objects.filter(user=request.user, quiz=quiz).first()
        if existing_result:
            messages.warning(request, 'You have already taken this quiz and cannot retake it.')
            return redirect('exams:quiz_result', result_id=existing_result.id)
    
    if request.method == 'POST':
        # Double-check before processing submission
        if request.user.role == 'STUDENT':
            existing_result = Result.objects.filter(user=request.user, quiz=quiz).first()
            if existing_result:
                messages.error(request, 'Quiz submission failed: You have already completed this quiz.')
                return redirect('exams:quiz_result', result_id=existing_result.id)
        
        # Get submission reason
        submission_reason = request.POST.get('submission_reason', 'manual')
        security_data = request.POST.get('security_data', '{}')
        
        # Process quiz submission
        score = 0
        total_marks = 0
        correct_answers = 0
        total_questions = quiz.question_set.count()
        
        for question in quiz.question_set.all():
            total_marks += question.marks
            selected_answer = request.POST.get(f'q{question.id}')
            
            if selected_answer and int(selected_answer) == question.correct_answer:
                score += question.marks
                correct_answers += 1
        
        # Calculate percentage
        percentage = (score / total_marks * 100) if total_marks > 0 else 0
        passed = percentage >= quiz.passing_score
        
        # Create result record
        result = Result.objects.create(
            user=request.user,
            quiz=quiz,
            score=percentage,
            passed=passed,
            submission_reason=submission_reason,
            security_violations=security_data
        )
        
        # Add success message based on submission reason
        if submission_reason == 'tab_switch_violation':
            messages.warning(request, 'Quiz was auto-submitted due to tab switching violation.')
        elif submission_reason == 'time_up':
            messages.info(request, 'Quiz was auto-submitted as time expired.')
        else:
            messages.success(request, 'Quiz submitted successfully!')
        
        return redirect('exams:quiz_result', result_id=result.id)
    
    return render(request, 'exams/quiz_attempt.html', {'quiz': quiz})

@login_required
def quiz_result(request, result_id):
    result = get_object_or_404(Result, pk=result_id, user=request.user)
    return render(request, 'exams/quiz_result.html', {'result': result})

@login_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Only creator or HOD can edit
    if request.user != quiz.creator and request.user.role != 'HOD':
        messages.error(request, 'You do not have permission to edit this quiz.')
        return redirect('exams:quiz_detail', quiz_id=quiz.id)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            quiz = form.save()
            
            # Delete existing questions
            quiz.question_set.all().delete()
            
            # Process new questions
            question_count = 0
            for key in request.POST.keys():
                if key.startswith('questions-') and key.endswith('-text'):
                    index = key.split('-')[1]
                    text = request.POST.get(f'questions-{index}-text')
                    option_1 = request.POST.get(f'questions-{index}-option_1')
                    option_2 = request.POST.get(f'questions-{index}-option_2')
                    option_3 = request.POST.get(f'questions-{index}-option_3')
                    option_4 = request.POST.get(f'questions-{index}-option_4')
                    correct_answer = request.POST.get(f'questions-{index}-correct_answer')
                    marks = request.POST.get(f'questions-{index}-marks', 1)
                    
                    if all([text, option_1, option_2, option_3, option_4, correct_answer]):
                        Question.objects.create(
                            quiz=quiz,
                            text=text,
                            option_1=option_1,
                            option_2=option_2,
                            option_3=option_3,
                            option_4=option_4,
                            correct_answer=int(correct_answer),
                            marks=int(marks)
                        )
                        question_count += 1
            
            if question_count > 0:
                messages.success(request, f'Quiz updated successfully with {question_count} questions!')
                return redirect('exams:quiz_detail', quiz_id=quiz.id)
            else:
                messages.error(request, 'Please add at least one question to the quiz.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'exams/quiz_edit.html', {'form': form, 'quiz': quiz})

@login_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Only creator or HOD can delete
    if request.user != quiz.creator and request.user.role != 'HOD':
        messages.error(request, 'You do not have permission to delete this quiz.')
        return redirect('exams:quiz_detail', quiz_id=quiz.id)
    
    if request.method == 'POST':
        quiz_title = quiz.title
        quiz.delete()
        messages.success(request, f'Quiz "{quiz_title}" has been deleted successfully.')
        return redirect('exams:quiz_list')
    
    return render(request, 'exams/quiz_delete.html', {'quiz': quiz})
