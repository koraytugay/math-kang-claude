-- Practice website database (PLAN.md, Phase 2). Run once as the database owner (neondb_owner).
-- First create the website's own user with ONE standalone SQL statement (not inside a script/transaction,
-- Neon refuses that). Do NOT create it in the Neon console/CLI: those roles join neon_superuser.
--     create role mk_site login password '<long random password>';

create table if not exists profiles (
    id          text primary key,              -- 'deniz', 'toprak', 'koray'
    name        text not null,
    avatar      text not null default '',
    is_parent   boolean not null default false
);

insert into profiles (id, name, avatar, is_parent) values
    ('deniz',  'Deniz',  '🦘', false),
    ('toprak', 'Toprak', '🐨', false),
    ('koray',  'Koray',  '🧪', true)
on conflict (id) do nothing;

-- One row per answered question.
create table if not exists attempts (
    id          bigserial primary key,
    profile_id  text not null references profiles(id),
    question_id text not null,                 -- "<generator>|<variant>|<seed>|h0/h1" from the bank
    gen         text not null,                 -- generator key = the skill
    variant     text not null,
    difficulty  smallint not null,             -- 1 = Part A, 2 = B, 3 = C
    harder      boolean not null default false,
    chosen      smallint not null,             -- 0..4 = A..E
    correct     boolean not null,
    seconds     integer not null default 0,
    created_at  timestamptz not null default now()
);
create index if not exists attempts_profile_time on attempts (profile_id, created_at);
create index if not exists attempts_profile_gen  on attempts (profile_id, gen);

-- Smart practice state per child per skill (Phase 3).
create table if not exists skill_state (
    profile_id  text not null references profiles(id),
    gen         text not null,
    level       smallint not null default 1,
    box         smallint not null default 0,   -- Leitner box
    due_at      timestamptz,
    streak      integer not null default 0,
    updated_at  timestamptz not null default now(),
    primary key (profile_id, gen)
);

-- Badges (Phase 4).
create table if not exists achievements (
    profile_id  text not null references profiles(id),
    code        text not null,
    earned_at   timestamptz not null default now(),
    primary key (profile_id, code)
);

-- The website's own user (mk_site): it can read and add/update rows in these tables, nothing else
-- (no deleting, no changing tables).
grant usage on schema public to mk_site;
grant select on profiles to mk_site;
grant select, insert on attempts to mk_site;
grant select, insert, update on skill_state, achievements to mk_site;
grant usage on sequence attempts_id_seq to mk_site;
