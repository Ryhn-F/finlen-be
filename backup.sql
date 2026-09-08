--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

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
-- Name: roleplay_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roleplay_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    scenario character varying(100) NOT NULL,
    critical_thinking integer DEFAULT 0 NOT NULL,
    risk_awareness integer DEFAULT 0 NOT NULL,
    impulse_control integer DEFAULT 0 NOT NULL,
    decision_making integer DEFAULT 0 NOT NULL,
    financial_instinct_score integer DEFAULT 0 NOT NULL,
    xp_earned integer DEFAULT 0 NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    scenario_id uuid,
    CONSTRAINT roleplay_sessions_critical_thinking_check CHECK (((critical_thinking >= 0) AND (critical_thinking <= 100))),
    CONSTRAINT roleplay_sessions_decision_making_check CHECK (((decision_making >= 0) AND (decision_making <= 100))),
    CONSTRAINT roleplay_sessions_financial_instinct_score_check CHECK (((financial_instinct_score >= 0) AND (financial_instinct_score <= 100))),
    CONSTRAINT roleplay_sessions_impulse_control_check CHECK (((impulse_control >= 0) AND (impulse_control <= 100))),
    CONSTRAINT roleplay_sessions_risk_awareness_check CHECK (((risk_awareness >= 0) AND (risk_awareness <= 100)))
);


ALTER TABLE public.roleplay_sessions OWNER TO postgres;

