# Library Management System

## Overview

This is a Flask-based web application for managing a school library system. The application serves Green Valley Educational Institute and provides role-based access for three user types: students, employees, and administrators. The system handles book inventory, user authentication, book borrowing/returning, fine calculations, and administrative operations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask**: Chosen as the main web framework for its simplicity and flexibility in building educational applications
- **Jinja2 templating**: Used for server-side rendering with template inheritance for consistent UI
- **Session-based authentication**: Simple session management for user state across requests

### Database Design
- **SQLite**: Lightweight, file-based database perfect for educational environments with no complex setup requirements
- **Three main tables**:
  - `users`: Stores all user types with flexible schema accommodating different credential requirements
  - `books`: Book inventory with availability tracking
  - `transactions`: Book borrowing history with issue/return dates and status tracking
- **Direct SQL queries**: Raw SQL used instead of ORM for educational transparency and performance

### Authentication System
- **Role-based access control**: Three distinct user types with different authentication methods
  - Students: Authenticate with admission number and password (simplified from previous multi-field approach)
  - Employees: Authenticate with name, department, and subject
  - Admins: Authenticate with phone number and password
- **No password encryption**: Simplified for educational use (should be enhanced for production)
- **Personalized greetings**: Header displays "Hi [Name]" when users are logged in

### Frontend Architecture
- **Bootstrap 5**: Responsive CSS framework for consistent styling across devices
- **Dark theme**: Custom CSS variables for modern, eye-friendly interface
- **Component-based templates**: Base template with role-specific dashboard extensions
- **Font Awesome icons**: Professional iconography throughout the interface

### Business Logic
- **Fine calculation**: Automatic calculation of ₹2/day for books overdue beyond 7 days
- **Book availability tracking**: Real-time status updates for book borrowing
- **Search functionality**: Full-text search across book titles, authors, and categories
- **Dashboard statistics**: Role-appropriate metrics and summaries

### File Structure
- **Modular design**: Separate files for authentication (`auth.py`), database operations (`database.py`), and main application logic
- **Static assets**: CSS and images organized in standard Flask structure
- **Template hierarchy**: Base template with role-specific extensions for maintainability

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.1.3**: CSS framework loaded via CDN for responsive design
- **Font Awesome 6.0.0**: Icon library loaded via CDN for consistent iconography

### Python Packages
- **Flask**: Core web framework
- **SQLite3**: Built-in Python database interface (no external installation required)

### Environment Configuration
- **SESSION_SECRET**: Environment variable for Flask session security (falls back to default for development)

### Static Assets
- **School logo**: Expected at `/static/images/logo.svg` for branding
- **Custom CSS**: Single stylesheet at `/static/css/styles.css` for theming

### Database
- **SQLite file**: `library.db` created automatically in application root directory
- **No external database server required**: Self-contained database solution suitable for educational environments