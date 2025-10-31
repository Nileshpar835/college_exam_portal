# College Exam Portal

A comprehensive web-based examination system built with Django that allows educational institutions to conduct online quizzes and manage academic content efficiently.

Check out the live demo here: [Exam Portal Live](https://examination-bmiit.onrender.com/)
  

## 🚀 Features

### User Management
- **Multi-role Authentication System**
  - Students, Faculty, and HOD (Head of Department) roles
  - Email verification system
  - Profile management with photo upload
  - Password change functionality

### Dashboard System
- **Role-based Dashboards**
  - Student Dashboard: View available quizzes, results, and study materials
  - Faculty Dashboard: Create quizzes, manage materials, view student results
  - HOD Dashboard: Manage faculty, students, and announcements

### Quiz Management
- **Comprehensive Quiz System**
  - Create and edit quizzes with multiple-choice questions
  - Set duration and passing scores
  - Real-time quiz taking interface
  - Automatic scoring and result generation
  - Quiz result viewing and analysis

### Study Materials
- **Content Management**
  - Upload study materials (PDFs, documents)
  - External resource links
  - Subject-wise categorization
  - Faculty can upload, students can download

### Announcements
- **Communication System**
  - Create and manage announcements
  - Role-based announcement viewing
  - Date-stamped notifications

## 🛠️ Technologies Used

### Backend
- **Python 3.x**
- **Django 4.x** - Web framework
- **Django ORM** - Database operations
- **Django Authentication** - User management
- **Django Messages Framework** - Flash messages

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling with custom animations
- **JavaScript (ES6+)** - Interactive functionality
- **Bootstrap 5.1.3** - Responsive CSS framework
- **Font Awesome 6.0.0** - Icons

### Database
- **Supabase** (PostgreSQL/MySQL)

### Email System
- **Django Email Backend** - Email verification
- **HTML Email Templates** - Styled verification emails

### File Handling
- **Django File Upload** - Study material management
- **Media file serving** - File downloads
   
## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone git@github.com:Nileshpar835/college_exam_portal.git
cd college_exam_portal
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Visit `https://examination-bmiit.onrender.com/` to access the application.

## 📦 Dependencies

```txt
Django>=4.0
Pillow>=8.0.0              # Image handling
django-crispy-forms>=1.14  # Form styling
python-decouple>=3.6       # Environment variables
```

## 👥 User Roles & Permissions

### Student
- View available quizzes
- Take quizzes
- View results and scores
- Download study materials
- View announcements

### Faculty
- Create and manage quizzes
- Upload study materials
- View student results
- Create announcements
- Manage quiz questions

### HOD (Head of Department)
- All faculty permissions
- Create faculty accounts
- Manage users (activate/deactivate)
- View system statistics
- System-wide announcements

## 🎯 Key Features Implementation

### Quiz System
- **Dynamic Question Management**: Add/remove questions dynamically
- **Timer Functionality**: JavaScript-based quiz timer
- **Auto-submit**: Automatic submission when time expires
- **Instant Results**: Immediate score calculation

### File Upload System
- **Multiple File Types**: Support for PDFs, documents, images
- **File Validation**: Type and size restrictions
- **Secure Storage**: Organized media file structure

### Email Verification
- **HTML Email Templates**: Professional email design
- **Secure Tokens**: Django's built-in token generation
- **Responsive Design**: Mobile-friendly email templates

### Responsive Design
- **Mobile-First Approach**: Bootstrap responsive grid
- **Modern UI/UX**: Clean, professional interface
- **Interactive Elements**: Hover effects, animations

## 🔧 Configuration

### Email Settings (settings.py)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Media Files
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up static file serving
- [ ] Configure email backend
- [ ] Set up HTTPS
- [ ] Configure ALLOWED_HOSTS

### Environment Variables
Create a `.env` file:
```
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=your-database-url
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## 📱 Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact:Nileshpar835@gmail.com

## 🔮 Future Enhancements

- [ ] Real-time chat system
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Integration with LMS platforms
- [ ] Video conferencing integration
- [ ] Advanced question types (essay, code)
- [ ] Plagiarism detection
- [ ] Grade book management

---
## Made with ❤️ by Nilesh Parmar

