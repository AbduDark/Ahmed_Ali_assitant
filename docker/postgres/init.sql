-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for trigram-based text search (useful for Arabic)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
