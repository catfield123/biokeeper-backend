CREATE TABLE research_description (
    id SERIAL PRIMARY KEY,
    research_id INT NOT NULL REFERENCES research(id),
    type VARCHAR(10) NOT NULL,
    polygon_data JSONB,
    text TEXT
);
