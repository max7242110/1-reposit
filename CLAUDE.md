# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack air conditioner rating system:
- **Backend**: Django 5.1 + Django REST Framework, PostgreSQL
- **Frontend**: Next.js 16 (App Router, SSR), TypeScript, Tailwind CSS 4

## Commands

### Backend (from `backend/`)
```bash
source venv/bin/activate
python manage.py runserver          # Dev server on :8000
python manage.py migrate
python manage.py import_v2 file.xlsx  # Import AC data from Excel

# Testing
pytest                              # All tests
pytest ratings/tests/               # Single app tests
pytest --cov=ratings --cov-report=html
```

### Frontend (from `frontend/`)
```bash
npm run dev         # Dev server on :3000
npm run build && npm start
npm test
npm run test:coverage
```

### Environment
Backend needs `DJANGO_SETTINGS_MODULE=config.settings.development` and PostgreSQL env vars (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`).
Frontend needs `NEXT_PUBLIC_API_URL=http://localhost:8000/api` in `.env.local`.

## Architecture

### Two-Version API Strategy
- **v1** (`/api/conditioners/`, `/api/v1/`): Legacy endpoints — `ratings` app, models `AirConditioner` + `ParameterValue`
- **v2** (`/api/v2/models/`): Modern endpoints — `catalog` app, models `ACModel` + `ModelRawValue`

Both versions are active; v2 is the primary development target. Frontend has both `/` (v1) and `/v2/` routes.

### Backend Apps
| App | Purpose |
|-----|---------|
| `ratings/` | v1 legacy — simple list/detail for AirConditioner |
| `catalog/` | v2 — ACModel, EquipmentType, ModelRegion; refactored admin, import |
| `methodology/` | Scoring criteria and methodologies (Criterion, Methodology, CriteriaRow) |
| `scoring/` | Engine + pluggable scorers; computes weighted index per methodology |
| `brands/` | Brand management |
| `core/` | TimestampMixin, audit logging, i18n helpers, roles |

### Key Data Flow
1. Excel → `import_v2` management command → `ModelRawValue` (one row per model+criterion)
2. Scoring engine reads raw values + methodology weights → computes index
3. DRF serializers expose rich v2 payload; frontend renders via SSR

### Frontend Structure
- `src/app/` — Next.js App Router pages (`/`, `/conditioner/[id]`, `/v2/`, `/v2/model/[id]`)
- `src/components/` — Reusable UI (RatingTableV2, ParameterBar, IndexCriterionCard, etc.)
- `src/lib/api.ts` — Single API client for both v1 and v2 endpoints
- `src/lib/types.ts` — Shared TypeScript types

### Admin
Django admin is the primary data management interface. Admin code lives in `catalog/admin/` and `methodology/admin/` (split into submodules for organization).

## Key Patterns
- Settings split: `config/settings/base.py`, `development.py`, `production.py`
- `core.models.TimestampMixin` used as base for all models
- Scoring scorers are pluggable classes in `scoring/scorers/`
- Publishing states: draft → review → published → archived (on ACModel)
- Lab status tracking per criterion: `not_measured`, `pending`, `not_in_mode`, `measured`
