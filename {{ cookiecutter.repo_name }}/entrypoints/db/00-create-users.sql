-- Create users for the application
CREATE USER {{ cookiecutter.repo_name }};
CREATE DATABASE {{ cookiecutter.repo_name }};
\c {{ cookiecutter.repo_name }};
-- Not sure if these grants are necessary as the database is empty
GRANT SELECT ON ALL TABLES IN SCHEMA public TO {{ cookiecutter.repo_name }};
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO {{ cookiecutter.repo_name }};
-- Grant default privileges on both sequences and tables for the app user
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO {{ cookiecutter.repo_name }};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO {{ cookiecutter.repo_name }};
