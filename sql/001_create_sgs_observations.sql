CREATE TABLE IF NOT EXISTS raw_bcb.sgs_observations (
    series_id        integer NOT NULL,
    observation_date date    NOT NULL,
    raw_value        text    NOT NULL,

    PRIMARY KEY (series_id, observation_date)
);

