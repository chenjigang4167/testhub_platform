# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TestHub is an AI-driven test management platform built with Django 4.2 (backend) + Vue 3 (frontend). It provides test case management, API testing, UI automation testing, AI-powered requirement analysis, and test case generation capabilities.

## Common Commands
# Activate the virtual environment(Windows)
E:\python_venv\testhub\Scripts\activate.bat
# Activate the virtual environment(MacOS)
source .venv/bin/activate

### Backend (Django)

```bash
# Start development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run all scheduled tasks (API testing + UI automation)
python manage.py run_all_scheduled_tasks

# Initialize UI automation locator strategies
python manage.py init_locator_strategies

# Download webdrivers for UI automation
python manage.py download_webdrivers
```

### Frontend (Vue 3 + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

## Architecture

### Backend Structure (`apps/`)

The Django project uses a modular app structure under `apps/`:

- **users**: User authentication and profile management (custom User model)
- **projects**: Project and team management
- **testcases**: Manual test case management with steps, attachments, comments
- **testsuites**: Test suite organization
- **executions**: Test plan execution and result tracking
- **reports**: Test report generation
- **reviews**: Test case review workflow with templates and assignments
- **versions**: Version/release management
- **requirement_analysis**: AI-powered requirement document parsing (PDF/Word/TXT) and test case generation
- **assistant**: Dify AI chatbot integration
- **api_testing**: API testing module (HTTP/WebSocket, environments, scheduled tasks, Allure reports)
- **ui_automation**: UI automation with Selenium/Playwright, element management, page objects, AI intelligent mode

### Frontend Structure (`frontend/src/`)

- **views/**: Page components organized by feature module
- **api/**: API service layer
- **stores/**: Pinia state management
- **router/**: Vue Router configuration
- **components/**: Shared components
- **layout/**: Layout components

### Key Configuration Files

- `backend/settings.py`: Django settings (database, REST framework, CORS, Celery, email)
- `frontend/vite.config.js`: Vite build configuration
- `.env`: Environment variables (DB credentials, API keys, email config)

## API Structure

All API endpoints are prefixed with `/api/`:
- `/api/auth/` and `/api/users/`: User authentication
- `/api/projects/`: Project management
- `/api/testcases/`: Test case CRUD
- `/api/testsuites/`: Test suite management
- `/api/executions/`: Test execution
- `/api/reports/`: Report generation
- `/api/reviews/`: Review workflow
- `/api/versions/`: Version management
- `/api/assistant/`: AI assistant chat
- `/api/requirement-analysis/`: AI requirement analysis
- `/api/` (api_testing): API testing endpoints
- `/api/ui-automation/`: UI automation endpoints

API documentation available at `/api/docs/` (Swagger) and `/api/redoc/` (ReDoc).

## Database

MySQL 8.0+ with `utf8mb4` charset. Configuration via environment variables:
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

## AI Integration

The platform supports multiple AI providers configured in `requirement_analysis.AIModelConfig`:
- DeepSeek, Qwen (通义千问), SiliconFlow (硅基流动), OpenAI-compatible APIs
- AI roles: `testcase_writer`, `testcase_reviewer`, `browser_use_text`, `browser_use_vision`

UI automation AI mode uses `browser-use` library with LangChain for intelligent browser automation (`apps/ui_automation/ai_agent.py`).

## Testing Prompt Templates

Custom prompts for AI test case generation are defined in:
- `tester.md`: Test case writer persona and output format
- `tester_pro.md`: Test case reviewer persona

## Key Dependencies

Backend: Django REST Framework, drf-spectacular, django-filter, celery, httpx, selenium, playwright, browser-use, langchain-openai

Frontend: Vue 3, Element Plus, Pinia, Vue Router, Axios, ECharts, Monaco Editor, xlsx

## Commit 规范
- 默认不自动提交代码
- 多个相关修改应合并为一个 commit
- commit message 格式：`<type>: <简短描述>`
- 提交前必须运行 lint 和测试