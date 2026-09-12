Database Schema Documentation
Overview
The public schema contains four tables:

users — application user profiles and progression data
scenarios — roleplay scenario definitions
roleplay_sessions — user attempts or sessions for scenarios
alembic_version — database migration version tracking
Current approximate row counts:

users: 14 rows
scenarios: 10 rows
roleplay_sessions: 5 rows
alembic_version: 0 rows
No table or column comments are currently defined.

Entity Relationship Overview
users
│
└──< roleplay_sessions >── scenarios

Relationships:

One users record can have many roleplay_sessions.
One scenarios record can be associated with many roleplay_sessions.
roleplay_sessions.scenario_id is nullable, so a session may exist without a linked scenario.
roleplay_sessions.scenario stores a separate scenario name or description and may duplicate information represented by scenario_id.
public.users
Stores application user accounts and progression metrics.

Columns
id
Type: uuid
Required: Yes
Primary key: Yes
Default: gen_random_uuid()
Description: Unique identifier for the user.
username
Type: varchar
Required: Yes
Unique: Yes
Constraint: users_username_key
Description: User's unique username.
email
Type: varchar
Required: Yes
Unique: Yes
Constraint: users_email_key
Description: User's unique email address.
password_hash
Type: text
Required: Yes
Description: Hashed password associated with the user account.
Security note: This table is exposed to Supabase client roles because RLS is disabled. Password hashes should not be readable by anon or ordinary authenticated users. Prefer Supabase Auth for authentication credentials rather than storing application passwords directly in a client-accessible table.

level
Type: integer
Required: Yes
Default: 1
Constraint: level >= 1
Description: User progression level.
financial_instinct
Type: numeric
Required: Yes
Default: 0
Constraint: financial_instinct >= 0 AND financial_instinct <= 100
Description: Overall financial-instinct score.
xp
Type: integer
Required: Yes
Default: 0
Constraint: xp >= 0
Description: Accumulated experience points.
created_at
Type: timestamptz
Required: Yes
Default: now()
Description: Timestamp when the user was created.
updated_at
Type: timestamptz
Required: Yes
Default: now()
Description: Timestamp when the user was last updated.
Constraints
Primary key: users_pkey on id
Unique constraint: users_username_key on username
Unique constraint: users_email_key on email
Check constraint on level
Check constraint on financial_instinct
Check constraint on xp
public.scenarios
Stores roleplay scenarios used by the application.

Columns
id
Type: uuid
Required: Yes
Primary key: Yes
Description: Unique scenario identifier.
Note: No default value is currently defined.
title
Type: varchar
Required: Yes
Description: Human-readable scenario title.
slug
Type: varchar
Required: Yes
Description: URL-friendly or programmatic scenario identifier.
Recommendation: Consider adding a unique constraint if each scenario slug must be unique.

description
Type: text
Required: Yes
Description: Longer description of the scenario.
category
Type: varchar
Required: Yes
Description: Scenario grouping or category.
difficulty
Type: varchar
Required: Yes
Description: Difficulty classification.
Recommendation: Consider a check constraint or lookup table if only specific difficulty values are valid.

npc_role
Type: varchar
Required: Yes
Description: Role played by the non-player character in the scenario.
financial_context
Type: jsonb
Required: Yes
Description: Structured financial context provided to the scenario.
The expected JSON structure is not documented in the database. Consider adding application-level documentation or a JSON Schema.

objective
Type: text
Required: Yes
Description: Objective the user should accomplish during the scenario.
initial_state
Type: jsonb
Required: Yes
Description: Initial state or configuration for the scenario.
The expected JSON structure is not documented in the database.

system_prompt
Type: text
Required: Yes
Description: Prompt or system instructions used to drive scenario behavior.
Security note: This may contain application logic or AI instructions and should not be publicly readable unless intentionally exposed.

max_turns
Type: integer
Required: Yes
Description: Maximum number of turns allowed in the scenario.
No positivity or upper-bound check constraint is currently defined.

is_active
Type: boolean
Required: Yes
Description: Indicates whether the scenario is currently available.
No default value is currently defined.

created_at
Type: timestamptz
Required: Yes
Default: now()
Description: Timestamp when the scenario was created.
updated_at
Type: timestamptz
Required: Yes
Default: now()
Description: Timestamp when the scenario was last updated.
Recommendation: Ensure application code or a database trigger updates this column automatically.

Constraints
Primary key: scenarios_pkey on id
Referenced by roleplay_sessions.scenario_id
No unique constraint currently exists on slug
No check constraints currently exist on max_turns, difficulty, or is_active
public.roleplay_sessions
Stores individual user roleplay sessions and evaluation results.

Columns
id
Type: uuid
Required: Yes
Primary key: Yes
Default: gen_random_uuid()
Description: Unique identifier for the roleplay session.
user_id
Type: uuid
Required: Yes
Description: User who owns the session.
Foreign key: users.id
Constraint: roleplay_sessions_user_id_fkey
scenario
Type: varchar
Required: Yes
Description: Scenario name or snapshot stored directly on the session.
This may be a denormalized copy of scenario information. Its relationship with scenario_id should be clarified.

