# COMP3011

## Project Structure

```
COMP3011/
├── Dockerfile
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── market_data.py
│   │   └── property.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── investor.py
│   │   ├── living.py
│   │   └── market.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   └── propeties.py
│   └── services/
│       ├── __init__.py
│       └── calculations
└── tests/
    ├── __init__.py
    └── test_main.py
```

Phase 1: Foundation (Current Sprint)
Commit 1: Config & Schemas

config.py - API key auth
schemas/properties.py - Property schemas
schemas/analytics.py - Analytics schemas
Commit 2: CRUD Router ← Next

Wire up market.py router in main.py
Test: Create, Read, Update, Delete properties
Phase 2: Investor Analytics
Commit 3: Investor Router

/investor/growth-forecast/{postcode}
/investor/yield-hotspots
/investor/market-trends/{region}
Phase 3: Living/Relocator
Commit 4: Living Router

/living/safety-score/{postcode}
/living/affordability
/living/compare

