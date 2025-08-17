from django import forms
from .models import StudyMaterial, News

class MaterialForm(forms.ModelForm):
    # New PDF field (optional)
    file = forms.FileField(
        required=False,
        help_text='Upload a PDF file (max 10 MB).',
        widget=forms.ClearableFileInput(attrs={'accept': 'application/pdf'})
    )

    class Meta:
        model = StudyMaterial
        # Keep existing fields; file_url will be set after upload
        fields = ['title', 'description', 'file_url', 'external_link', 'subject']

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if not f:
            return f
        content_type = getattr(f, 'content_type', '') or ''
        name = (getattr(f, 'name', '') or '').lower()
        if content_type != 'application/pdf' and not name.endswith('.pdf'):
            raise forms.ValidationError('Only PDF files are allowed.')
        if f.size and f.size > 10 * 1024 * 1024:
            raise forms.ValidationError('File too large (max 10 MB).')
        return f

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'is_public']
        fields = ['title', 'content', 'is_public']