critical_thinking
Type: integer
Required: Yes
Default: 0
Constraint: critical_thinking >= 0 AND critical_thinking <= 100
Description: Critical-thinking evaluation score.
risk_awareness
Type: integer
Required: Yes
Default: 0
Constraint: risk_awareness >= 0 AND risk_awareness <= 100
Description: Risk-awareness evaluation score.
impulse_control
Type: integer
Required: Yes
Default: 0
Constraint: impulse_control >= 0 AND impulse_control <= 100
Description: Impulse-control evaluation score.
decision_making
Type: integer
Required: Yes
Default: 0
Constraint: decision_making >= 0 AND decision_making <= 100
Description: Decision-making evaluation score.
financial_instinct_score
Type: integer
Required: Yes
Default: 0
Constraint: financial_instinct_score >= 0 AND financial_instinct_score <= 100
Description: Financial-instinct score calculated for this session.
xp_earned
Type: integer
Required: Yes
Default: 0
Description: Experience points earned from the session.
No nonnegative check constraint is currently defined.

status
Type: varchar
Required: Yes
Default: 'active'
Description: Current session status.
No check constraint currently limits this to known values such as active, completed, or abandoned.

created_at
Type: timestamptz
Required: Yes
Default: now()
Description: Timestamp when the session was created.
completed_at
Type: timestamptz
Required: No
Description: Timestamp when the session was completed.
scenario_id
Type: uuid
Required: No
Description: Scenario associated with the session.
Foreign key: scenarios.id
Constraint: roleplay_sessions_scenario_id_fkey
Constraints
Primary key: roleplay_sessions_pkey on id
Foreign key to users.id
Foreign key to scenarios.id
Score checks enforce values from 0 through 100
No check constraint currently exists for xp_earned
No check constraint currently exists for status
No rule currently ensures completed_at is populated when status is completed
Design observations
scenario and scenario_id appear to represent overlapping concepts.
If scenario_id is authoritative, consider removing scenario or renaming it to something explicit such as scenario_snapshot.
If historical scenario data must remain unchanged after a scenario is edited, retaining a snapshot column may be appropriate.
Consider adding an index on user_id, scenario_id, and possibly created_at for common session-history queries.
public.learning_materials
Stores supplementary PDF learning materials (a "formal" and a "brainrot" version) associated with a scenario. The actual PDF files are stored in Supabase Storage; only the storage file paths are persisted here. Public URLs are resolved at request time by the API using the Supabase client.

Columns
id
Type: uuid
Required: Yes
Primary key: Yes
Default: gen_random_uuid()
Description: Unique identifier for the learning material.
scenario_id
Type: uuid
Required: Yes
Description: Scenario this material belongs to.
Foreign key: scenarios.id
On delete: CASCADE
title
Type: varchar(255)
Required: Yes
Description: Display title of the material.
description
Type: text
Required: No
Description: Optional summary of the material.
formal_file_path
Type: text
Required: Yes
Description: Supabase Storage object path for the formal-version PDF (not a public URL).
brainrot_file_path
Type: text
Required: Yes
Description: Supabase Storage object path for the brainrot-version PDF (not a public URL).
source_name
Type: varchar(255)
Required: No
Description: Attribution for the original source of the material.
source_url
Type: text
Required: No
Description: Link to the original source.
created_at
Type: timestamptz
Required: Yes
Default: now()
updated_at
Type: timestamptz
Required: Yes
Default: now()

Constraints
Primary key: learning_materials_pkey on id
Foreign key to scenarios.id, ON DELETE CASCADE
Index on scenario_id

public.alembic_version
Tracks the version of the database schema managed by Alembic migrations.

Columns
version_num
Type: varchar
Required: Yes
Primary key: Yes
Description: Current Alembic migration revision identifier.
Constraints
Primary key: alembic_version_pkc on version_num
Usage
This is an internal migration-management table and normally should not be exposed through the application API.

Security Findings
RLS is disabled on all tables
Row Level Security is currently disabled for:

public.users
public.scenarios
public.roleplay_sessions
public.alembic_version
As a result, these tables are fully exposed to Supabase anon and authenticated roles when accessed through Supabase client libraries, subject to any separate grants.

This is especially important because:

users contains email addresses and password hashes.
scenarios contains system prompts and potentially sensitive application logic.
roleplay_sessions contains user-linked performance data.
alembic_version is an internal migration table.
Enabling RLS alone will block access until appropriate policies are added. The following SQL shows only the enablement step and has not been applied:

Run SQL

Database

Run

1234
ALTER TABLE "public"."users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."scenarios" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."roleplay_sessions" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."alembic_version" ENABLE ROW LEVEL SECURITY;
Run the query to see results

0 rows

·

Limit 100 rows

Policies should then be designed around the application's authentication model. For example, users would generally be allowed to read and update only their own records, while scenarios might be publicly readable only when is_active = true.

Recommended Improvements
High priority
Enable RLS on all application tables.
Add policies for users, roleplay_sessions, and scenarios.
Prevent client-side access to password_hash.
Restrict access to alembic_version.
Confirm whether system_prompt should be exposed to clients.
Data integrity
Add a unique constraint to scenarios.slug if it is an identifier.
Add a check constraint for roleplay_sessions.xp_earned >= 0.
Add a check constraint for valid session statuses.
Add validation for scenarios.max_turns.
Define valid values for difficulty and category.
Consider enforcing consistency between status and completed_at.
Performance
Consider indexes on:

roleplay_sessions.user_id
roleplay_sessions.scenario_id
roleplay_sessions.created_at
scenarios.is_active
scenarios.slug
The unique constraints on users.username and users.email already provide unique indexes for those columns.

Maintainability
Add table and column comments.
Document the expected JSON structures for financial_context and initial_state.
Define whether roleplay_sessions.scenario is a snapshot or redundant data.
Add an automatic update mechanism for scenarios.updated_at and users.updated_at.
Consider using Supabase Auth instead of maintaining a custom password-hash column.
