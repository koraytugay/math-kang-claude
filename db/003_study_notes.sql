-- "Studied together" and "try this skill again" (PLAN.md, 2026-11-23). Run once as the database owner.
-- kind 'studied': a question the parent studied with a child (ref = question id).
-- kind 'retry':   a skill that must come back in the first questions of the child's next session (ref = skill key);
--                 done_at is set when the child has answered a question of that skill.
create table if not exists study_notes (
    id         bigserial primary key,
    profile_id text not null references profiles(id),
    kind       text not null,
    ref        text not null,
    created_at timestamptz not null default now(),
    done_at    timestamptz
);
create index if not exists study_notes_profile on study_notes (profile_id, kind);
grant select, insert, update on study_notes to mk_site;
grant usage on sequence study_notes_id_seq to mk_site;
-- one-off: the old "studied:<question id>" rows of the achievements table
-- insert into study_notes (profile_id, kind, ref)
--   select profile_id, 'studied', substr(code, 9) from achievements where code like 'studied:%';
