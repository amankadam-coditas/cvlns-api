# Civic Lens - AI-Powered Civic Grievance Reporting System

## Overview

Civic Lens is an intelligent complaint management platform that empowers citizens to report civic issues using images and optional descriptions. The system leverages AI to validate, categorize, and automatically route complaints to the appropriate government departments.

## Key Features

✅ **Easy Image-Based Reporting** - Citizens can upload photos of civic issues  
✅ **AI-Powered Analysis** - Automatic detection of issue types and damage levels  
✅ **Smart Description Generation** - Auto-generates structured descriptions when missing  
✅ **Consistency Validation** - Ensures image-text alignment before registration  
✅ **Automatic Categorization** - AI classifies complaints into 4 categories  
✅ **Smart Routing** - Routes to correct government departments automatically  
✅ **Image Quality Validation** - Ensures usable images before processing  

## Technical Stack

- **Backend:** FastAPI (Python)
- **Database:** SQLAlchemy ORM + SQLite (MVP) / PostgreSQL (Production)
- **AI/ML:** OpenAI Vision & GPT-4 Turbo
- **File Storage:** Cloudinary
- **API Documentation:** Swagger UI (auto-generated)

## Complaint Categories & Departments

| Category | Department |
|----------|-----------|
| Road | Public Works Department (PWD) |
| Municipal | Municipal Corporation |
| Electricity | Electricity Board |
| Water | Water Supply Department |

## Installation

### Prerequisites
- Python 3.9+
- pip or uv package manager

### Setup Steps

1. **Clone/Navigate to project:**
```bash
cd civic-lens
```

2. **Create virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r pyproject.toml
# or with uv:
uv pip install -e .
```

4. **Setup environment variables:**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials:
CLOUDINARY_API_SECRET=your_secret
CLOUDINARY_API_KEY=your_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
OPENAI_API_KEY=your_openai_key
DATABASE_URL=sqlite:///./civic_lens.db
```

5. **Run the application:**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Submit Complaint
**POST** `/api/complaints/submit`

Submit a civic complaint with image and location data.

**Form Parameters:**
- `file` (required): Image file (jpg, png, etc.)
- `latitude` (required): GPS latitude
- `longitude` (required): GPS longitude
- `description` (optional): User-provided description
- `category` (optional): User-selected category

**Response:**
```json
{
  "complaint_id": "COMPLAINT-ABC123DEF456",
  "status": "Registered",
  "image_url": "https://...",
  "description_generated": "There appears to be a pothole...",
  "category_ai": "Road",
  "ai_confidence": 0.92,
  "consistency_status": "CONSISTENT",
  "consistency_score": 0.95,
  "department": "Public Works Department (PWD)",
  "location": {"latitude": 40.7128, "longitude": -74.0060},
  "timestamp": "2026-03-03T10:30:00"
}
```

### Get Complaint Status
**GET** `/api/complaints/status/{complaint_id}`

Retrieve details of a specific complaint.

**Response:**
```json
{
  "complaint_id": "COMPLAINT-ABC123DEF456",
  "image_url": "https://...",
  "description_user": "There is a big hole on the road",
  "description_generated": "There appears to be a pothole...",
  "category_user": "Road",
  "category_ai": "Road",
  "consistency_score": 0.95,
  "location": {"latitude": 40.7128, "longitude": -74.0060},
  "department": "Public Works Department (PWD)",
  "status": "Registered",
  "timestamp": "2026-03-03T10:30:00",
  "ai_confidence": 0.92
}
```

### List All Complaints
**GET** `/api/complaints/list?skip=0&limit=50`

List all registered complaints with pagination.

### Get Department Complaints
**GET** `/api/complaints/department/{department}?skip=0&limit=50`

Get all complaints assigned to a specific department.

### Update Complaint Status
**PUT** `/api/complaints/status/{complaint_id}?status=Forwarded`

Update complaint status (Registered → Forwarded → Closed).

### List Departments
**GET** `/api/complaints/departments`

Get list of all departments in the system.

### List Categories
**GET** `/api/complaints/categories`

Get list of all complaint categories.

### Validate Image Quality
**POST** `/api/complaints/validate-image`

Pre-validate image quality before submission.

**Form Parameters:**
- `file` (required): Image file

