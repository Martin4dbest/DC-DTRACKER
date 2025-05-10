--
-- PostgreSQL database dump
--

-- Dumped from database version 17.0
-- Dumped by pg_dump version 17.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE ONLY public.pledges DROP CONSTRAINT pledges_user_id_fkey;
ALTER TABLE ONLY public.donations DROP CONSTRAINT donations_user_id_fkey;
ALTER TABLE ONLY public."user" DROP CONSTRAINT user_pkey;
ALTER TABLE ONLY public."user" DROP CONSTRAINT user_email_key;
ALTER TABLE ONLY public.donations DROP CONSTRAINT uq_donations_reference;
ALTER TABLE ONLY public.pledges DROP CONSTRAINT pledges_pkey;
ALTER TABLE ONLY public.donations DROP CONSTRAINT donations_pkey;
ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
ALTER TABLE public."user" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.pledges ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.donations ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.user_id_seq;
DROP TABLE public."user";
DROP SEQUENCE public.pledges_id_seq;
DROP TABLE public.pledges;
DROP SEQUENCE public.donations_id_seq;
DROP TABLE public.donations;
DROP TABLE public.alembic_version;
-- *not* dropping schema, since initdb creates it
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: donations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.donations (
    id integer NOT NULL,
    user_id integer NOT NULL,
    amount double precision NOT NULL,
    currency character varying(50),
    donation_date date NOT NULL,
    medal character varying(50),
    payment_type character varying(20) NOT NULL,
    receipt_filename character varying(255),
    amount_paid double precision NOT NULL,
    pledged_amount double precision NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    paid_status boolean,
    reference character varying(100) NOT NULL
);


--
-- Name: donations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.donations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: donations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.donations_id_seq OWNED BY public.donations.id;


--
-- Name: pledges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pledges (
    id integer NOT NULL,
    user_id integer,
    pledged_amount numeric,
    pledge_currency character varying,
    created_at timestamp without time zone
);


--
-- Name: pledges_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pledges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pledges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pledges_id_seq OWNED BY public.pledges.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    name character varying(200),
    phone character varying(50),
    email character varying(255),
    address character varying(500),
    country character varying(150),
    state character varying(150),
    church_branch character varying(150),
    birthday date,
    password_hash character varying(255),
    is_admin boolean,
    is_super_admin boolean,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    pledged_amount double precision,
    pledge_currency character varying(3),
    paid_status boolean,
    medal character varying(100),
    partner_since integer,
    donation_date date NOT NULL,
    has_received_onboarding_email boolean,
    has_received_onboarding_sms boolean
);


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: donations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.donations ALTER COLUMN id SET DEFAULT nextval('public.donations_id_seq'::regclass);


--
-- Name: pledges id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pledges ALTER COLUMN id SET DEFAULT nextval('public.pledges_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
e786ccd9b0d9
\.


--
-- Data for Name: donations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.donations (id, user_id, amount, currency, donation_date, medal, payment_type, receipt_filename, amount_paid, pledged_amount, "timestamp", paid_status, reference) FROM stdin;
345	47	500000	NGN	2025-05-10	\N	part_payment	LOAD_BALANCERS.PNG	0	0	2025-05-10 06:14:49.286846	f	efc25a23-3
\.


--
-- Data for Name: pledges; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pledges (id, user_id, pledged_amount, pledge_currency, created_at) FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."user" (id, name, phone, email, address, country, state, church_branch, birthday, password_hash, is_admin, is_super_admin, is_active, created_at, updated_at, pledged_amount, pledge_currency, paid_status, medal, partner_since, donation_date, has_received_onboarding_email, has_received_onboarding_sms) FROM stdin;
47	Joy Ilechi	9037584516	martin4dtruth@gmail.com		Canada	Kansas	New road	\N	scrypt:32768:8:1$q5SgMQuCuei7wuuq$c35e8217f6f792e58b0aa9cd848ffce1f96add1431db6bceaba84506a010308f481338053995aa1df4964fb4c09f846d4358b51dc6cb4dec0baf80b5ba6282e0	f	f	t	2025-05-10 07:10:27.320924	2025-05-10 06:12:06.380619	800000	CAD	f	\N	2021	2025-05-10	f	f
41	Martin Agoha	08037584519	martin4dtruth2@gmail.com	10 Rockstone estate, Ajah	Nigeria	Lagos	Ajah	\N	scrypt:32768:8:1$TDfL2glXwv2JXO2g$43bb169180b8829576757ed4fa5f3db7110f9f2a0e103fa0f8b71dde49a0f1461ed76747657dd43a706f9934f21d71dc0fab3e4c83b83c387e12cdff335f225f	t	f	t	2025-04-03 22:01:19.869851	2025-04-03 22:01:19.869851	0	USD	f	\N	\N	2025-04-03	f	f
342	Victor Maduike	07061997004	maduike2.victor@gmail.com	Co-operative Villa, Badore, Ajah	Nigeria	Lagos	Ajah	\N	scrypt:32768:8:1$EjJkk3Olvq0GzATl$3f7dc3a745667c0d0404814640dc7575007ac9011c0f131b03801cd64c9e78b4ee8fafddbac1e340947067081f19239955dd20f5d2e7bb686e916e5109797017	t	f	t	2024-12-10 14:58:47.184181	2025-02-17 12:53:10.499782	0	USD	f	\N	1990	2024-12-10	f	f
\.


--
-- Name: donations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.donations_id_seq', 345, true);


--
-- Name: pledges_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pledges_id_seq', 45, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_id_seq', 47, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: donations donations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.donations
    ADD CONSTRAINT donations_pkey PRIMARY KEY (id);


--
-- Name: pledges pledges_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pledges
    ADD CONSTRAINT pledges_pkey PRIMARY KEY (id);


--
-- Name: donations uq_donations_reference; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.donations
    ADD CONSTRAINT uq_donations_reference UNIQUE (reference);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: donations donations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.donations
    ADD CONSTRAINT donations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: pledges pledges_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pledges
    ADD CONSTRAINT pledges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- PostgreSQL database dump complete
--

