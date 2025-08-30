# TBL SACCOS Loan Management System

A comprehensive Django-based loan management system for Savings and Credit Cooperative Organizations (SACCOS).

## 🚀 Features

### Core Loan Management
- **Loan Application Processing**: Complete workflow from application to disbursement
- **Multi-Stage Approval System**: Guarantor → HR → Loan Officer → Committee → Accountant
- **Guarantor Management**: Multiple guarantors per loan with approval workflow
- **Repayment Tracking**: Automated repayment schedules and payment history
- **Loan Types**: Configurable loan types with different interest rates and terms

### User Management
- **Role-Based Access Control**: Member, HR Officer, Loan Officer, Committee Member, Accountant, Admin
- **User Profiles**: Complete member information with profile pictures
- **Notifications**: Real-time notifications for loan status updates

### Financial Management
- **Balance Tracking**: Real-time member balance calculations
- **Shares Management**: Buy and track member shares
- **Payment Processing**: Automated payment calculations and tracking
- **Financial Reports**: Comprehensive reporting for administrators

### Dashboard & Analytics
- **Unified Dashboard**: Member information + role-specific tasks
- **Progress Tracking**: Visual workflow progress indicators
- **Real-time Statistics**: Live updates on loan applications and financial data

## 🛠️ Technology Stack

- **Backend**: Django 4.2+ (Python 3.8+)
- **Database**: SQLite (configurable for PostgreSQL/MySQL in production)
- **Frontend**: Bootstrap 5, FontAwesome, Custom CSS
- **Authentication**: Django's built-in authentication system
- **File Handling**: Django's file storage system for documents and images

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Imancharlie/tblsaccos.git
cd tblsaccos
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 🌐 Production Deployment (PythonAnywhere)

### 1. Upload to PythonAnywhere
- Upload your project files to PythonAnywhere
- Or clone from GitHub: `git clone https://github.com/Imancharlie/tblsaccos.git`

### 2. Configure Virtual Environment
```bash
cd tblsaccos
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Settings
- Copy `tblsaccos/production.py` to `tblsaccos/settings.py`
- Update `ALLOWED_HOSTS` with your PythonAnywhere domain
- Set environment variables for `SECRET_KEY`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

### 4. Configure Web App
- Set source code to your project directory
- Set working directory to your project directory
- Set WSGI configuration file to point to your project

### 5. Run Migrations
```bash
python manage.py migrate
python manage.py collectstatic
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in your project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration
The system uses SQLite by default. For production, consider PostgreSQL or MySQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📱 Usage

### For Members
1. **Register/Login**: Create account or login to existing account
2. **Apply for Loans**: Submit loan applications with required documents
3. **Track Progress**: Monitor loan application status through dashboard
4. **Make Payments**: View and make loan repayments
5. **Manage Shares**: Buy and track share investments

### For Staff
1. **HR Officers**: Review loan applications for completeness
2. **Loan Officers**: Evaluate loan applications and approve/reject
3. **Committee Members**: Final approval of loan applications
4. **Accountants**: Process loan disbursements and track payments

### For Administrators
1. **User Management**: Manage all users and their roles
2. **System Configuration**: Configure loan types, interest rates, etc.
3. **Reports**: Generate comprehensive financial and operational reports
4. **System Monitoring**: Monitor system performance and user activities

## 🔒 Security Features

- **Role-Based Access Control**: Users can only access features relevant to their role
- **CSRF Protection**: Built-in CSRF protection for all forms
- **Session Security**: Secure session management with configurable timeouts
- **File Upload Security**: Secure file handling with size and type restrictions
- **Password Validation**: Strong password requirements and validation

## 📊 Database Schema

### Core Models
- **User**: Extended user model with profile information
- **LoanApplication**: Main loan application entity
- **GuarantorApproval**: Guarantor approval records
- **HRReview**: HR review records
- **LoanOfficerReview**: Loan officer review records
- **CommitteeReview**: Committee review records
- **AccountantReview**: Accountant review records
- **RepaymentSchedule**: Loan repayment schedules
- **Payment**: Payment records

### Supporting Models
- **LoanType**: Configurable loan types
- **Notification**: User notification system
- **Share**: Member share investments
- **Announcement**: System announcements

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📝 API Documentation

The system provides RESTful endpoints for:
- Loan applications
- User management
- Financial operations
- Reporting and analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation in the `/docs` folder

## 🔄 Changelog

### Version 1.0.0
- Initial release with core loan management features
- Multi-stage approval workflow
- User role management
- Dashboard and reporting
- File upload and management

## 🎯 Roadmap

- [ ] Mobile application (React Native)
- [ ] Advanced reporting and analytics
- [ ] Integration with banking APIs
- [ ] SMS notifications
- [ ] Multi-currency support
- [ ] Advanced security features

---

**TBL SACCOS** - Empowering SACCOS with modern loan management technology.

