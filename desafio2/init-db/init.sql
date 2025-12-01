CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email) VALUES
    ('Alice Silva', 'alice@example.com'),
    ('Bruno Santos', 'bruno@example.com'),
    ('Carla Oliveira', 'carla@example.com'),
    ('Daniel Costa', 'daniel@example.com');

CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO access_logs (action) VALUES ('Database initialized');
