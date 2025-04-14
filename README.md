# 🏨HostelMate - Hostel Management System

## 🌟Overview
HostelMate is a comprehensive hostel management system developed using Django framework. This project aims to streamline and automate various aspects of hostel management, making it easier for administrators to manage hostel operations and for students to access hostel-related services. (Still planning for adding better features)

## 🤝Contributors
This project is a collaborative effort between:
- Ladani Vidhi
- Harmi Kotak

Developed as part of our Django project coursework, we've worked together to create a robust and user-friendly hostel management solution.

## 🚀Features
- User Authentication and Authorization
- Student Registration and Profile Management
- Room Allocation and Management
- Complaint Management System
- Mess Management
- Admin Dashboard
- Student Dashboard

## ⚙️Technology Stack
- **Backend Framework:** Django
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Template Engine:** Django Templates

## 📁Project Structure
```
HostelMate/
├── Hostel_Management/     # Main project directory
├── hostel/               # Main application directory
├── static/              # Static files (CSS, JS, Images)
├── templates/           # HTML templates
├── scripts/            # Additional scripts
└── manage.py           # Django management script
```

## 🖥️Installation and Setup
1. Clone the repository
```bash
git clone https://github.com/Ladanividhi/HostelMate.git
cd HostelMate
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
```

3. Install dependencies
```bash
pip install django
```

4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Start the development server
```bash
python manage.py runserver
```

## 🔐 Login

- **Admin Login**:  
  The admin can log in using superuser credentials.  
  If you haven’t created one yet, run the following command in your terminal:
  ```bash
  python manage.py createsuperuser
  
- **Hostelite Login**:  
  Hostelites can log in through the **Login Page** using their credentials.
  New users can sign up via the **Signup Page** and create their accounts.

## 🔍 Explore Features

### 👨‍🎓 For Students:
- Submit complaints
- Give feedback (food)
- View room and bed allocation status
- Generate gatepass

### 👩‍💼 For Admins:
- View student profiles
- Assign rooms and beds
- View complaints
- Analyze mess feedback
- Monitor overall hostel operations via the admin dashboard

## 📚Documentation
Detailed documentation is available in the following files:
- `HostelMate_SRS.pdf` - Software Requirements Specification
- `Project Implementation_HostelMateFinal.pdf` - Project Implementation Details

## 😊Contributing
This project was developed as part of our academic coursework. While it's not actively maintained for contributions, feel free to fork the repository and make improvements.

## 📌 Closing Remarks 

This project not only demonstrates our practical understanding of Django and web development but also reflects our goal of solving real-world problems with meaningful digital solutions.

We hope HostelMate continues to evolve with more advanced features in the future, helping create smarter and more connected hostel environments.

Thankyou!
