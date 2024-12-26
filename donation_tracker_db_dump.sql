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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: donations; Type: TABLE; Schema: public; Owner: postgres
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
    paid_status boolean DEFAULT false
);


ALTER TABLE public.donations OWNER TO postgres;

--
-- Name: donations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.donations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.donations_id_seq OWNER TO postgres;

--
-- Name: donations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.donations_id_seq OWNED BY public.donations.id;


--
-- Name: pledges; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pledges (
    id integer NOT NULL,
    user_id integer,
    pledged_amount numeric,
    pledge_currency character varying,
    created_at timestamp without time zone
);


ALTER TABLE public.pledges OWNER TO postgres;

--
-- Name: pledges_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pledges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pledges_id_seq OWNER TO postgres;

--
-- Name: pledges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pledges_id_seq OWNED BY public.pledges.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
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
    donation_date date DEFAULT now() NOT NULL,
    has_received_onboarding_email boolean,
    has_received_onboarding_sms boolean,
    phone_password_hash character varying(255),
    email_password_hash character varying(255)
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: donations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.donations ALTER COLUMN id SET DEFAULT nextval('public.donations_id_seq'::regclass);


--
-- Name: pledges id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pledges ALTER COLUMN id SET DEFAULT nextval('public.pledges_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
d67aa8cd1c8b
\.


--
-- Data for Name: donations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.donations (id, user_id, amount, currency, donation_date, medal, payment_type, receipt_filename, amount_paid, pledged_amount, "timestamp", paid_status) FROM stdin;
315	367	3000	GBP	2024-12-22	\N	full_payment	tq15.PNG	0	0	2024-12-22 03:06:40.055855	f
316	364	5000	GBP	2024-12-22	\N	part_payment	\N	0	0	2024-12-22 20:13:41.73345	f
\.


--
-- Data for Name: pledges; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pledges (id, user_id, pledged_amount, pledge_currency, created_at) FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (id, name, phone, email, address, country, state, church_branch, birthday, password_hash, is_admin, is_super_admin, is_active, created_at, updated_at, pledged_amount, pledge_currency, paid_status, medal, partner_since, donation_date, has_received_onboarding_email, has_received_onboarding_sms, phone_password_hash, email_password_hash) FROM stdin;
367	Tobi Lawrence	7076942769	tposhvoice@gmail.com		Nigeria	Lagos	Ajah	\N	scrypt:32768:8:1$9S4oBkqQAnHNBE91$7c851671d809c3f3126f96432acc4cbdbdd4d62b929a2e91be779669327378f41d51acda2a6e0c3064618aff38aa543674e38042d4af603aed94707d3d4b729a	f	f	t	2024-12-21 23:23:16.518582	2024-12-22 02:57:59.425628	60000	GBP	f	Diamond Partner	1990	2024-12-22	f	f	\N	\N
342	Victor Maduike	07061997004	maduike.victor@gmail.com	Co-operative Villa, Badore, Ajah	Nigeria	Lagos	Ajah	\N	scrypt:32768:8:1$aytWHHu2vmvJ1x28$b49414bd39fb4e4e29e4bafe5a3630ce6cfb421013139f0e61aa8fe6a829b4d4801216e3a0870a115d0bda8a438ed5835ba038a083f182a03707d3c3df189b89	t	f	t	2024-12-10 14:58:47.184181	2024-12-11 03:05:06.528996	0	USD	f	\N	\N	2024-12-10	f	f	\N	\N
364	Uche Kenneth	8036089063	martin4dtruth2@gmail.com		Nigeria	Lagos	Ajah	\N	scrypt:32768:8:1$oTyUmz38HoXudaB6$239eb5af532f862e85ca0963d2d8e3e2a9438280b9179d03972287045f4bc01e23984642ba5dc3130c8acf04ae5fa6e7b0afdea1955eff7f47bfcc90e8790f41	f	f	t	2024-12-20 15:28:33.775963	2024-12-22 20:07:58.191993	6000	GBP	f	Diamond Partner	2020	2024-12-22	f	f	\N	\N
365	Ken Uche	9045531092	martinagoha7@gmail.com	11 Road	Nigeria	Lagos	Ajah	\N	scrypt:32768:8:1$FFnkhJ1rPlWf7ByA$f161f9eb4a7598a906c7df06bbd4e2b93bbfef6bc3fbca1ee4e213c682511edf16311deb507cb89e1ba4d42403bef117da79517de3d5849043287c2df5209928	f	f	t	2024-12-20 16:04:48.032427	2024-12-24 15:02:53.64831	90000	EUR	f	Diamond Partner	2024	2024-12-24	f	f	\N	\N
350	Martin Uzoma	8036098976	martin4dtruth@gmail.com	12 Kings street	Canada	Toronto	DT 1	\N	scrypt:32768:8:1$Xox4Kaab7H0BhwIB$d11418c1220ad70c4f889b9bc08ceb0a465bc8a0831b59c97bc16dd1bd10f704e0788a8dfb629de45c9195661b4e3c625048f07667d6defbb09d94f4f4733473	f	f	t	2024-12-15 09:39:51.107665	2024-12-24 15:25:05.390552	6000000	NGN	f	Gold Partner	2006	2024-12-24	t	f	\N	\N
366	Omega Ken	7070759841	michealomega@gmail.com	Ajah	Nigeria	Lagos	Ajah	\N	scrypt:32768:8:1$LV8BUVttrdWRVo3m$11318bff46bfd3b6415b0f626c911b75203a79219d195afa79cdcde8f1eef7c953658b1d7b0b30fe3a8b21b01e35f82a1d317cc72696ff579c8c0684c1e0b46a	f	f	t	2024-12-21 08:22:35.163184	2024-12-21 07:28:58.132453	0	NGN	f	Blue Partner	2009	2024-12-21	f	f	\N	\N
363	Patience Udo	8037584519	martin@tqstem.org	\N	\N	\N	\N	\N	scrypt:32768:8:1$46SeHZfAVmnuU8N1$daea84d51f109670da66d492520ae1e990955574029433a011fc9a68a34e1f6b6503f821e97f3c08beac33edf12c4e3cb38a7ea9852174725409434a1b1748a9	f	f	t	2024-12-20 06:52:47.105621	2024-12-20 06:52:47.105621	0	USD	f	\N	\N	2024-12-20	f	f	\N	\N
\.


--
-- Name: donations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.donations_id_seq', 316, true);


--
-- Name: pledges_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pledges_id_seq', 45, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 367, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: donations donations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.donations
    ADD CONSTRAINT donations_pkey PRIMARY KEY (id);


--
-- Name: pledges pledges_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pledges
    ADD CONSTRAINT pledges_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_phone_key UNIQUE (phone);


--
-- Name: user user_phone_key1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_phone_key1 UNIQUE (phone);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: donations donations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.donations
    ADD CONSTRAINT donations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: pledges pledges_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pledges
    ADD CONSTRAINT pledges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

