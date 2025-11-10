CREATE TABLE "public"."Channel" ("id" uuid NOT NULL DEFAULT gen_random_uuid(), "handle" text NOT NULL, "name" text, PRIMARY KEY ("id") , UNIQUE ("id"), UNIQUE ("handle"));COMMENT ON TABLE "public"."Channel" IS E'Table containing channel information from YouTube.';
CREATE EXTENSION IF NOT EXISTS pgcrypto;
