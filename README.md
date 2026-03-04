# UrbanPulse 360

A dual-persona property intelligence REST API designed to serve property investors and relocators with market analytics, rental insights, and location data.

## Overview

UrbanPulse 360 integrates housing market and rental data to provide CRUD operations for property listings alongside analytical endpoints such as median rent calculations, affordability indices, and regional price trends.

### Target Users

- **Property Investors**: Seeking yield calculations, growth forecasts, and investment hotspots
- **Relocators**: Seeking safety scores, affordability metrics, and lifestyle fit assessments

## Tech Stack

| Component        | Technology                                  |
| ---------------- | ------------------------------------------- |
| Runtime          | Python 3.11+                                |
| Framework        | FastAPI                                     |
| Database         | PostgreSQL (Azure Database Flexible Server) |
| ORM              | SQLAlchemy 2.0                              |
| Validation       | Pydantic                                    |
| Containerisation | Docker                                      |
| Hosting          | Azure App Service                           |
| CI/CD            | GitHub Actions                              |

## Project Structure

```
COMP3011/
├── Dockerfile
├── README.md
├── requirements.txt
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
├── app/
│   ├── __init__.py
│   ├── config.py               # API key authentication
│   ├── database.py             # SQLAlchemy engine and session
│   ├── main.py                 # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── market_data.py      # CrimeStat, MarketTrend models
│   │   └── property.py         # Property model
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── investor.py         # Investor analytics endpoints
│   │   ├── living.py           # Relocator/lifestyle endpoints
│   │   └── market.py           # Property CRUD endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── analytics.py        # Analytics response schemas
│   │   └── properties.py       # Property request/response schemas
│   └── services/
│       └── __init__.py
└── tests/
    ├── __init__.py
    └── test_main.py
```

## API Endpoints

### Health Check

| Method | Endpoint | Description                       |
| ------ | -------- | --------------------------------- |
| GET    | `/`      | API health status                 |
| GET    | `/docs`  | Interactive Swagger documentation |

### Properties (CRUD) - Requires API Key

| Method | Endpoint           | Description                                   |
| ------ | ------------------ | --------------------------------------------- |
| POST   | `/properties/`     | Create a new property listing                 |
| GET    | `/properties/`     | List properties with filtering and pagination |
| GET    | `/properties/{id}` | Retrieve a specific property                  |
| PUT    | `/properties/{id}` | Update a property listing                     |
| DELETE | `/properties/{id}` | Delete a property listing                     |

#### Query Parameters for Listing

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20, max: 100)
- `postcode` - Filter by postcode prefix
- `property_type` - Filter by type (house, flat, terraced, etc.)
- `min_price` / `max_price` - Price range filter
- `bedrooms` - Filter by bedroom count
- `status` - Filter by status (for_sale, for_rent, sold, let)

## Authentication

All CRUD endpoints require an API key passed via the `X-API-Key` header.

```bash
curl -X GET "https://your-api-url/properties/" \
  -H "X-API-Key: your-api-key-here"
```

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Docker (optional)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/comp3011.git
   cd comp3011
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/urbanpulse
   API_KEY=your-development-api-key
   ```

5. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Access the API at `http://localhost:8000`

### Running with Docker

```bash
docker build -t urbanpulse .
docker run -p 80:80 --env-file .env urbanpulse
```

## Deployment

The application is deployed to Azure App Service via GitHub Actions. The CI/CD pipeline:

1. Builds a Docker image on push to `main`
2. Pushes the image to Azure Container Registry
3. Updates the App Service container configuration
4. Sets environment variables from GitHub Secrets
5. Restarts the application

### Required GitHub Secrets

| Secret              | Description                           |
| ------------------- | ------------------------------------- |
| `ACR_LOGIN_SERVER`  | Azure Container Registry login server |
| `ACR_USERNAME`      | ACR username                          |
| `ACR_PASSWORD`      | ACR password                          |
| `AZURE_CREDENTIALS` | Azure service principal credentials   |
| `DATABASE_URL`      | PostgreSQL connection string          |
| `API_KEY`           | API authentication key                |

## Database Models

### Property

| Column        | Type    | Description                   |
| ------------- | ------- | ----------------------------- |
| id            | Integer | Primary key                   |
| postcode      | String  | UK postcode                   |
| address       | String  | Full address                  |
| price         | Integer | Price in GBP                  |
| property_type | String  | house, flat, terraced, etc.   |
| bedrooms      | Integer | Number of bedrooms            |
| status        | String  | for_sale, for_rent, sold, let |

### CrimeStat

| Column          | Type    | Description      |
| --------------- | ------- | ---------------- |
| id              | Integer | Primary key      |
| postcode_sector | String  | Postcode sector  |
| month           | String  | Data month       |
| crime_count     | Integer | Number of crimes |
| category        | String  | Crime category   |

### MarketTrend

| Column    | Type    | Description          |
| --------- | ------- | -------------------- |
| id        | Integer | Primary key          |
| region    | String  | Geographic region    |
| quarter   | String  | Data quarter         |
| avg_price | Integer | Average price in GBP |

## Development Roadmap

### Phase 1: Foundation (Complete)

- [x] Project structure and configuration
- [x] API key authentication
- [x] Pydantic schemas for validation
- [x] Property CRUD endpoints
- [x] CI/CD pipeline with GitHub Actions

### Phase 2: Investor Analytics (Planned)

- [ ] Growth forecast endpoint
- [ ] Yield hotspots endpoint
- [ ] Market trends endpoint

### Phase 3: Living/Relocator (Planned)

- [ ] Safety score endpoint
- [ ] Affordability index endpoint
- [ ] Location comparison endpoint

### Phase 4: GenAI Integration (Planned)

- [ ] OpenAI-powered consultant endpoint

## Data Sources

The API is designed to integrate with publicly available datasets:

- [HM Land Registry](https://www.gov.uk/government/organisations/land-registry) - Property sale prices
- [ONS](https://www.ons.gov.uk/) - Regional statistics and income data
- [Police.uk](https://data.police.uk/) - Crime statistics by postcode
- [data.gov.uk](https://www.data.gov.uk/) - UK government open data

## Licence

This project is developed for COMP3011 coursework at the University of Leeds.
