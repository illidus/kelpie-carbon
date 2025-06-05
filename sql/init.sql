-- Initialize Kelpie Carbon Database
-- Creates tables for storing AOI geometries and carbon analysis results

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create schema for carbon analysis
CREATE SCHEMA IF NOT EXISTS carbon_analysis;

-- Table for storing Area of Interest geometries
CREATE TABLE IF NOT EXISTS carbon_analysis.aoi_geometries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    geometry GEOMETRY(POLYGON, 4326) NOT NULL,
    area_m2 DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for storing carbon analysis results
CREATE TABLE IF NOT EXISTS carbon_analysis.results (
    id SERIAL PRIMARY KEY,
    aoi_id INTEGER REFERENCES carbon_analysis.aoi_geometries(id),
    analysis_date DATE NOT NULL,
    mean_fai DOUBLE PRECISION,
    mean_ndre DOUBLE PRECISION,
    biomass_density_kg_m2 DOUBLE PRECISION,
    total_biomass_tonnes DOUBLE PRECISION,
    carbon_tonnes DOUBLE PRECISION,
    co2e_tonnes DOUBLE PRECISION,
    car_equivalent INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique analysis per AOI per date
    UNIQUE(aoi_id, analysis_date)
);

-- Table for caching spectral index calculations
CREATE TABLE IF NOT EXISTS carbon_analysis.spectral_cache (
    id SERIAL PRIMARY KEY,
    geometry_hash VARCHAR(64) NOT NULL,
    analysis_date DATE NOT NULL,
    mean_fai DOUBLE PRECISION,
    mean_ndre DOUBLE PRECISION,
    pixel_count INTEGER,
    valid_pixel_percentage DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Cache key
    UNIQUE(geometry_hash, analysis_date)
);

-- Create spatial index on geometries
CREATE INDEX IF NOT EXISTS idx_aoi_geometries_geom 
ON carbon_analysis.aoi_geometries USING GIST (geometry);

-- Create indices for common queries
CREATE INDEX IF NOT EXISTS idx_results_analysis_date 
ON carbon_analysis.results (analysis_date);

CREATE INDEX IF NOT EXISTS idx_results_aoi_date 
ON carbon_analysis.results (aoi_id, analysis_date);

CREATE INDEX IF NOT EXISTS idx_spectral_cache_hash_date 
ON carbon_analysis.spectral_cache (geometry_hash, analysis_date);

-- Insert some example AOI geometries for testing
INSERT INTO carbon_analysis.aoi_geometries (name, description, geometry, area_m2) VALUES 
(
    'Victoria BC Test Area',
    'Test polygon used in mathematical validation',
    ST_GeomFromText('POLYGON((-123.5 48.4, -123.4 48.4, -123.4 48.5, -123.5 48.5, -123.5 48.4))', 4326),
    81738005.53
),
(
    'Strait of Georgia Sample',
    'Larger kelp analysis area in British Columbia',
    ST_GeomFromText('POLYGON((-123.7 48.3, -123.6 48.3, -123.6 48.4, -123.7 48.4, -123.7 48.3))', 4326),
    93570000.0
) ON CONFLICT DO NOTHING;

-- Create a view for easy querying of latest results
CREATE OR REPLACE VIEW carbon_analysis.latest_results AS
SELECT DISTINCT ON (aoi.id) 
    aoi.id as aoi_id,
    aoi.name,
    aoi.description,
    aoi.area_m2,
    r.analysis_date,
    r.total_biomass_tonnes,
    r.co2e_tonnes,
    r.car_equivalent,
    ST_AsGeoJSON(aoi.geometry) as geometry_geojson
FROM carbon_analysis.aoi_geometries aoi
LEFT JOIN carbon_analysis.results r ON aoi.id = r.aoi_id
ORDER BY aoi.id, r.analysis_date DESC;

-- Grant permissions (adjust as needed for your security model)
GRANT USAGE ON SCHEMA carbon_analysis TO kelpie;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA carbon_analysis TO kelpie;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA carbon_analysis TO kelpie; 