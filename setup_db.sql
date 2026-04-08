-- ============================================================
-- ReloScope — AlloyDB Schema
-- ============================================================

-- Enable pgvector for embedding-based similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- Table: user_profiles
-- Stores user preferences and priorities for personalized analysis
-- ============================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT UNIQUE NOT NULL,
    priorities JSONB DEFAULT '{}',
    -- Example: {"air_quality": 0.20, "commute": 0.25, "amenities": 0.20, 
    --           "climate": 0.10, "investment": 0.15, "cost": 0.10}
    workplace_address TEXT DEFAULT '',
    preferred_language TEXT DEFAULT 'en',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- Table: city_analyses
-- Stores full city-level analysis results for comparison and history
-- ============================================================
CREATE TABLE IF NOT EXISTS city_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city TEXT NOT NULL,
    state TEXT DEFAULT '',
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    -- Environment data
    avg_temp_celsius DOUBLE PRECISION,
    min_temp_celsius DOUBLE PRECISION,
    max_temp_celsius DOUBLE PRECISION,
    humidity_pct DOUBLE PRECISION,
    precipitation_prob_pct DOUBLE PRECISION,
    air_quality_aqi INTEGER,
    aqi_category TEXT DEFAULT '',
    dominant_pollutant TEXT DEFAULT '',
    pm25_ugm3 DOUBLE PRECISION,
    pm10_ugm3 DOUBLE PRECISION,
    ozone_ugm3 DOUBLE PRECISION,
    solar_potential_kwh DOUBLE PRECISION,
    sunshine_hours_per_year DOUBLE PRECISION,
    elevation_meters DOUBLE PRECISION,
    flood_risk TEXT DEFAULT 'unknown',
    -- Livability data
    amenity_density_score INTEGER DEFAULT 0,
    school_count INTEGER DEFAULT 0,
    hospital_count INTEGER DEFAULT 0,
    park_count INTEGER DEFAULT 0,
    restaurant_count INTEGER DEFAULT 0,
    gym_count INTEGER DEFAULT 0,
    supermarket_count INTEGER DEFAULT 0,
    train_station_count INTEGER DEFAULT 0,
    police_count INTEGER DEFAULT 0,
    -- Commute data
    commute_drive_min DOUBLE PRECISION,
    commute_transit_min DOUBLE PRECISION,
    commute_destination TEXT DEFAULT '',
    -- Investment data
    property_trend TEXT DEFAULT '',
    news_sentiment TEXT DEFAULT '',
    cost_of_living_relative TEXT DEFAULT '',
    -- Scoring
    weighted_score DOUBLE PRECISION,
    scores_json JSONB DEFAULT '{}',
    -- Full raw data for deep retrieval
    raw_data JSONB DEFAULT '{}',
    -- Embedding for semantic search ("find cities like Bangalore")
    embedding VECTOR(768),
    -- Metadata
    analyzed_by TEXT DEFAULT 'reloscope',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_city_analyses_city ON city_analyses (LOWER(city));
CREATE INDEX IF NOT EXISTS idx_city_analyses_created ON city_analyses (created_at DESC);

-- ============================================================
-- Table: neighborhood_analyses
-- Stores neighborhood-level detailed analysis within a city
-- ============================================================
CREATE TABLE IF NOT EXISTS neighborhood_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city TEXT NOT NULL,
    neighborhood TEXT NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    -- Environment
    air_quality_aqi INTEGER,
    aqi_category TEXT DEFAULT '',
    elevation_meters DOUBLE PRECISION,
    flood_risk TEXT DEFAULT 'unknown',
    -- Livability
    amenity_density_score INTEGER DEFAULT 0,
    amenity_counts JSONB DEFAULT '{}',
    -- Example: {"school": 15, "hospital": 6, "park": 3, ...}
    top_schools JSONB DEFAULT '[]',
    -- Example: [{"name": "DPS", "rating": 4.3, "reviews": 500}, ...]
    top_hospitals JSONB DEFAULT '[]',
    -- Commute
    commute_drive_min DOUBLE PRECISION,
    commute_transit_min DOUBLE PRECISION,
    commute_destination TEXT DEFAULT '',
    -- Green space / density
    green_space_score DOUBLE PRECISION,
    building_density TEXT DEFAULT '',
    -- Embedding for "find neighborhoods like Koramangala"
    embedding VECTOR(768),
    raw_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_neighborhood_city ON neighborhood_analyses (LOWER(city));
CREATE INDEX IF NOT EXISTS idx_neighborhood_name ON neighborhood_analyses (LOWER(neighborhood));

-- ============================================================
-- Table: business_analyses
-- Stores business opportunity analysis results
-- ============================================================
CREATE TABLE IF NOT EXISTS business_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city TEXT NOT NULL,
    neighborhood TEXT NOT NULL,
    business_type TEXT NOT NULL,
    competition_count INTEGER DEFAULT 0,
    demand_score DOUBLE PRECISION DEFAULT 0,
    opportunity_score DOUBLE PRECISION DEFAULT 0,
    analysis JSONB DEFAULT '{}',
    -- Example: {"verdict": "HIGH OPPORTUNITY", "reason": "6 cafes serving 12 coworking spaces"}
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- Table: comparison_reports
-- Stores generated comparison reports with document links
-- ============================================================
CREATE TABLE IF NOT EXISTS comparison_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT,
    query TEXT NOT NULL,
    cities_compared TEXT[] DEFAULT '{}',
    winner TEXT DEFAULT '',
    weighted_scores JSONB DEFAULT '{}',
    -- Example: {"Bangalore": 7.2, "Pune": 7.8, "Hyderabad": 8.1}
    recommendation TEXT DEFAULT '',
    spreadsheet_url TEXT DEFAULT '',
    document_url TEXT DEFAULT '',
    calendar_links JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_email ON comparison_reports (user_email);
CREATE INDEX IF NOT EXISTS idx_reports_created ON comparison_reports (created_at DESC);

-- ============================================================
-- Table: monitored_areas
-- Tracks areas registered for ongoing monitoring (LoopAgent)
-- ============================================================
CREATE TABLE IF NOT EXISTS monitored_areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city TEXT NOT NULL,
    neighborhood TEXT NOT NULL,
    user_email TEXT NOT NULL,
    baseline_snapshot JSONB DEFAULT '{}',
    monitoring_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- Table: monitoring_snapshots
-- Monthly snapshots for tracked areas to detect changes
-- ============================================================
CREATE TABLE IF NOT EXISTS monitoring_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    monitored_area_id UUID REFERENCES monitored_areas(id),
    snapshot_data JSONB DEFAULT '{}',
    changes_detected JSONB DEFAULT '{}',
    snapshot_date TIMESTAMP DEFAULT NOW()
);
