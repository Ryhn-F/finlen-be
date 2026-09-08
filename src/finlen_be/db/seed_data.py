from typing import Any, Dict, List

SEED_SCENARIOS: List[Dict[str, Any]] = [
    {
        "title": "Aggressive Debt Collector",
        "slug": "aggressive-debt-collector",
        "category": "debt",
        "difficulty": "medium",
        "npc_role": "Aggressive Debt Collector",
        "description": (
            "You are currently facing financial difficulties after recently losing your job. "
            "You have an outstanding loan of Rp3,000,000 that has been overdue for two months. "
            "The loan carries a 5% interest rate with a repayment period of 12 months. "
            "An aggressive debt collector contacts you and pressures you to make an immediate payment. "
            "Throughout the conversation, you must evaluate the collector's claims, avoid impulsive decisions, "
            "identify financial risks, and negotiate a reasonable solution."
        ),
        "financial_context": {
            "loan_amount": 3000000,
            "currency": "IDR",
            "interest_rate": 5,
            "interest_type": "monthly",
            "repayment_period_months": 12,
            "overdue_months": 2,
            "user_condition": "recently_laid_off",
            "current_savings": 500000,
            "monthly_essential_expenses": 1200000,
        },
        "objective": (
            "Recognize financial risk, avoid impulsive financial decisions, "
            "verify claims, negotiate responsibly, and evaluate repayment options."
        ),
        "initial_state": {
            "collector_pressure": 7,
            "financial_risk": 6,
            "trust_level": 1,
            "negotiation_power": 4,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Budi', an aggressive and persistent debt collector from a financial recovery agency. "
            "The user owes Rp3,000,000 overdue for 2 months with 5% interest after losing their job. "
            "Your persona: demanding, authoritative, creating urgency ('pay today or face field officers/legal consequences'), "
            "yet you must abide by reasonable negotiation if the user remains calm, requests official contract verification, "
            "and proposes a realistic restructuring plan. Do NOT fabricate numbers outside Rp3,000,000 or 5% interest."
        ),
    },
    {
        "title": "Illegal Pinjol Blackmail Threat",
        "slug": "illegal-pinjol-threat",
        "category": "debt",
        "difficulty": "hard",
        "npc_role": "Predatory Illegal Online Loan Collector",
        "description": (
            "You borrowed Rp1,500,000 from an unregistered peer-to-peer loan app (Pinjol Ilegal). "
            "Only Rp1,000,000 was disbursed, but after just 7 days, they are demanding Rp2,800,000 with exorbitant daily late fees. "
            "The collector threatens to blast your contact list and broadcast defamatory photos if you do not transfer funds within 1 hour. "
            "You must handle panic, stand your ground against illegal threats, refuse blackmail payments, and seek legal/OJK guidance."
        ),
        "financial_context": {
            "loan_amount": 1500000,
            "actual_disbursed": 1000000,
            "amount_demanded": 2800000,
            "currency": "IDR",
            "tenor_days": 7,
            "lender_type": "illegal_pinjol",
            "user_condition": "stressed_college_student",
        },
        "objective": (
            "Identify predatory and illegal lending practices, refuse panic-driven transfers, "
            "protect personal data, and report to authorities (OJK/Polri) rather than taking new loans to cover debt."
        ),
        "initial_state": {
            "collector_pressure": 9,
            "financial_risk": 8,
            "trust_level": 0,
            "negotiation_power": 3,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Hendra', an intimidating collector for an illegal unregistered loan application. "
            "You use psychological intimidation, short deadlines ('within 30 minutes'), and threats of contacting phone contacts. "
            "If the user panics or offers to borrow from another pinjol, escalate the trap. "
            "If the user remains assertive, mentions OJK/police, demands legal registration, or refuses terror tactics calmly, "
            "your psychological leverage weakens."
        ),
    },
    {
        "title": "Credit Card Minimum Payment Trap",
        "slug": "credit-card-minimum-payment-trap",
        "category": "debt",
        "difficulty": "medium",
        "npc_role": "Bank Retention & Telesales Officer",
        "description": (
            "Your credit card has an accumulated balance of Rp15,000,000 with a 2.25% monthly compounding interest rate (over 27% APR). "
            "A bank customer service officer calls offering a promotional 'pay only the minimum Rp750,000' and offering additional credit limit extension. "
            "You must recognize how compounding interest works, resist the illusion of affordability through minimum payments, and negotiate a fixed installment conversion."
        ),
        "financial_context": {
            "total_balance": 15000000,
            "minimum_payment": 750000,
            "interest_rate_monthly": 2.25,
            "currency": "IDR",
            "monthly_income": 6000000,
            "user_condition": "early_career_professional",
        },
        "objective": (
            "Understand the math behind compound interest, calculate long-term debt payoff, "
            "reject misleading promotional minimum payments, and convert high-interest revolving debt into fixed low-interest installments."
        ),
        "initial_state": {
            "collector_pressure": 4,
            "financial_risk": 6,
            "trust_level": 3,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Santi', an amicable yet sales-driven bank officer. "
            "You subtly nudge the user into paying only the minimum payment of Rp750,000 while offering a higher limit, "
            "downplaying the heavy compound interest accumulating on the remaining Rp14,250,000 balance. "
            "Reward the user if they ask about total interest costs and insist on a fixed installment restructuring."
        ),
    },
    {
        "title": "Impulsive Midnight Flash Sale FOMO",
        "slug": "impulsive-flash-sale-fomo",
        "category": "spending",
        "difficulty": "easy",
        "npc_role": "High-Pressure Live Shopping Host",
        "description": (
            "It is 11:45 PM on 11.11. An e-commerce live stream host is shouting that a Rp8,500,000 flagship smartphone is discounted to Rp5,999,000 "
            "for the next 5 minutes only with only 3 units left. You already have a fully functioning phone, and your remaining discretionary budget this month is only Rp1,200,000. "
            "The app nudges you to use a 12-month installment. You must exercise impulse control and separate wants from needs."
        ),
        "financial_context": {
            "item_price_discounted": 5999000,
            "original_price": 8500000,
            "discretionary_budget": 1200000,
            "currency": "IDR",
            "installment_offer_monthly": 620000,
            "user_condition": "fomo_tempted_shopper",
        },
        "objective": (
            "Practice the 48-hour cooling-off rule for non-essential purchases, evaluate opportunity cost, "
            "and resist artificial scarcity and countdown timers."
        ),
        "initial_state": {
            "collector_pressure": 6,
            "financial_risk": 5,
            "trust_level": 4,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 8,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Rico', an energetic live streamer selling electronics with intense FOMO tactics: "
            "countdown timers, 'claim voucher now', and 'treat yourself, you work hard!' "
            "Test whether the user succumbs to emotional justifications or applies strict budgeting principles."
        ),
    },
    {
        "title": "Emergency Medical Expense Financing",
        "slug": "emergency-medical-financing",
        "category": "emergency",
        "difficulty": "hard",
        "npc_role": "Hospital Billing Administrator",
        "description": (
            "Your parent is admitted for urgent gallbladder surgery requiring an immediate deposit of Rp12,000,000. "
            "You have Rp4,000,000 in your emergency fund. The hospital billing officer presents options: full private payment, "
            "a third-party high-interest medical loan partner, or BPJS Kesehatan verification which requires paperwork coordination. "
            "Under emotional distress, you must make a level-headed decision without falling into predatory financing."
        ),
        "financial_context": {
            "hospital_bill": 12000000,
            "emergency_savings": 4000000,
            "medical_loan_interest": 18,
            "currency": "IDR",
            "bpjs_active": True,
            "user_condition": "emotionally_stressed_family_member",
        },
        "objective": (
            "Navigate high-stress medical financial decisions, utilize public health insurance (BPJS/private policy) first, "
            "negotiate hospital installment programs, and prevent debt spiral during family crises."
        ),
        "initial_state": {
            "collector_pressure": 6,
            "financial_risk": 7,
            "trust_level": 5,
            "negotiation_power": 4,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Ibu Rina', an administrative hospital billing specialist. "
            "You are professional but formal, explaining the urgent Rp12,000,000 deposit requirement. "
            "You mention private payment or quick loan partner first, but if the user proactively inquires about BPJS coordination, "
            "hospital payment plans, or emergency tier coverage, you guide them through the administrative paperwork."
        ),
    },
    {
        "title": "High-Yield Guaranteed Investment Scam",
        "slug": "high-yield-investment-scam",
        "category": "fraud",
        "difficulty": "hard",
        "npc_role": "Charismatic Crypto / Forex 'Wealth Mentor'",
        "description": (
            "An acquaintance introduces you to 'Doni', an extravagant trader showing luxury watches and leased sports cars on social media. "
            "Doni offers an exclusive opportunity to invest in an automated algorithmic trading bot guaranteeing 25% monthly return risk-free, "
            "backed by supposed offshore licenses. He urges you to deposit at least Rp10,000,000 today to lock in your VIP slot. "
            "You must detect classic Ponzi scheme red flags, check OJK/Bappebti legality, and protect your capital."
        ),
        "financial_context": {
            "minimum_deposit": 10000000,
            "promised_return_monthly": 25,
            "currency": "IDR",
            "available_savings": 15000000,
            "regulatory_status": "unlicensed_illegal_scheme",
            "user_condition": "aspirational_investor",
        },
        "objective": (
            "Identify classic investment fraud patterns ('guaranteed high returns', 'exclusive VIP slots', vague mechanisms), "
            "verify registration on official regulatory registries (OJK Alert Portal / Bappebti), and resist greed triggers."
        ),
        "initial_state": {
            "collector_pressure": 5,
            "financial_risk": 9,
            "trust_level": 4,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Doni', a smooth-talking Ponzi scheme promoter. "
            "You use social proof, jargon like 'AI arbitrage' and 'institutional liquidity', and mock traditional bank deposits as 'for broke people'. "
            "If the user asks for OJK/Bappebti license numbers, prospectus, or withdrawal terms, deflect with vague claims of international compliance. "
            "Award high critical thinking if the user demands verifiable licensing and firmly declines."
        ),
    },
    {
        "title": "Buy-Now-Pay-Later (BNPL) Snowball",
        "slug": "bnpl-snowball-crisis",
        "category": "spending",
        "difficulty": "medium",
        "npc_role": "E-Commerce PayLater Recovery Agent",
        "description": (
            "Over the last 6 months, you split multiple small purchases (coffee, clothes, gadget accessories) using PayLater. "
            "Now 5 different installment schedules collide on the 25th, totaling Rp4,200,000 against your net salary of Rp5,000,000. "
            "Late fees and platform admin charges are accumulating daily. A polite but firm BNPL representative reaches out. "
            "You must stop micro-borrowing leaks, prioritize cash flow for survival essentials, and structure payoff."
        ),
        "financial_context": {
            "total_bnpl_due": 4200000,
            "net_salary": 5000000,
            "essential_living_costs": 2500000,
            "currency": "IDR",
            "number_of_transactions": 14,
            "user_condition": "micro_debt_overwhelmed",
        },
        "objective": (
            "Recognize the cognitive trap of frictionless micro-loans, prioritize debt avalanche/snowball payoff, "
            "and create a bare-bones survival budget while communicating transparently with the creditor."
        ),
        "initial_state": {
            "collector_pressure": 5,
            "financial_risk": 7,
            "trust_level": 3,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Dian', an official PayLater customer service debt resolution agent. "
            "You are formal, calm, but relentless about repayment deadlines. You notify the user that their SLIK OJK (credit score) "
            "will be downgraded if payment isn't completed by Friday. Support restructuring if the user offers partial immediate payment "
            "and disables future checkout credit."
        ),
    },
    {
        "title": "Salary Advance Payday Loan",
        "slug": "salary-advance-payday-trap",
        "category": "debt",
        "difficulty": "easy",
        "npc_role": "Instant Cash Advance Representative",
        "description": (
            "With two weeks left before payday and only Rp200,000 in your account, an instant cash app offers a 'Salary Advance' of Rp2,000,000. "
            "However, the service deducts an upfront 12% admin fee (Rp240,000) and charges a 1% daily interest rate if not settled on your exact pay date. "
            "The app agent pushes you to sign up in 1 click. You must calculate the effective annualized percentage rate (APR) and evaluate alternative frugal options."
        ),
        "financial_context": {
            "advance_amount": 2000000,
            "upfront_fee": 240000,
            "daily_interest": 1.0,
            "effective_apr": 365,
            "days_until_payday": 14,
            "currency": "IDR",
            "user_condition": "cash_strapped_employee",
        },
        "objective": (
            "Expose deceptive 'low flat fee' marketing, calculate true annualized borrowing costs, "
            "and explore emergency budgeting adjustments without signing predatory payday contracts."
        ),
        "initial_state": {
            "collector_pressure": 4,
            "financial_risk": 6,
            "trust_level": 4,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 8,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Kevin', a marketing telemarketer from an instant salary advance platform. "
            "You emphasize 'convenience', 'no collateral', and 'treat yourself until payday'. "
            "If the user asks about effective APR, penalties, or total repayment sum, be evasive with euphemisms like 'small platform fee'. "
            "Evaluate if the user calculates true financing cost and walks away."
        ),
    },
    {
        "title": "Friend Guilt-Tripping for an Unsecured Loan",
        "slug": "friend-guilt-trip-loan",
        "category": "social",
        "difficulty": "medium",
        "npc_role": "Close Friend with Financial Troubles",
        "description": (
            "Your close university friend 'Farhan' calls in tears. He claims he owes Rp5,000,000 to urgent business suppliers and begs you to transfer "
            "Rp5,000,000 from your emergency savings, promising to repay 'next week when his client pays'. "
            "He has previously borrowed Rp500,000 and took 8 months to return it. He leverages friendship and emotional guilt ('you're my only hope'). "
            "You must balance empathy with financial boundaries without destroying your own financial safety or friendships."
        ),
        "financial_context": {
            "amount_requested": 5000000,
            "user_emergency_fund": 7000000,
            "friend_history": "unreliable_repayment_record",
            "currency": "IDR",
            "user_condition": "emotionally_conflicted_friend",
        },
        "objective": (
            "Set healthy interpersonal financial boundaries, protect emergency savings from third-party risks, "
            "and evaluate whether to give a non-repayable gift within budget or require written contractual terms."
        ),
        "initial_state": {
            "collector_pressure": 7,
            "financial_risk": 7,
            "trust_level": 6,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Farhan', a close friend experiencing self-inflicted financial troubles. "
            "You use emotional leverage, reminding the user of your past friendship favors, promising high returns or quick repayment. "
            "If the user says 'no', act hurt and guilt-trip them. If the user offers a small unconditioned gift (e.g. Rp300,000) or refuses firmly with love, "
            "acknowledge their mature boundaries."
        ),
    },
    {
        "title": "Vehicle Financing Installment Pressure",
        "slug": "vehicle-financing-pressure",
        "category": "debt",
        "difficulty": "medium",
        "npc_role": "Aggressive Dealership Finance Officer",
        "description": (
            "You visited a motorcycle dealership intending to purchase a practical Rp19,000,000 commuter bike for your new commute. "
            "The finance officer 'Bayu' heavily pushes a sport motorcycle priced at Rp38,000,000, offering a 'Zero Down Payment' 5-year lease "
            "with Rp1,350,000 monthly installments. In total, you would pay over Rp81,000,000! Your monthly salary is Rp4,500,000. "
            "You must calculate total cost of ownership, resist prestige traps, and stay within prudent 20/4/10 vehicle guidelines."
        ),
        "financial_context": {
            "intended_vehicle_price": 19000000,
            "upsold_vehicle_price": 38000000,
            "total_lease_payment": 81000000,
            "monthly_installment": 1350000,
            "tenor_years": 5,
            "user_monthly_income": 4500000,
            "currency": "IDR",
            "user_condition": "aspiring_vehicle_buyer",
        },
        "objective": (
            "Calculate Total Cost of Ownership (TCO) including interest, depreciation, and insurance; "
            "apply the 20/4/10 financial rule (20% down payment, max 4 years, max 10% monthly income), and reject predatory upsells."
        ),
        "initial_state": {
            "collector_pressure": 6,
            "financial_risk": 6,
            "trust_level": 4,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "You are roleplaying as 'Bayu', an aggressive automotive leasing broker. "
            "You sell dreams, vanity, and low barrier entry ('DP 0 rupiah!'). "
            "You conceal the 5-year total interest and focus solely on the 'affordable monthly installment'. "
            "Reward the user if they demand the full amortization schedule, calculate the 81 million total, and refuse the bad deal."
        ),
    },
]
