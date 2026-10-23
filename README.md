# 🎓 College Lab Booking System

A web-based application for managing college laboratory equipment and booking requests. Students can explore available equipment and submit booking requests, while administrators can review, approve, or reject those requests.

The project is built with Flask and SQLite and uses Docker for containerization and Jenkins for continuous integration and deployment.

## ✨ Features

### 👨‍🎓 Student Features
- User registration and login.
- Secure password hashing.
- View the student dashboard.
- Browse available laboratory equipment.
- Submit equipment booking requests.
- View booking history and booking status.
- Login-protected booking functionality.

### 🛡️ Admin Features
- Dedicated administrator access.
- View booking requests.
- Review student booking details.
- Approve or reject pending bookings.
- Check booking status and availability conflicts.

### ⚙️ Development and DevOps
- Flask-based web application.
- SQLite database for users, equipment, and bookings.
- Docker image creation and containerized deployment.
- Jenkins pipeline for automated testing and deployment.
- Automated application tests using pytest.
- Persistent Docker volume for database storage.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| HTML and CSS | User interface |
| Jinja2 | HTML templating |
| Werkzeug | Password hashing and security utilities |
| pytest | Automated testing |
| Git and GitHub | Version control |
| Docker | Containerization |
| Jenkins | CI/CD automation |

## 🏗️ Project Structure

```text
college-lab-booking/
│
├── app.py
├── database.py
├── college_lab.db
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── Jenkinsfile
├── README.md
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── equipment.html
│   ├── bookings.html
│   └── admin_bookings.html
│
├── static/
│   └── style.css
│
└── tests/
    └── test_app.py
```

*Note: The structure above describes the main project files. Adjust the template and directory names if your current repository differs.*

## 🚀 Getting Started

### Prerequisites

Install the following tools:

- Python 3.11
- Git
- Docker Desktop
- Jenkins (for the CI/CD workflow)

### 1. Clone the Repository

```bash
git clone https://github.com/Vinod1403/college-lab-booking.git
cd college-lab-booking
```

### 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
py -3.11 -m pip install -r requirements.txt
```

### 4. Run the Application

```powershell
py -3.11 app.py
```

Open your browser and visit:

`http://localhost:5000`

Register an account to begin exploring the application.

## 🧪 Running Tests

Execute the automated test suite:

```powershell
py -3.11 -m pytest -v
```

The current test suite contains six tests covering:

- Home page access.
- Equipment page access.
- Dashboard authentication requirements.
- Booking authentication requirements.
- Student registration.
- Student login.

**Latest verified result:** 6 tests passed.

## 🐳 Running with Docker

Build the Docker image:

```powershell
docker build -t college-lab-booking:ci .
```

Run the container:

```powershell
docker run -d --name college-lab-demo -p 5001:5000 college-lab-booking:ci
```

Open:

`http://localhost:5001`

Check the running container:

```powershell
docker ps
```

View application logs:

```powershell
docker logs --tail 50 college-lab-demo
```

### Persistent Database Storage

The application supports configuring its database location using the `DATABASE_PATH` environment variable.

Create a persistent Docker volume:

```powershell
docker volume create college-lab-data
```

Run the application with the volume mounted:

```powershell
docker run -d --name college-lab-demo -p 5001:5000 -v college-lab-data:/data -e DATABASE_PATH=/data/college_lab.db college-lab-booking:ci
```

The database path inside the container is:

`/data/college_lab.db`

The Docker volume keeps the database independent of the container lifecycle. Keep the volume mounted during future deployments to preserve users, equipment, and bookings.

## 🔄 Jenkins CI/CD Pipeline

The project includes a `Jenkinsfile` that defines the automated workflow.

### Pipeline Stages

1. **Checkout:** Retrieves the source code from the configured Git repository.
2. **Install Dependencies and Test:** Installs Python dependencies and runs pytest.
3. **Check Docker Access:** Verifies Docker availability.
4. **Build Docker Image:** Builds the application image.
5. **Prepare Persistent Storage:** Ensures the database volume exists.
6. **Deploy Application:** Replaces the application container and mounts the persistent volume.
7. **Verify Deployment:** Checks the database configuration and application data.

The deployment stage should run only after the preceding tests and image build succeed.

### Run the Pipeline

1. Open your Jenkins dashboard.
2. Select the `College-Lab-Booking-CI` job.
3. Click **Build Now**.
4. Open the latest build's **Console Output**.
5. Verify that the tests, Docker build, deployment, and verification stages succeed.

The Jenkins configuration must use the correct repository, Docker installation, and deployment settings for the machine running Jenkins.

## 🔐 Security Considerations

- Passwords are stored as hashes rather than plaintext.
- Login-protected routes restrict access to authenticated users.
- Administrator permissions should be checked on the server.
- Database files and credentials should not be committed to a public repository.
- Production deployments should use a production-grade WSGI server, secure configuration, and appropriate request protections.

## 🎯 Project Objectives

- Simplify laboratory equipment booking.
- Reduce manual coordination between students and laboratory administrators.
- Centralize booking records and equipment information.
- Prevent conflicting equipment reservations.
- Demonstrate the integration of Flask development with Docker and Jenkins automation.

## 🔮 Future Enhancements

- Email notifications for booking updates.
- Equipment availability calendars.
- Booking analytics and reports.
- Improved role-based access control.
- Deployment health checks and rollback support.
- Cloud deployment and monitoring.

## 👨‍💻 Author

**Vinod**

GitHub: [Vinod1403](https://github.com/Vinod1403)

---

*Developed as a college laboratory booking and DevOps learning project.*
