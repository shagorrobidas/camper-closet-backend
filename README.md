# Comper Closet App

## Description
Comper Closet App is a comprehensive digital wardrobe and packing management system built with the Django REST Framework. It allows end users to digitize their closet, intelligently categorize their clothing, automatically extract apparel details using AI image scanning, and seamlessly plan packing lists for their upcoming trips—complete with deadline tracking and email notifications.

## Features
- **Digital Closet Management:** Create, categorize, and track clothing items with properties like brand, size, quantity, and multi-color support natively stored.
- **AI-Powered Image Scanning:** Upload photos of your clothes and let the OpenAI integration automatically extract product details, calculate quantities, and determine dominant hex colors.
- **Advanced Categorization:** Flexible system with both built-in system categories (e.g. Tops, Bottoms) and user-defined custom categories.
- **Trip & Packing Organizer:** Plan trips, create packing lists, and keep track of deadlines with automated background validation.
- **Robust Authentication:** Secure access using JWT (JSON Web Tokens) with token blacklisting support.
- **Automated Notifications & Processing:** Background workers powered by Celery & Redis to handle recurring tasks such as daily packing deadline checks and user email notifications.
- **API Pagination & Filtering:** Fully paginated REST endpoints supporting rich query-parameter filtering and sorting.

## Tech Stack
- **Backend Framework:** Django, Django REST Framework (DRF)
- **Database:** PostgreSQL / SQLite
- **Task Queue:** Celery, Redis
- **Authentication:** SimpleJWT (JSON Web Tokens)
- **AI Integration:** OpenAI (`gpt-4o-mini`) model for vision and image analysis
- **Other:** django-celery-beat, python-dotenv

## Installation

### Prerequisites
- Python 3.12+
- Redis Server (for background tasks)
- Git

### Steps
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd comper-closet-app
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add the following keys:
   ```env
   SECRET_KEY=your_django_secret_key
   DJANGO_LOG_LEVEL=INFO
   EMAIL_HOST_USER=your_smtp_email
   EMAIL_HOST_PASSWORD=your_smtp_password
   CELERY_BROKER_URL=redis://127.0.0.1:6379/0
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Apply Database Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser (Optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```

8. **Start Celery Worker & Beat (in separate terminal windows):**
   ```bash
   celery -A core worker -l info
   celery -A core beat -l info
   ```

## Usage
- Access the core API at `http://localhost:8000/api/`
- For scanning items via AI, submit a `POST` request with a `multipart/form-data` image payload to `/api/closet/items/scan/` using a valid Bearer token.
- You can access the Django admin panel and inspect background task schedules at `http://localhost:8000/admin/`.

## API Documentation
Key Application Endpoints:
- `POST /api/users/...` - Authentication, user registration & Token retrieval.
- `GET/POST /api/closet/items/` - List, filter, and create digital closet items.
- `POST /api/closet/items/scan/` - Upload an image to automatically extract item details via the OpenAI Vision API.
- `GET /api/closet/categories/` - Retrieve custom and system-available clothing classifications. 
- `GET/POST /api/packing/...` - Create and track packing milestones and automated tasks.

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License.

## Contact / Author
Developed by **Betopia Limited** - *[roysagor88@gmail.com]*
