from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudyMaterial, News
from .forms import MaterialForm, NewsForm
from django.conf import settings
import uuid
import logging

logger = logging.getLogger(__name__)

try:
    from supabase import create_client  # supabase-py v2
except Exception as e:
    create_client = None
    logger.error(f"Supabase import failed: {e}")


# 🔧 Helper to initialize Supabase client
def get_supabase_client():
    if not create_client:
        return None, "Supabase client not available. Install: pip install supabase"

    supabase_url = getattr(settings, 'SUPABASE_URL', '').strip()
    supabase_key = getattr(settings, 'SUPABASE_KEY', '').strip()
    supabase_bucket = getattr(settings, 'SUPABASE_BUCKET', 'study-materials')

    if not supabase_url or 'your-supabase-url' in supabase_url:
        return None, "Invalid Supabase URL configuration."

    if not supabase_key or len(supabase_key) < 50:
        return None, "Invalid Supabase API key configuration. Key appears incomplete."

    try:
        supabase = create_client(supabase_url, supabase_key)
        return (supabase, supabase_bucket), None
    except Exception as e:
        return None, f"Failed to initialize Supabase client: {str(e)}"


@login_required
def material_list(request):
    materials = StudyMaterial.objects.all()
    return render(request, 'materials/material_list.html', {'materials': materials})


@login_required
def material_upload(request):
    if request.user.role == 'STUDENT':
        messages.error(request, 'Only faculty members can upload study materials.')
        return redirect('materials:material_list')

    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user

            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                supabase_client, error = get_supabase_client()
                if not supabase_client:
                    messages.error(request, error)
                    return render(request, 'materials/material_upload.html', {'form': form})

                supabase, supabase_bucket = supabase_client

                try:
                    file_extension = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'pdf'
                    path = f"uploads/{request.user.id}/{uuid.uuid4()}.{file_extension}"

                    uploaded_file.seek(0)
                    file_data = uploaded_file.read()

                    supabase.storage.from_(supabase_bucket).upload(
                        path,
                        file_data,
                        file_options={
                            "content-type": uploaded_file.content_type or "application/pdf",
                            "cache-control": "3600",
                            "upsert": False,
                        },
                    )

                    url_result = supabase.storage.from_(supabase_bucket).get_public_url(path)

                    public_url = None
                    if hasattr(url_result, 'data') and hasattr(url_result.data, 'publicUrl'):
                        public_url = url_result.data.publicUrl
                    elif isinstance(url_result, str):
                        public_url = url_result

                    if public_url:
                        material.file_url = public_url
                        messages.success(request, 'File uploaded successfully to Supabase!')
                    else:
                        messages.warning(request, 'Upload completed but URL generation failed.')

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    if 'row-level security policy' in str(e).lower() or '403' in str(e):
                        messages.error(request,
                            'Upload failed due to storage permissions. '
                            'Please check your Supabase bucket policies.')
                    else:
                        messages.error(request, f'Upload failed: {str(e)}')
                    return render(request, 'materials/material_upload.html', {'form': form})

            material.save()
            messages.success(request, 'Study material saved successfully!')
            return redirect('materials:material_list')
        else:
            messages.error(request, 'Please correct the form errors.')
    else:
        form = MaterialForm()

    return render(request, 'materials/material_upload.html', {'form': form})


@login_required
def news_list(request):
    news = News.objects.all().order_by('-created_at')
    return render(request, 'materials/news_list.html', {'news_list': news})


@login_required
def news_create(request):
    if request.user.role == 'STUDENT':
        return redirect('materials:news_list')

    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.created_by = request.user
            news.save()
            return redirect('materials:news_list')
    else:
        form = NewsForm()
    return render(request, 'materials/news_create.html', {'form': form})


@login_required
def material_edit(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk)
    if request.user != material.uploaded_by:
        messages.error(request, 'You do not have permission to edit this material.')
        return redirect('materials:material_list')

    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            mat = form.save(commit=False)
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                supabase_client, error = get_supabase_client()
                if not supabase_client:
                    messages.error(request, error)
                    return render(request, 'materials/material_edit.html', {'form': form, 'material': material})

                supabase, supabase_bucket = supabase_client

                try:
                    file_extension = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'pdf'
                    path = f"uploads/{request.user.id}/{uuid.uuid4()}.{file_extension}"

                    uploaded_file.seek(0)
                    file_data = uploaded_file.read()

                    supabase.storage.from_(supabase_bucket).upload(
                        path,
                        file_data,
                        file_options={
                            "content-type": uploaded_file.content_type or "application/pdf",
                            "cache-control": "3600",
                            "upsert": False,
                        },
                    )

                    url_result = supabase.storage.from_(supabase_bucket).get_public_url(path)

                    public_url = None
                    if hasattr(url_result, 'data') and hasattr(url_result.data, 'publicUrl'):
                        public_url = url_result.data.publicUrl
                    elif isinstance(url_result, str):
                        public_url = url_result

                    if public_url:
                        mat.file_url = public_url
                        messages.success(request, 'File uploaded successfully to Supabase!')
                    else:
                        messages.warning(request, 'Upload completed but URL generation failed.')

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    if 'row-level security policy' in str(e).lower() or '403' in str(e):
                        messages.error(request,
                            'Upload failed due to storage permissions. '
                            'Please check your Supabase bucket policies.')
                    else:
                        messages.error(request, f'Upload failed: {str(e)}')
                    return render(request, 'materials/material_edit.html', {'form': form, 'material': material})

            mat.save()
            messages.success(request, 'Study material updated successfully!')
            return redirect('materials:material_list')
    else:
        form = MaterialForm(instance=material)

    return render(request, 'materials/material_edit.html', {'form': form, 'material': material})


@login_required
def material_delete(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk)
    if request.user != material.uploaded_by:
        messages.error(request, 'You do not have permission to delete this material.')
        return redirect('materials:material_list')

    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Study material deleted successfully!')
        return redirect('materials:material_list')

    return render(request, 'materials/material_confirm_delete.html', {'material': material})
