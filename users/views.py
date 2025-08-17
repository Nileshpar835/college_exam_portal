from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import CustomUserCreationForm, UserProfileForm, CustomPasswordChangeForm
from .models import CustomUser
from exams.models import Result, Quiz
from materials.models import News

import uuid



def home(request):
    """
    Redirect users to dashboard if authenticated, otherwise to login.
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return redirect('users:login')

def register(request):
    """
    Handle user registration with email verification (modern HTML email).
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email is verified
            # email_verification_token should be auto-set by model default
            user.save()

            # Send verification email
            try:
                verify_url = request.build_absolute_uri(
                    reverse('users:verify_email', args=[str(user.email_verification_token)])
                )

                subject = "Verify your email - College Exam Portal"
                # Render modern HTML template
                html_content = render_to_string('users/verify_email.html', {
                    'username': user.username,
                    'verify_url': verify_url,
                })
                text_content = strip_tags(html_content)  # Plain text fallback

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                    to=[user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                messages.success(request, 'Registration successful 🎉. Please check your email to verify your account.')
            except Exception as e:
                messages.warning(request, f'Registered, but failed to send verification email: {e}')

            return redirect('users:login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    Handle user login with email verification check.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Debug: Check if credentials are received
        print(f"Login attempt - Username/Email: {username}, Password received: {bool(password)}")
        
        # Check if user exists by username or email
        try:
            from django.db.models import Q
            user_exists = CustomUser.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()
            if user_exists:
                print(f"User found: {user_exists.username}, Email: {user_exists.email}, Active: {user_exists.is_active}, Email verified: {user_exists.is_email_verified}")
            else:
                print("No user found with this username/email")
        except Exception as e:
            print(f"Error checking user: {e}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"User authenticated: {user.username}, Active: {user.is_active}, Email verified: {user.is_email_verified}")
            
            # Check if user is active and email is verified
            if not user.is_active:
                messages.error(request, 'Your account is not active. Please verify your email.')
                return render(request, 'users/login.html')
            elif not user.is_email_verified:
                messages.error(request, 'Please verify your email before logging in.')
                return render(request, 'users/login.html')
            else:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('users:dashboard')
        else:
            print("Authentication failed")
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'users/login.html')


def logout_view(request):
    """
    Logout user and redirect to login page.
    """
    logout(request)
    return redirect('users:login')


def verify_email(request, token):
    """
    Verify user's email using token.
    """
    try:
        user = CustomUser.objects.get(email_verification_token=token)
        user.is_email_verified = True
        user.is_active = True
        user.save()
        messages.success(request, 'Email verified successfully. You can now login.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    return redirect('users:login')

def access_denied(request):
    """
    Safe page for unauthorized access attempts.
    """
    return render(request, 'users/access_denied.html')


@login_required
def dashboard(request):
    """
    Display dashboard based on user role.
    """
    role = (request.user.role or '').upper()
    print(f"Dashboard access - User: {request.user.username}, Role: {role}")
    
    template_name = f'users/dashboard_{request.user.role.lower()}.html'
    context = {'user': request.user}

    if role == 'HOD':
        context.update({
            'faculty_count': CustomUser.objects.filter(role='FACULTY').count(),
            'student_count': CustomUser.objects.filter(role='STUDENT').count(),
            'quiz_count': Quiz.objects.count(),
            'recent_results': Result.objects.order_by('-completed_at')[:10],
            'announcements': News.objects.order_by('-created_at')[:10],
        })
    elif role == 'FACULTY':
        from materials.models import StudyMaterial
        context.update({
            'created_quizzes': request.user.created_quizzes.order_by('-created_at')[:10],
            'student_results': Result.objects.filter(quiz__creator=request.user).order_by('-completed_at')[:20],
            'materials': StudyMaterial.objects.filter(uploaded_by=request.user).order_by('-created_at')[:10],
            'announcements': News.objects.order_by('-created_at')[:10],
        })
    elif role == 'STUDENT':
        from materials.models import StudyMaterial
        
        # Get upcoming quizzes with completion status
        upcoming_quizzes = Quiz.objects.order_by('-created_at')[:10]
        for quiz in upcoming_quizzes:
            try:
                quiz.user_results = Result.objects.get(user=request.user, quiz=quiz)
            except Result.DoesNotExist:
                quiz.user_results = None
        
        context.update({
            'upcoming_quizzes': upcoming_quizzes,
            'materials': StudyMaterial.objects.order_by('-created_at')[:10],
            'user_results': Result.objects.filter(user=request.user).order_by('-completed_at')[:10],
            'announcements': News.objects.order_by('-created_at')[:10],
        })

    return render(request, template_name, context)



# new view for HOD to create faculty
@login_required
def create_faculty(request):
    """
    Allow HOD to create a Faculty account with email verification.
    """
    if request.user.role != 'HOD':
        messages.error(request, 'Unauthorized')
        return redirect('users:access_denied')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'FACULTY'
            user.is_active = False  # Faculty will activate after email verification
            user.is_email_verified = False  
            user.save()

            # Send verification email
            try:
                verify_url = request.build_absolute_uri(
                    reverse('users:verify_email', args=[str(user.email_verification_token)])
                )

                subject = "Faculty Account - Verify your email"
                html_content = render_to_string('users/verify_email.html', {
                    'username': user.username,
                    'verify_url': verify_url,
                })
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                    to=[user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                messages.success(request, 'Faculty account created. Verification email sent ✅.')
            except Exception as e:
                messages.warning(request, f'Faculty created but failed to send email: {e}')

            return redirect('users:user_list')
    else:
        form = CustomUserCreationForm(initial={'role': 'FACULTY'})

    return render(request, 'users/create_faculty.html', {'form': form})



@login_required
def edit_user(request, user_id):
    """
    Allow HOD to edit faculty and student details.
    """
    if request.user.role != 'HOD':
        messages.error(request, 'Unauthorized access.')
        return redirect('users:access_denied')
    
    user_to_edit = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent HOD from editing other HODs
    if user_to_edit.role == 'HOD':
        messages.error(request, 'Cannot edit HOD accounts.')
        return redirect('users:user_list')
    
    if request.method == 'POST':
        # Update user details
        user_to_edit.username = request.POST.get('username')
        user_to_edit.email = request.POST.get('email')
        user_to_edit.first_name = request.POST.get('first_name', '')
        user_to_edit.last_name = request.POST.get('last_name', '')
        user_to_edit.department = request.POST.get('department')
        
        # Only allow role change between FACULTY and STUDENT
        new_role = request.POST.get('role')
        if new_role in ['FACULTY', 'STUDENT']:
            user_to_edit.role = new_role
        
        try:
            user_to_edit.save()
            messages.success(request, f'User "{user_to_edit.username}" updated successfully.')
            return redirect('users:user_list')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    context = {
        'user_to_edit': user_to_edit,
    }
    return render(request, 'users/edit_user.html', context)

@login_required
def delete_user(request, user_id):
    """
    Allow HOD to delete faculty and student accounts.
    """
    if request.user.role != 'HOD':
        messages.error(request, 'Unauthorized access.')
        return redirect('users:access_denied')
    
    user_to_delete = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent HOD from deleting other HODs or themselves
    if user_to_delete.role == 'HOD' or user_to_delete == request.user:
        messages.error(request, 'Cannot delete HOD accounts.')
        return redirect('users:user_list')
    
    if request.method == 'POST':
        username = user_to_delete.username
        user_role = user_to_delete.get_role_display()
        user_to_delete.delete()
        messages.success(request, f'{user_role} "{username}" has been deleted successfully.')
        return redirect('users:user_list')
    
    context = {
        'user_to_delete': user_to_delete,
    }
    return render(request, 'users/delete_user.html', context)

@login_required
def toggle_user_status(request, user_id):
    """
    Allow HOD to activate/deactivate user accounts.
    """
    if request.user.role != 'HOD':
        messages.error(request, 'Unauthorized access.')
        return redirect('users:access_denied')
    
    user_to_toggle = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent HOD from deactivating other HODs
    if user_to_toggle.role == 'HOD':
        messages.error(request, 'Cannot modify HOD account status.')
        return redirect('users:user_list')
    
    user_to_toggle.is_active = not user_to_toggle.is_active
    user_to_toggle.save()
    
    status = "activated" if user_to_toggle.is_active else "deactivated"
    messages.success(request, f'User "{user_to_toggle.username}" has been {status}.')
    
    return redirect('users:user_list')





@login_required
def user_list(request):
    """
    View for HOD to see lists of students and faculty.
    """
    if request.user.role != 'HOD':
        messages.error(request, 'Unauthorized access.')
        return redirect('users:access_denied')
    
    faculty_list = CustomUser.objects.filter(role='FACULTY').order_by('username')
    student_list = CustomUser.objects.filter(role='STUDENT').order_by('username')
    
    context = {
        'faculty_list': faculty_list,
        'student_list': student_list,
    }
    
    return render(request, 'users/user_list.html', context)

@login_required
def profile(request):
    """Display user profile"""
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    """Allow users to edit their profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully! 🎉')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def change_password(request):
    """Allow users to change their password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Password changed successfully! 🔒')
            return redirect('users:profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'users/change_password.html', {'form': form})

@login_required
def delete_profile_picture(request):
    """Allow users to delete their profile picture"""
    if request.method == 'POST':
        if request.user.profile_picture:
            request.user.profile_picture.delete()
            request.user.save()
            messages.success(request, 'Profile picture removed successfully.')
        return redirect('users:edit_profile')
    return redirect('users:profile')
