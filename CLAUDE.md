# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **APS (Advanced Planning and Scheduling) Readiness Assessment System** - a Flask web application for evaluating companies' preparedness for implementing APS systems. The application provides a comprehensive evaluation framework with 28 assessment questions across 4 categories.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment (Windows)
aps_venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Primary method - runs with database initialization
python app.py

# Alternative method - simple runner
python run.py
```

### Database Management
```bash
# Check database status and integrity
python check_db.py

# Reset database (interactive script)
python check_db.py  # Choose 'y' when prompted for reset
```

## Architecture

### Core Components

**Flask Application Structure:**
- `app.py` - Main Flask application with all routes, database initialization, and business logic
- `run.py` - Simple application runner (imports from app.py)
- `config.py` - Configuration settings including database path and secret key
- `check_db.py` - Database diagnostic and maintenance utility

**Database Schema:**
- SQLite database (`aps_assessment.db`) with 6 tables:
  - `categories` - Assessment categories with weights (4 categories)
  - `questions` - Assessment questions (28 total)
  - `question_options` - Multiple choice options for each question (5 levels per question)
  - `companies` - Company information
  - `assessments` - Assessment sessions with scores and maturity levels
  - `assessment_results` - Detailed question-by-question results

**Templates Structure:**
- `templates/base.html` - Base template with Bootstrap styling and navigation
- Form templates: `company_form.html`, `assessment_form.html`, `question_new.html`, `question_edit.html`, `category_edit.html`
- Display templates: `index.html`, `companies.html`, `assessments.html`, `questions.html`, `categories.html`, `assessment_detail.html`

### Assessment Framework

**4 Main Categories with Weights:**
1. **Process Evaluation (35%)** - Current planning and execution processes
2. **Data Readiness (35%)** - Master data, forecasts, and operational data quality
3. **System Assessment (15%)** - ERP, MES, and system integration capabilities
4. **Governance (15%)** - Organizational readiness, decision-making, and management support

**Scoring System:**
- Each question scored 1-5 points
- Total possible score: 140 points (28 questions × 5 points)
- Maturity levels calculated as:
  - Level 1: < 40% (< 56 points)
  - Level 2: 40-60% (56-84 points)
  - Level 3: 60-80% (84-112 points)
  - Level 4: 80-91% (112-127 points)
  - Level 5: ≥ 91% (≥ 127 points)

### Key Functions

**Database Initialization:**
- `init_db()` - Creates all tables with proper foreign key relationships
- `insert_initial_data()` - Populates initial categories, questions, and options
- Automatic initialization on `app.py` startup

**Assessment Processing:**
- `calculate_maturity_level(total_score)` - Converts total score to maturity level
- Form processing in `submit_assessment()` route handles scoring and storage
- Chart data API endpoint for visualization

### Application Flow

1. **Company Management** - Register companies with industry/size details
2. **Assessment Execution** - Select company → Complete 28-question evaluation
3. **Results Analysis** - View detailed scores by category, generate charts
4. **Question Management** - Edit assessment questions and options
5. **History Tracking** - View all past assessments with comparison capabilities

## Development Notes

### Database Considerations
- SQLite database auto-creates on first run
- Use `check_db.py` for troubleshooting database issues
- Foreign key relationships enforce data integrity
- Assessment results stored with full question-level detail for analysis

### Template System
- Uses Bootstrap 5 for responsive UI
- Chart.js integration for score visualization
- Korean language interface
- Consistent navigation and flash messaging

### Security Notes
- Secret key configured via environment variable or fallback
- SQL injection protected through parameterized queries
- No authentication system implemented (single-user application)

### Testing and Debugging
- Flask debug mode enabled in both runners
- Comprehensive error handling in database operations
- Database diagnostic tools included for troubleshooting