-- PLAN.md 4.1: after a wrong first answer the child gets one more try. `correct` stays the first try;
-- second_try says whether the second click was right (null when the first try was right).
alter table attempts add column if not exists second_try boolean;
