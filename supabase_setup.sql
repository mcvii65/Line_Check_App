create extension if not exists pgcrypto;

create table if not exists public.bets (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz not null default now(),
    username text not null,
    bet_date date not null,
    matchup text not null,
    bet_type text not null,
    odds integer not null,
    stake numeric not null,
    user_probability numeric not null,
    result text not null default 'pending',
    profit numeric,
    notes text
);

-- Row level security (RLS) should be enabled when real authentication and
-- user-scoped policies are added. With no login system yet, username only
-- separates records in the app; it is not real security or access control.
comment on column public.bets.username is
    'Display filter only; without authentication this value is not a security boundary.';
