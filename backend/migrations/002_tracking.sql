-- 002_tracking.sql 签核快照持续跟踪：变更流水（事务内outbox）、跟踪台账、行级贡献
-- ORM启动时create_all自动建表；本文件保留实际DDL备查，无在线版本迁移执行器。

CREATE TABLE public.fact_events (
    id integer NOT NULL,
    fact_id integer NOT NULL,
    op character varying(10) NOT NULL,
    before json,
    after json NOT NULL,
    created character varying(40)
);

CREATE SEQUENCE public.fact_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.fact_events_id_seq OWNED BY public.fact_events.id;

CREATE TABLE public.trackers (
    id integer NOT NULL,
    snapshot_id integer NOT NULL,
    state character varying(20),
    date_from character varying(10),
    date_to character varying(10),
    metric json,
    signed json,
    numerator double precision,
    denominator double precision,
    value double precision,
    groups json,
    applied_event_id integer,
    error text,
    updated character varying(40)
);

CREATE SEQUENCE public.trackers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.trackers_id_seq OWNED BY public.trackers.id;

CREATE TABLE public.tracker_contribs (
    id integer NOT NULL,
    tracker_id integer NOT NULL,
    fact_id integer NOT NULL,
    class_code character varying(50),
    day character varying(10),
    n double precision,
    d double precision
);

CREATE SEQUENCE public.tracker_contribs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.tracker_contribs_id_seq OWNED BY public.tracker_contribs.id;

ALTER TABLE ONLY public.fact_events ALTER COLUMN id SET DEFAULT nextval('public.fact_events_id_seq'::regclass);
ALTER TABLE ONLY public.trackers ALTER COLUMN id SET DEFAULT nextval('public.trackers_id_seq'::regclass);
ALTER TABLE ONLY public.tracker_contribs ALTER COLUMN id SET DEFAULT nextval('public.tracker_contribs_id_seq'::regclass);

ALTER TABLE ONLY public.fact_events
    ADD CONSTRAINT fact_events_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.trackers
    ADD CONSTRAINT trackers_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.trackers
    ADD CONSTRAINT trackers_snapshot_id_key UNIQUE (snapshot_id);

ALTER TABLE ONLY public.tracker_contribs
    ADD CONSTRAINT tracker_contribs_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.tracker_contribs
    ADD CONSTRAINT tracker_contribs_tracker_id_fact_id_key UNIQUE (tracker_id, fact_id);

ALTER TABLE ONLY public.trackers
    ADD CONSTRAINT trackers_snapshot_id_fkey FOREIGN KEY (snapshot_id) REFERENCES public.snapshots(id);

ALTER TABLE ONLY public.tracker_contribs
    ADD CONSTRAINT tracker_contribs_tracker_id_fkey FOREIGN KEY (tracker_id) REFERENCES public.trackers(id);
