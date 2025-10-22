PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS missions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  title       TEXT NOT NULL,
  tags        TEXT,
  status      TEXT NOT NULL DEFAULT 'open',       -- open|scheduled|in-progress|locked|complete|archived
  difficulty  TEXT NOT NULL DEFAULT 'standard',   -- easy|standard|hard|epic
  region_hint TEXT,
  brief       TEXT,                               -- player-facing blurb
  dossier     TEXT,                               -- GM notes
  x           REAL NOT NULL DEFAULT 0.5,          -- normalized 0..1 on global map
  y           REAL NOT NULL DEFAULT 0.5,
  created_at  INTEGER NOT NULL,
  updated_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS regions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  img  TEXT,                                      -- optional region image
  w    INTEGER, h INTEGER,
  x0 REAL, y0 REAL, x1 REAL, y1 REAL              -- bbox on global map (0..1)
);

-- Optional reputation (kept for future use)
CREATE TABLE IF NOT EXISTS rep_global (
  id INTEGER PRIMARY KEY CHECK (id=1),
  score INTEGER NOT NULL DEFAULT 0
);

-- Advent-style global timer
CREATE TABLE IF NOT EXISTS global_timer (
  id INTEGER PRIMARY KEY CHECK (id=1),
  label TEXT NOT NULL DEFAULT 'ADVENT',
  ticks INTEGER NOT NULL DEFAULT 0,
  max_ticks INTEGER NOT NULL DEFAULT 6,
  note TEXT,
  updated_at INTEGER NOT NULL
);
