-- Schema for Florida IT Opportunities Workflow

-- 1. Table for general business details from Google Places
CREATE TABLE IF NOT EXISTS businesses (
    id SERIAL PRIMARY KEY,
    place_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    website_url TEXT,
    rating NUMERIC(3, 2),
    user_ratings_total INTEGER,
    search_query VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_businesses_place_id ON businesses(place_id);
CREATE INDEX IF NOT EXISTS idx_businesses_search_query ON businesses(search_query);

-- 2. Table for scraped website content and metadata
CREATE TABLE IF NOT EXISTS website_enrichment (
    business_id INTEGER PRIMARY KEY REFERENCES businesses(id) ON DELETE CASCADE,
    scraped_title TEXT,
    meta_description TEXT,
    scraped_text TEXT,
    http_status INTEGER,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP VIEW IF EXISTS v_lead_scoring;
DROP TABLE IF EXISTS it_opportunities;

-- 3. Table for Gemini IT opportunities classification and sizing
CREATE TABLE IF NOT EXISTS it_opportunities (
    business_id INTEGER PRIMARY KEY REFERENCES businesses(id) ON DELETE CASCADE,
    business_size VARCHAR(50) NOT NULL, -- 'Small', 'Medium', 'Large'
    business_size_reasoning TEXT,
    website_status VARCHAR(50) NOT NULL, -- 'Modern', 'Outdated', 'Broken/Missing'
    it_pain_points TEXT[], -- Array of strings
    pitchable_services TEXT[], -- Array of strings
    opportunity_score INTEGER CHECK (opportunity_score >= 1 AND opportunity_score <= 10),
    lead_tier VARCHAR(50) NOT NULL, -- 'High', 'Medium', 'Low'
    sales_reasoning TEXT,
    category VARCHAR(100),
    online_presence TEXT,
    security_risk_detected BOOLEAN DEFAULT FALSE,
    security_risk_summary TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_it_opportunities_lead_tier ON it_opportunities(lead_tier);
CREATE INDEX IF NOT EXISTS idx_it_opportunities_score ON it_opportunities(opportunity_score);
CREATE INDEX IF NOT EXISTS idx_it_opportunities_size ON it_opportunities(business_size);

-- 4. Unified view for Power BI lead scoring dashboard
CREATE OR REPLACE VIEW v_lead_scoring AS
SELECT
    b.id,
    b.place_id,
    b.name,
    b.phone,
    b.address,
    b.website_url,
    b.rating AS google_rating,
    b.user_ratings_total AS google_reviews_count,
    b.search_query,
    w.scraped_title,
    w.meta_description,
    w.scraped_text,
    w.http_status AS scrape_http_status,
    o.business_size,
    o.business_size_reasoning,
    o.website_status,
    o.it_pain_points,
    o.pitchable_services,
    o.opportunity_score,
    o.lead_tier,
    o.sales_reasoning,
    o.category,
    o.online_presence,
    o.security_risk_detected,
    o.security_risk_summary,
    o.analyzed_at
FROM businesses b
LEFT JOIN website_enrichment w ON b.id = w.business_id
INNER JOIN it_opportunities o ON b.id = o.business_id;
