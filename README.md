# Smart Attendance System

A modern, automated attendance system that uses facial recognition to track student attendance in real-time. The system provides a web interface for administrators to manage and view attendance records.

## Features

- **Real-time Face Recognition**: Automatically detects and recognizes students using their facial features
- **Web Interface**: User-friendly dashboard for managing attendance
- **Admin Authentication**: Secure login system for viewing attendance records
- **Attendance Tracking**:
  - Automatic marking of present/absent status
  - Late arrival detection (after 30 seconds)
  - Early departure detection
  - Real-time status updates
- **Data Export**: Export attendance records in CSV/Excel format
- **Dark/Light Theme**: Toggle between dark and light modes
- **Responsive Design**: Works on both desktop and mobile devices

## Project Structure

```
smart-attendance-system/
├── app.py                 # Main Flask application
├── main.py               # Face recognition and attendance tracking
├── generate_encodings.py # Generate face encodings from student images
├── requirements.txt      # Project dependencies
├── static/              # Static files
│   ├── css/
│   │   └── theme.css    # Theme styles
│   └── js/
│       └── theme.js     # Theme toggle functionality
├── templates/           # HTML templates
│   ├── index.html      # Main dashboard
│   ├── login.html      # Admin login page
│   ├── view_attendance.html    # Attendance view page
│   └── attendance_details.html # Detailed attendance view
├── Attendance_Excels/   # Generated attendance records
├── Student_face_data/   # Student face images
│   └── [student_name]/  # Individual student folders
└── encodings.pickle     # Generated face encodings
```

## Prerequisites

- Python 3.8 or higher
- Webcam
- Visual Studio Build Tools (for Windows)
- CMake

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/madhurmanoj/Smart-Attendance-System-Using-Face-Recognition
   cd smart-attendance-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Prepare student data:
   - Create a folder named `Student_face_data`
   - Create subfolders for each student with their name
   - Add student photos in their respective folders
   - Run face encoding generation:
     ```bash
     python generate_encodings.py
     ```

5. Start the application:
   ```bash
   python app.py
   ```

## Usage

1. Access the web interface at `http://localhost:5000`
2. Default admin credentials:
   - Username: admin
   - Password: 1234

### Starting Attendance

1. Click "Start Attendance" on the dashboard
2. The system will automatically:
   - Detect faces in real-time
   - Mark students as present if they arrive within 30 seconds
   - Mark students as late if they arrive after 30 seconds
   - Mark students as absent if they don't show up within 10 minutes

### Viewing Attendance

1. Click "View Attendance" on the dashboard
2. Log in with admin credentials
3. Select a date to view attendance records
4. View detailed attendance information including:
   - Student names
   - Arrival times
   - Attendance status
   - Late arrivals

## API Documentation

### Authentication Endpoints

#### POST /login
- **Description**: Admin login
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: Redirects to attendance view on success

#### GET /logout
- **Description**: Admin logout
- **Response**: Redirects to home page

### Attendance Management

#### GET /start_attendance
- **Description**: Start the attendance system
- **Response**:
  ```json
  {
    "status": "success|error",
    "message": "string"
  }
  ```

#### GET /stop_attendance
- **Description**: Stop the attendance system
- **Response**:
  ```json
  {
    "status": "success|error",
    "message": "string"
  }
  ```

#### GET /get_dates
- **Description**: Get list of available attendance dates
- **Response**:
  ```json
  {
    "status": "success|error",
    "dates": ["YYYY-MM-DD"],
    "message": "string"
  }
  ```

#### GET /get_attendance/<date>
- **Description**: Get attendance records for a specific date
- **Parameters**:
  - `date`: Date in YYYY-MM-DD format
- **Response**:
  ```json
  {
    "status": "success",
    "data": [
      {
        "Name": "string",
        "Time": "string",
        "Status": "Present|Absent"
      }
    ],
    "columns": ["string"]
  }
  ```

## Contributing

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write meaningful commit messages
- Add comments for complex logic
- Update documentation for new features
- Test changes thoroughly before submitting

## Security Considerations

- Change default admin credentials in production
- Use HTTPS in production environment
- Implement rate limiting for login attempts
- Store credentials securely (e.g., in environment variables)
- Regular security updates

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Face Recognition Library: [face_recognition](https://github.com/ageitgey/face_recognition)
- Web Framework: [Flask](https://flask.palletsprojects.com/)
- Frontend: [Bootstrap](https://getbootstrap.com/) 