--
-- Name: scenarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scenarios (
    id uuid NOT NULL,
    title character varying(150) NOT NULL,
    slug character varying(100) NOT NULL,
    description text NOT NULL,
    category character varying(50) NOT NULL,
    difficulty character varying(20) NOT NULL,
    npc_role character varying(100) NOT NULL,
    financial_context jsonb NOT NULL,
    objective text NOT NULL,
    initial_state jsonb NOT NULL,
    system_prompt text NOT NULL,
    max_turns integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.scenarios OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash text NOT NULL,
    level integer DEFAULT 1 NOT NULL,
    financial_instinct numeric(5,2) DEFAULT 0 NOT NULL,
    xp integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT users_financial_instinct_check CHECK (((financial_instinct >= (0)::numeric) AND (financial_instinct <= (100)::numeric))),
    CONSTRAINT users_level_check CHECK ((level >= 1)),
    CONSTRAINT users_xp_check CHECK ((xp >= 0))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
7109830f0caf
\.


--
-- Data for Name: roleplay_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roleplay_sessions (id, user_id, scenario, critical_thinking, risk_awareness, impulse_control, decision_making, financial_instinct_score, xp_earned, status, created_at, completed_at, scenario_id) FROM stdin;
5a0cf2ac-1f44-4bf8-bd2e-5ab742927603	52582f9e-9285-4b68-8c4d-1813f094f22b	aggressive-debt-collector	56	58	54	56	56	85	completed	2026-09-06 20:17:38.301056+07	2026-09-06 20:17:40.535342+07	c6a51b6a-767f-4d7f-a0e2-303c74c2d58a
6e76b387-9c4f-439c-9b9f-9fa9ab2eb640	83fc044c-1a98-4e21-a6c4-7efe054a6819	aggressive-debt-collector	56	58	54	56	56	85	completed	2026-09-06 20:17:59.505837+07	2026-09-06 20:18:01.796873+07	c6a51b6a-767f-4d7f-a0e2-303c74c2d58a
c58c42af-ff46-4b5e-ae9a-7b762d5c9400	6318567a-4027-4500-b5c7-e56a6fd2dda2	aggressive-debt-collector	56	58	54	56	56	85	completed	2026-09-06 20:22:15.82997+07	2026-09-06 20:22:17.950123+07	c6a51b6a-767f-4d7f-a0e2-303c74c2d58a
80e56d8d-f836-4d2f-a84d-62d17224e831	8fe63fe8-c433-4ba6-b3bc-c2e145503b3d	aggressive-debt-collector	56	58	54	56	56	85	completed	2026-09-06 20:42:21.198567+07	2026-09-06 20:42:23.372669+07	c6a51b6a-767f-4d7f-a0e2-303c74c2d58a
c6c91661-d121-4e7f-bdd6-f55cf593b026	3ae706c2-6358-401d-b903-b7b0eaa85b63	impulsive-flash-sale-fomo	66	66	60	60	63	240	completed	2026-09-06 23:26:58.18301+07	2026-09-06 23:35:13.432985+07	aa51cbbd-f8a2-40fc-9d85-48d643c21948
c69bf271-6f57-4709-b1fe-be7673d6b832	f51c846f-19fc-41ab-94a4-4f52c1a5463a	aggressive-debt-collector	56	58	54	56	56	85	completed	2026-09-07 00:26:35.053238+07	2026-09-07 00:26:37.155916+07	c6a51b6a-767f-4d7f-a0e2-303c74c2d58a
1479ca84-fdda-416f-ac46-20af9286a4e6	20000b20-a0f0-49b0-b0fc-16a7b47bf730	aggressive-debt-collector	56	58	54	56	56	85	completed	2026-09-07 00:33:17.442802+07	2026-09-07 00:33:19.517312+07	c6a51b6a-767f-4d7f-a0e2-303c74c2d58a
718e7983-cbf5-4e4b-94bb-6a4c43f70e2b	3ae706c2-6358-401d-b903-b7b0eaa85b63	impulsive-flash-sale-fomo	48	48	48	48	48	15	completed	2026-09-06 23:41:56.529914+07	2026-09-07 00:33:37.903567+07	aa51cbbd-f8a2-40fc-9d85-48d643c21948
483dbe32-a144-4d42-b234-cab6c8b4a698	3ae706c2-6358-401d-b903-b7b0eaa85b63	bnpl-snowball-crisis	52	50	48	46	49	35	completed	2026-09-07 00:33:47.589868+07	2026-09-07 00:39:17.378426+07	5bee0d35-0f86-461d-8bd4-d30a502cec1a
69e08c7b-54e6-4190-93db-743f6c9b13ea	df1dd22b-2123-4540-bbbd-f4c707c26e0a	aggressive-debt-collector	56	58	54	56	56	85	completed	2026-09-07 00:51:10.405805+07	2026-09-07 00:51:12.422982+07	c6a51b6a-767f-4d7f-a0e2-303c74c2d58a
34a88bfd-6458-4361-b43f-93ade5edfa75	78ec7dad-018a-4881-bb14-4005197e5657	aggressive-debt-collector	56	58	54	56	56	85	completed	2026-09-07 00:54:13.040625+07	2026-09-07 00:54:15.38477+07	c6a51b6a-767f-4d7f-a0e2-303c74c2d58a
c186edf3-c464-4b9a-aa6c-43b28be703df	3ae706c2-6358-401d-b903-b7b0eaa85b63	impulsive-flash-sale-fomo	50	50	50	50	50	15	active	2026-09-07 09:09:31.207622+07	\N	aa51cbbd-f8a2-40fc-9d85-48d643c21948
\.


--
-- Data for Name: scenarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scenarios (id, title, slug, description, category, difficulty, npc_role, financial_context, objective, initial_state, system_prompt, max_turns, is_active, created_at, updated_at) FROM stdin;
c6a51b6a-767f-4d7f-a0e2-303c74c2d58a	Aggressive Debt Collector	aggressive-debt-collector	You are currently facing financial difficulties after recently losing your job. You have an outstanding loan of Rp3,000,000 that has been overdue for two months. The loan carries a 5% interest rate with a repayment period of 12 months. An aggressive debt collector contacts you and pressures you to make an immediate payment. Throughout the conversation, you must evaluate the collector's claims, avoid impulsive decisions, identify financial risks, and negotiate a reasonable solution.	debt	medium	Aggressive Debt Collector	{"currency": "IDR", "loan_amount": 3000000, "interest_rate": 5, "interest_type": "monthly", "overdue_months": 2, "user_condition": "recently_laid_off", "current_savings": 500000, "repayment_period_months": 12, "monthly_essential_expenses": 1200000}	Recognize financial risk, avoid impulsive financial decisions, verify claims, negotiate responsibly, and evaluate repayment options.	{"trust_level": 1, "current_stage": "opening", "financial_risk": 6, "negotiation_power": 4, "collector_pressure": 7}	You are roleplaying as 'Budi', an aggressive and persistent debt collector from a financial recovery agency. The user owes Rp3,000,000 overdue for 2 months with 5% interest after losing their job. Your persona: demanding, authoritative, creating urgency ('pay today or face field officers/legal consequences'), yet you must abide by reasonable negotiation if the user remains calm, requests official contract verification, and proposes a realistic restructuring plan. Do NOT fabricate numbers outside Rp3,000,000 or 5% interest.	10	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
51fcebea-e0ed-47c4-91de-ac9e08ba09b4	Illegal Pinjol Blackmail Threat	illegal-pinjol-threat	You borrowed Rp1,500,000 from an unregistered peer-to-peer loan app (Pinjol Ilegal). Only Rp1,000,000 was disbursed, but after just 7 days, they are demanding Rp2,800,000 with exorbitant daily late fees. The collector threatens to blast your contact list and broadcast defamatory photos if you do not transfer funds within 1 hour. You must handle panic, stand your ground against illegal threats, refuse blackmail payments, and seek legal/OJK guidance.	debt	hard	Predatory Illegal Online Loan Collector	{"currency": "IDR", "tenor_days": 7, "lender_type": "illegal_pinjol", "loan_amount": 1500000, "user_condition": "stressed_college_student", "amount_demanded": 2800000, "actual_disbursed": 1000000}	Identify predatory and illegal lending practices, refuse panic-driven transfers, protect personal data, and report to authorities (OJK/Polri) rather than taking new loans to cover debt.	{"trust_level": 0, "current_stage": "opening", "financial_risk": 8, "negotiation_power": 3, "collector_pressure": 9}	You are roleplaying as 'Hendra', an intimidating collector for an illegal unregistered loan application. You use psychological intimidation, short deadlines ('within 30 minutes'), and threats of contacting phone contacts. If the user panics or offers to borrow from another pinjol, escalate the trap. If the user remains assertive, mentions OJK/police, demands legal registration, or refuses terror tactics calmly, your psychological leverage weakens.	10	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
5bc55fb7-f1e4-4047-97d7-051097de71d3	Credit Card Minimum Payment Trap	credit-card-minimum-payment-trap	Your credit card has an accumulated balance of Rp15,000,000 with a 2.25% monthly compounding interest rate (over 27% APR). A bank customer service officer calls offering a promotional 'pay only the minimum Rp750,000' and offering additional credit limit extension. You must recognize how compounding interest works, resist the illusion of affordability through minimum payments, and negotiate a fixed installment conversion.	debt	medium	Bank Retention & Telesales Officer	{"currency": "IDR", "total_balance": 15000000, "monthly_income": 6000000, "user_condition": "early_career_professional", "minimum_payment": 750000, "interest_rate_monthly": 2.25}	Understand the math behind compound interest, calculate long-term debt payoff, reject misleading promotional minimum payments, and convert high-interest revolving debt into fixed low-interest installments.	{"trust_level": 3, "current_stage": "opening", "financial_risk": 6, "negotiation_power": 5, "collector_pressure": 4}	You are roleplaying as 'Santi', an amicable yet sales-driven bank officer. You subtly nudge the user into paying only the minimum payment of Rp750,000 while offering a higher limit, downplaying the heavy compound interest accumulating on the remaining Rp14,250,000 balance. Reward the user if they ask about total interest costs and insist on a fixed installment restructuring.	10	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
aa51cbbd-f8a2-40fc-9d85-48d643c21948	Impulsive Midnight Flash Sale FOMO	impulsive-flash-sale-fomo	It is 11:45 PM on 11.11. An e-commerce live stream host is shouting that a Rp8,500,000 flagship smartphone is discounted to Rp5,999,000 for the next 5 minutes only with only 3 units left. You already have a fully functioning phone, and your remaining discretionary budget this month is only Rp1,200,000. The app nudges you to use a 12-month installment. You must exercise impulse control and separate wants from needs.	spending	easy	High-Pressure Live Shopping Host	{"currency": "IDR", "original_price": 8500000, "user_condition": "fomo_tempted_shopper", "discretionary_budget": 1200000, "item_price_discounted": 5999000, "installment_offer_monthly": 620000}	Practice the 48-hour cooling-off rule for non-essential purchases, evaluate opportunity cost, and resist artificial scarcity and countdown timers.	{"trust_level": 4, "current_stage": "opening", "financial_risk": 5, "negotiation_power": 5, "collector_pressure": 6}	You are roleplaying as 'Rico', an energetic live streamer selling electronics with intense FOMO tactics: countdown timers, 'claim voucher now', and 'treat yourself, you work hard!' Test whether the user succumbs to emotional justifications or applies strict budgeting principles.	8	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
a1870ea6-8d42-4def-8a0d-a86e9c7e70fb	Emergency Medical Expense Financing	emergency-medical-financing	Your parent is admitted for urgent gallbladder surgery requiring an immediate deposit of Rp12,000,000. You have Rp4,000,000 in your emergency fund. The hospital billing officer presents options: full private payment, a third-party high-interest medical loan partner, or BPJS Kesehatan verification which requires paperwork coordination. Under emotional distress, you must make a level-headed decision without falling into predatory financing.	emergency	hard	Hospital Billing Administrator	{"currency": "IDR", "bpjs_active": true, "hospital_bill": 12000000, "user_condition": "emotionally_stressed_family_member", "emergency_savings": 4000000, "medical_loan_interest": 18}	Navigate high-stress medical financial decisions, utilize public health insurance (BPJS/private policy) first, negotiate hospital installment programs, and prevent debt spiral during family crises.	{"trust_level": 5, "current_stage": "opening", "financial_risk": 7, "negotiation_power": 4, "collector_pressure": 6}	You are roleplaying as 'Ibu Rina', an administrative hospital billing specialist. You are professional but formal, explaining the urgent Rp12,000,000 deposit requirement. You mention private payment or quick loan partner first, but if the user proactively inquires about BPJS coordination, hospital payment plans, or emergency tier coverage, you guide them through the administrative paperwork.	10	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
2ffd9c98-d81c-454e-acb4-b939d80250e1	High-Yield Guaranteed Investment Scam	high-yield-investment-scam	An acquaintance introduces you to 'Doni', an extravagant trader showing luxury watches and leased sports cars on social media. Doni offers an exclusive opportunity to invest in an automated algorithmic trading bot guaranteeing 25% monthly return risk-free, backed by supposed offshore licenses. He urges you to deposit at least Rp10,000,000 today to lock in your VIP slot. You must detect classic Ponzi scheme red flags, check OJK/Bappebti legality, and protect your capital.	fraud	hard	Charismatic Crypto / Forex 'Wealth Mentor'	{"currency": "IDR", "user_condition": "aspirational_investor", "minimum_deposit": 10000000, "available_savings": 15000000, "regulatory_status": "unlicensed_illegal_scheme", "promised_return_monthly": 25}	Identify classic investment fraud patterns ('guaranteed high returns', 'exclusive VIP slots', vague mechanisms), verify registration on official regulatory registries (OJK Alert Portal / Bappebti), and resist greed triggers.	{"trust_level": 4, "current_stage": "opening", "financial_risk": 9, "negotiation_power": 5, "collector_pressure": 5}	You are roleplaying as 'Doni', a smooth-talking Ponzi scheme promoter. You use social proof, jargon like 'AI arbitrage' and 'institutional liquidity', and mock traditional bank deposits as 'for broke people'. If the user asks for OJK/Bappebti license numbers, prospectus, or withdrawal terms, deflect with vague claims of international compliance. Award high critical thinking if the user demands verifiable licensing and firmly declines.	10	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
5bee0d35-0f86-461d-8bd4-d30a502cec1a	Buy-Now-Pay-Later (BNPL) Snowball	bnpl-snowball-crisis	Over the last 6 months, you split multiple small purchases (coffee, clothes, gadget accessories) using PayLater. Now 5 different installment schedules collide on the 25th, totaling Rp4,200,000 against your net salary of Rp5,000,000. Late fees and platform admin charges are accumulating daily. A polite but firm BNPL representative reaches out. You must stop micro-borrowing leaks, prioritize cash flow for survival essentials, and structure payoff.	spending	medium	E-Commerce PayLater Recovery Agent	{"currency": "IDR", "net_salary": 5000000, "total_bnpl_due": 4200000, "user_condition": "micro_debt_overwhelmed", "essential_living_costs": 2500000, "number_of_transactions": 14}	Recognize the cognitive trap of frictionless micro-loans, prioritize debt avalanche/snowball payoff, and create a bare-bones survival budget while communicating transparently with the creditor.	{"trust_level": 3, "current_stage": "opening", "financial_risk": 7, "negotiation_power": 5, "collector_pressure": 5}	You are roleplaying as 'Dian', an official PayLater customer service debt resolution agent. You are formal, calm, but relentless about repayment deadlines. You notify the user that their SLIK OJK (credit score) will be downgraded if payment isn't completed by Friday. Support restructuring if the user offers partial immediate payment and disables future checkout credit.	10	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
199458ad-bb01-40cd-9317-b810263f4bb2	Salary Advance Payday Loan	salary-advance-payday-trap	With two weeks left before payday and only Rp200,000 in your account, an instant cash app offers a 'Salary Advance' of Rp2,000,000. However, the service deducts an upfront 12% admin fee (Rp240,000) and charges a 1% daily interest rate if not settled on your exact pay date. The app agent pushes you to sign up in 1 click. You must calculate the effective annualized percentage rate (APR) and evaluate alternative frugal options.	debt	easy	Instant Cash Advance Representative	{"currency": "IDR", "upfront_fee": 240000, "effective_apr": 365, "advance_amount": 2000000, "daily_interest": 1.0, "user_condition": "cash_strapped_employee", "days_until_payday": 14}	Expose deceptive 'low flat fee' marketing, calculate true annualized borrowing costs, and explore emergency budgeting adjustments without signing predatory payday contracts.	{"trust_level": 4, "current_stage": "opening", "financial_risk": 6, "negotiation_power": 5, "collector_pressure": 4}	You are roleplaying as 'Kevin', a marketing telemarketer from an instant salary advance platform. You emphasize 'convenience', 'no collateral', and 'treat yourself until payday'. If the user asks about effective APR, penalties, or total repayment sum, be evasive with euphemisms like 'small platform fee'. Evaluate if the user calculates true financing cost and walks away.	8	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
6f60fa6b-bbcc-44d7-a94b-6007665cd570	Friend Guilt-Tripping for an Unsecured Loan	friend-guilt-trip-loan	Your close university friend 'Farhan' calls in tears. He claims he owes Rp5,000,000 to urgent business suppliers and begs you to transfer Rp5,000,000 from your emergency savings, promising to repay 'next week when his client pays'. He has previously borrowed Rp500,000 and took 8 months to return it. He leverages friendship and emotional guilt ('you're my only hope'). You must balance empathy with financial boundaries without destroying your own financial safety or friendships.	social	medium	Close Friend with Financial Troubles	{"currency": "IDR", "friend_history": "unreliable_repayment_record", "user_condition": "emotionally_conflicted_friend", "amount_requested": 5000000, "user_emergency_fund": 7000000}	Set healthy interpersonal financial boundaries, protect emergency savings from third-party risks, and evaluate whether to give a non-repayable gift within budget or require written contractual terms.	{"trust_level": 6, "current_stage": "opening", "financial_risk": 7, "negotiation_power": 5, "collector_pressure": 7}	You are roleplaying as 'Farhan', a close friend experiencing self-inflicted financial troubles. You use emotional leverage, reminding the user of your past friendship favors, promising high returns or quick repayment. If the user says 'no', act hurt and guilt-trip them. If the user offers a small unconditioned gift (e.g. Rp300,000) or refuses firmly with love, acknowledge their mature boundaries.	10	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
6d88720e-d6fb-413a-9fd2-3923f6ae4752	Vehicle Financing Installment Pressure	vehicle-financing-pressure	You visited a motorcycle dealership intending to purchase a practical Rp19,000,000 commuter bike for your new commute. The finance officer 'Bayu' heavily pushes a sport motorcycle priced at Rp38,000,000, offering a 'Zero Down Payment' 5-year lease with Rp1,350,000 monthly installments. In total, you would pay over Rp81,000,000! Your monthly salary is Rp4,500,000. You must calculate total cost of ownership, resist prestige traps, and stay within prudent 20/4/10 vehicle guidelines.	debt	medium	Aggressive Dealership Finance Officer	{"currency": "IDR", "tenor_years": 5, "user_condition": "aspiring_vehicle_buyer", "monthly_installment": 1350000, "total_lease_payment": 81000000, "user_monthly_income": 4500000, "upsold_vehicle_price": 38000000, "intended_vehicle_price": 19000000}	Calculate Total Cost of Ownership (TCO) including interest, depreciation, and insurance; apply the 20/4/10 financial rule (20% down payment, max 4 years, max 10% monthly income), and reject predatory upsells.	{"trust_level": 4, "current_stage": "opening", "financial_risk": 6, "negotiation_power": 5, "collector_pressure": 6}	You are roleplaying as 'Bayu', an aggressive automotive leasing broker. You sell dreams, vanity, and low barrier entry ('DP 0 rupiah!'). You conceal the 5-year total interest and focus solely on the 'affordable monthly installment'. Reward the user if they demand the full amortization schedule, calculate the 81 million total, and refuse the bad deal.	10	t	2026-09-06 20:12:37.95815+07	2026-09-06 20:12:37.95815+07
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, level, financial_instinct, xp, created_at, updated_at) FROM stdin;
ca5992ce-7f2f-4cee-8a85-3965465fc76f	user_7d35c930	user_7d35c930@example.com	$2b$12$NQUw30nYfC5LIW0p6wEqIe3hrBE2rh9xqfMQb6Zko4PPYqv5C2BC.	1	0.00	0	2026-09-06 20:17:15.717273+07	2026-09-06 20:17:15.717273+07
6100501c-1153-4164-8fa9-2a19dcac8e54	user_fce3450a	user_fce3450a@example.com	$2b$12$xJuBnWhvQz0/ncT8zY1W7uLP19XsVVNdys29T1hAfhfw.XCEHRsma	1	0.00	0	2026-09-06 20:17:34.929778+07	2026-09-06 20:17:34.929778+07
2a47cf14-e5d1-42d8-90fb-2886e9d1dba9	roleplayer_f7f9d702	roleplayer_f7f9d702@example.com	$2b$12$gcQMpiT9E3nSjV8od7oCcOQJ5L499VOnlgkQ9GuSpTuxxUsaLLV3a	1	0.00	0	2026-09-06 20:17:37.409046+07	2026-09-06 20:17:37.409046+07
52582f9e-9285-4b68-8c4d-1813f094f22b	roleplayer_bca46c5c	roleplayer_bca46c5c@example.com	$2b$12$TJGZCknFSIQxAG6wa1nEG.Ijp8LdoV1GVvU0aX4ldFuBU028hGQzu	1	56.00	85	2026-09-06 20:17:36.529845+07	2026-09-06 20:17:40.525858+07
0d2d00bc-81e1-4bc5-8536-247c555005d1	user_a1f6ae0d	user_a1f6ae0d@example.com	$2b$12$WfxYW7a41Atk4HRjGR4BuefwGFIp/0.ouCm2Y9qw2k76KA1NSMLD2	1	0.00	0	2026-09-06 20:17:56.020308+07	2026-09-06 20:17:56.020308+07
acbebcc6-2d35-47d8-ba0c-32078cb8e9de	roleplayer_3f480465	roleplayer_3f480465@example.com	$2b$12$JZWAhRAWBjvEkvVJ.asLm.XmCLbu9pMZISwsdsH.DC/y.V0xt5hYC	1	0.00	0	2026-09-06 20:17:58.579455+07	2026-09-06 20:17:58.579455+07
83fc044c-1a98-4e21-a6c4-7efe054a6819	roleplayer_fc41d90a	roleplayer_fc41d90a@example.com	$2b$12$jN0SX/FfSwEnmOEScyB2nePuNbpOydTmSeYT9as7cexcZVawVD/MW	1	56.00	85	2026-09-06 20:17:57.781189+07	2026-09-06 20:18:01.787088+07
2ddc8939-122c-47eb-a72f-c0b34575fea9	user_eb24fe51	user_eb24fe51@example.com	$2b$12$rFwXkiHHTPqHh0qZ78NcjuNyOaq3V3S8zUy2bbrotF2s.4g/UDcTK	1	0.00	0	2026-09-06 20:22:12.167795+07	2026-09-06 20:22:12.167795+07
c3e819bb-8eec-4ca4-adf7-f34c63e63b68	roleplayer_e9f134e3	roleplayer_e9f134e3@example.com	$2b$12$TQXY0U1qHYzk/yhyi5i4uef1PJeKA4m6m9FnlEy7AzCyQLMMyzB7i	1	0.00	0	2026-09-06 20:22:14.875011+07	2026-09-06 20:22:14.875011+07
6318567a-4027-4500-b5c7-e56a6fd2dda2	roleplayer_96971c80	roleplayer_96971c80@example.com	$2b$12$IcwBxQEEKsdRsMtEzN.gXe8yTfLos.uVX883G8xzYwYk8/uXora.2	1	56.00	85	2026-09-06 20:22:14.079776+07	2026-09-06 20:22:17.943054+07
d7908d03-0a93-44d1-8ec3-4d7b6a94b35e	user_8d840d82	user_8d840d82@example.com	$2b$12$I0ai/ayimu7d1v8yEhTn3OVHv.ONZC34V.biTA7541yC2DzNwO.4W	1	0.00	0	2026-09-06 20:42:18.067947+07	2026-09-06 20:42:18.067947+07
0abebb29-056a-4b9e-94be-b676d4017748	roleplayer_5e72c4ea	roleplayer_5e72c4ea@example.com	$2b$12$e.JMvYJZobrrCotrt3FKg.jd5kfLHFLXo6UMy7bP.BqtdELOZQTKS	1	0.00	0	2026-09-06 20:42:20.327128+07	2026-09-06 20:42:20.327128+07
8fe63fe8-c433-4ba6-b3bc-c2e145503b3d	roleplayer_239987cd	roleplayer_239987cd@example.com	$2b$12$Dl85DSHgG/VnJ8Ghpom/NeYtTlABgteTvFh00SSe3kM1TnfhSaDy.	1	56.00	85	2026-09-06 20:42:19.557324+07	2026-09-06 20:42:23.364101+07
13d501d6-5712-4937-ba77-3a0caf987768	user_e33a2e68	user_e33a2e68@example.com	$2b$12$TnUpeZVbvV4RWjUXtnGn3OwnWhLXhUvEYYsFMdtSSQ38TtzQ4v0b.	1	0.00	0	2026-09-07 00:26:31.786588+07	2026-09-07 00:26:31.786588+07
7dfccae3-71f6-4afd-933c-8a684d0b0d08	roleplayer_f08b1613	roleplayer_f08b1613@example.com	$2b$12$HwWED3.exKnxN8k//U1lZuPxBtksAsSbOjeww/NJAODNNd713Kr/O	1	0.00	0	2026-09-07 00:26:34.085769+07	2026-09-07 00:26:34.085769+07
f51c846f-19fc-41ab-94a4-4f52c1a5463a	roleplayer_0ab4f9f6	roleplayer_0ab4f9f6@example.com	$2b$12$yZhh66rGsmCVHcieNihHYuzb1yZgcONQ6Z49VG4QaTl/HaLq5tcKS	1	56.00	85	2026-09-07 00:26:33.314679+07	2026-09-07 00:26:37.140756+07
a43dc7bb-259e-432a-97cc-14e4fe53a92f	user_9d5baa43	user_9d5baa43@example.com	$2b$12$jrLQ3fOo1JUvs/atshcGu.yMz7HbwjUrTNVoHHlVolGdGtAO2x8C6	1	0.00	0	2026-09-07 00:33:14.109759+07	2026-09-07 00:33:14.109759+07
a6b6907f-a491-4e78-a65e-5e6fa768efae	roleplayer_df797639	roleplayer_df797639@example.com	$2b$12$Ktb2sEQ5bsO.xekouOn3LufVUh3AjmG1mhZg7bhc882z8TXCzDZn6	1	0.00	0	2026-09-07 00:33:16.420177+07	2026-09-07 00:33:16.420177+07
20000b20-a0f0-49b0-b0fc-16a7b47bf730	roleplayer_77ce53a5	roleplayer_77ce53a5@example.com	$2b$12$HkNlO4zFWgVd3Mxe9F.1cOpLQB.dw.xcpToXOp/GP6jEeb6gy75Gq	1	56.00	85	2026-09-07 00:33:15.502627+07	2026-09-07 00:33:19.505547+07
3ae706c2-6358-401d-b903-b7b0eaa85b63	rayhan	reyhan.firdaus227@gmail.com	$2b$12$brWYCFYe4cWB6uTNEdkyuOQJ5beRX80K7iX25WKaUTGRmnn3ihmXm	3	53.80	290	2026-09-06 23:23:25.199174+07	2026-09-07 00:39:17.369624+07
47560427-fcdd-4bcd-a1de-25cf56bd6619	user_f2d5c004	user_f2d5c004@example.com	$2b$12$SpeclNhe/JdTT.a6bKNkiuM28wY0y7tySiwtBG918taz59lhnuOP.	1	0.00	0	2026-09-07 00:51:07.056413+07	2026-09-07 00:51:07.056413+07
5d0a370c-ddbc-42cd-9021-72895be1e29b	roleplayer_50d5430e	roleplayer_50d5430e@example.com	$2b$12$j5As.5sMlk.ePsncF7Ky2.3AAc4fTk1BAXvoW5aXN6BCTEpl7m0Gi	1	0.00	0	2026-09-07 00:51:09.399901+07	2026-09-07 00:51:09.399901+07
df1dd22b-2123-4540-bbbd-f4c707c26e0a	roleplayer_96d97ebb	roleplayer_96d97ebb@example.com	$2b$12$ctrBrazE72NrA/jso5OSEewHshRLGcWCWKKSbb.a2JH.HenzQjHfi	1	56.00	85	2026-09-07 00:51:08.623735+07	2026-09-07 00:51:12.415332+07
d6a9b917-5cad-47bc-82d0-14b4d320f175	user_54aab743	user_54aab743@example.com	$2b$12$eX00Mho6LsYvq1qXTHLlOu3J08TPCGn8lHjhnddzZtkdsKJWEzjbK	1	0.00	0	2026-09-07 00:54:09.344222+07	2026-09-07 00:54:09.344222+07
5afdd40b-8b98-4f59-8d33-18ff272d988f	roleplayer_9537c916	roleplayer_9537c916@example.com	$2b$12$uMXQBuDpJQV1Ugt4anfxoeUJKJpS8B.6ujBqxin285s4DncISNBrO	1	0.00	0	2026-09-07 00:54:11.759559+07	2026-09-07 00:54:11.759559+07
78ec7dad-018a-4881-bb14-4005197e5657	roleplayer_2d9dbaea	roleplayer_2d9dbaea@example.com	$2b$12$Xr7lGq.JJ1hMM41daDjm6uXLJrnva0x4yHFJsxAL8sFPyl1IHnN92	1	56.00	85	2026-09-07 00:54:10.833683+07	2026-09-07 00:54:15.373636+07
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: roleplay_sessions roleplay_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roleplay_sessions
    ADD CONSTRAINT roleplay_sessions_pkey PRIMARY KEY (id);


--
-- Name: scenarios scenarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ix_roleplay_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roleplay_sessions_user_id ON public.roleplay_sessions USING btree (user_id);


--
-- Name: ix_scenarios_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scenarios_category ON public.scenarios USING btree (category);


--
-- Name: ix_scenarios_slug; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_scenarios_slug ON public.scenarios USING btree (slug);


--
-- Name: roleplay_sessions roleplay_sessions_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roleplay_sessions
    ADD CONSTRAINT roleplay_sessions_scenario_id_fkey FOREIGN KEY (scenario_id) REFERENCES public.scenarios(id) ON DELETE SET NULL;


--
-- Name: roleplay_sessions roleplay_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roleplay_sessions
    ADD CONSTRAINT roleplay_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

