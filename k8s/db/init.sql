CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(title) > 0),
    completed BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tasks (title, completed)
SELECT seed.title, seed.completed
FROM (VALUES
    ('Explorar la documentación de la API', FALSE),
    ('Consultar tareas desde el frontend', FALSE),
    ('Practicar Docker Compose', FALSE)
) AS seed(title, completed)
WHERE NOT EXISTS (SELECT 1 FROM tasks);