**Response:**
```json
{
  "is_valid": true,
  "message": "Image quality is acceptable",
  "analysis": {
    "detected_objects": ["pothole", "asphalt"],
    "issue_type": "pothole",
    "damage_level": "moderate",
    "confidence": 0.92
  }
}
```

## Complete Workflow

### Step 1: Citizen Captures Issue
- User takes/uploads image of civic issue
- Optionally provides description

### Step 2: Image Upload
```bash
curl -X POST "http://localhost:8000/api/complaints/submit" \
  -F "file=@issue.jpg" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060" \
  -F "description=There is a pothole on Main Street" \
  -F "category=Road"
```

### Step 3: AI Processing
1. **Image Analysis** - Detects objects, issues, damage level
2. **Quality Check** - Validates image clarity and relevance
3. **Description Generation** - Creates formal description if missing
4. **Consistency Validation** - Checks image-text alignment
5. **Auto-Categorization** - Classifies into Road/Municipal/Electricity/Water
6. **Routing** - Maps to appropriate department

### Step 4: Registration
- Unique complaint ID generated (e.g., COMPLAINT-ABC123DEF456)
- Data stored in database
- Status set to "Registered"

### Step 5: Department Handling
- City department views complaints queue
- Updates status to "Forwarded" when action taken
- Marks as "Closed" when resolved

## Data Model

### Complaint Record
```json
{
  "complaint_id": "COMPLAINT-ABC123DEF456",
  "image_url": "https://cloudinary.com/...",
  "description_user": "Optional user description",
  "description_generated": "AI-generated formal description",
  "category_user": "Optional user-selected category",
  "category_ai": "Road",
  "consistency_score": 0.95,
  "consistency_status": "CONSISTENT",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "department": "Public Works Department (PWD)",
  "status": "Registered",
  "timestamp": "2026-03-03T10:30:00",
  "ai_confidence": 0.92,
  "image_analysis_results": {
    "detected_objects": ["pothole", "asphalt"],
    "issue_type": "pothole",
    "damage_level": "moderate",
    "visual_features": {
      "is_clear_image": true,
      "visibility": "good",
      "artifacts": []
    }
  }
}
```

## Edge Cases Handling

| Scenario | Handling |
|----------|----------|
| Blurry Image | Returns 400 error requesting re-upload |
| No Issue Detected | Returns 400 error requesting clearer image |
| Category Ambiguity | AI suggests most likely category with confidence score |
| Location Denied | User can manually enter coordinates |
| Image-Text Mismatch | Marks as "INCONSISTENT" but allows submission with warning |
| High Damage Level | Automatically flagged with severity indicator |

## Performance Metrics

- **Submission Time:** < 60 seconds (MVP target)
- **AI Accuracy:** 80%+ categorization accuracy
- **Department Routing:** 90%+ correct mapping
- **Consistency Detection:** 85%+ accuracy

## API Documentation

Once running, access interactive API docs at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Development

### File Structure
```
civic-lens/
├── main.py              # FastAPI app init
├── pyproject.toml       # Dependencies
├── .env                 # Environment variables
├── README.md            # This file
└── src/
    ├── __init__.py
    ├── config.py        # Settings & config
    ├── models.py        # SQLAlchemy ORM models
    ├── schemas.py       # Pydantic validation schemas
    ├── database.py      # Database session setup
    ├── file_uploader.py # Cloudinary integration
    ├── ai_service.py    # OpenAI integration & AI logic
    ├── complaint_service.py  # Business logic
    └── routers.py       # API endpoints
```

### Adding New Features

1. **New Category:** Update `CategoryEnum` in models.py and schemas.py, add department mapping in `complaint_service.py`
2. **New AI Model:** Extend `AIService` in ai_service.py
3. **New Endpoint:** Add router in routers.py

## Available Deployment Options

- **Local:** SQLite database
- **Docker:** Containerized with PostgreSQL
- **Cloud:** AWS RDS + S3, Google Cloud SQL, Azure Database

## Future Enhancements

- Multi-language support
- Severity detection (Critical/High/Medium/Low)
- Duplicate complaint detection
- Real-time tracking dashboard
- SLA-based auto-escalation
- Government API integration
- Mobile app (React Native/Flutter)
- Complaints analytics dashboard

## License

See LICENSE file in project root.

## Support

For issues or questions, please check the GitHub issues or contact the development team.

---

**Built with ❤️ for civic improvement**
