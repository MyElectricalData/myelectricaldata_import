CREATE TABLE config
(
    key   TEXT PRIMARY KEY,
    value json NOT NULL
);
CREATE UNIQUE INDEX idx_config_key ON config (key);

CREATE TABLE addresses
(
    pdl   TEXT PRIMARY KEY,
    json  json NOT NULL,
    count INTEGER
);
CREATE UNIQUE INDEX idx_pdl_addresses
    ON addresses (pdl);

CREATE TABLE contracts
(
    pdl   TEXT PRIMARY KEY,
    json  json NOT NULL,
    count INTEGER
);
CREATE UNIQUE INDEX idx_pdl_contracts
    ON contracts (pdl);

CREATE TABLE consumption_daily
(
    pdl   TEXT    NOT NULL,
    date  TEXT    NOT NULL,
    value INTEGER NOT NULL,
    fail  INTEGER
);

CREATE TABLE consumption_detail
(
    pdl          TEXT    NOT NULL,
    date         TEXT    NOT NULL,
    value        INTEGER NOT NULL,
    interval     INTEGER NOT NULL,
    measure_type TEXT    NOT NULL,
    fail         INTEGER
);

CREATE TABLE production_daily
(
    pdl   TEXT    NOT NULL,
    date  TEXT    NOT NULL,
    value INTEGER NOT NULL,
    fail  INTEGER
);
CREATE UNIQUE INDEX idx_date_production
    ON production_daily (date);

CREATE TABLE production_detail
(
    pdl          TEXT    NOT NULL,
    date         TEXT    NOT NULL,
    value        INTEGER NOT NULL,
    interval     INTEGER NOT NULL,
    measure_type TEXT    NOT NULL,
    fail         INTEGER
);
CREATE UNIQUE INDEX idx_date_production_detail
    ON production_detail (date);