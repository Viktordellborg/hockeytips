-- Hockeytips: tables for leagues, members and tips, with Row Level Security (RLS).
-- Run once in Supabase: SQL Editor -> New query -> paste -> Run.
-- auth.uid() is the id of the logged-in user making the request (null when logged out).

-- ---------- Tables ----------

create table public.leagues (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 1 and 50),
  -- 6 characters, e.g. "3F9A1C". Used to invite friends in step 5.
  invite_code text not null unique default upper(substr(md5(gen_random_uuid()::text), 1, 6)),
  created_by uuid not null default auth.uid() references auth.users on delete cascade,
  created_at timestamptz not null default now()
);

create table public.league_members (
  league_id uuid not null references public.leagues on delete cascade,
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  joined_at timestamptz not null default now(),
  primary key (league_id, user_id)  -- A user can only be in a league once.
);

-- One tip per user and game. It counts in every league the user is in.
create table public.tips (
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  game_id bigint not null,  -- The game id from the NHL API (id in schedule.json).
  picked_team text not null check (picked_team ~ '^[A-Z]{3}$'),  -- Team abbreviation, e.g. "TOR".
  created_at timestamptz not null default now(),
  primary key (user_id, game_id)
);

-- ---------- Helper functions ----------

-- Is the logged-in user a member of this league?
-- "security definer" runs with the owner's rights, so it can read league_members without
-- triggering the RLS policy on league_members again (that would loop forever).
create function public.is_league_member(league uuid)
returns boolean
language sql
security definer
set search_path = ''
stable
as $$
  select exists (
    select 1 from public.league_members
    where league_id = league and user_id = auth.uid()
  );
$$;

-- When someone creates a league, they become its first member automatically.
create function public.add_creator_as_member()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.league_members (league_id, user_id) values (new.id, new.created_by);
  return new;
end;
$$;

create trigger on_league_created
  after insert on public.leagues
  for each row execute function public.add_creator_as_member();

-- ---------- Table rights ----------
-- GRANT decides which tables a role may use at all. RLS below decides which rows.
-- Only logged-in users (authenticated) get rights. Logged-out visitors (anon) get none.

grant select, insert, update, delete on public.leagues to authenticated;
grant select, delete on public.league_members to authenticated;
grant select, insert, update, delete on public.tips to authenticated;
grant execute on function public.is_league_member(uuid) to authenticated;

-- ---------- Row Level Security ----------
-- With RLS on, nothing is allowed until a policy allows it.
-- "to authenticated" means only logged-in users. Logged-out visitors get nothing.

alter table public.leagues enable row level security;
alter table public.league_members enable row level security;
alter table public.tips enable row level security;

-- Leagues: see leagues you are in (or created), create leagues as yourself,
-- and only the creator may rename or delete.
create policy "Members can see their leagues" on public.leagues
  for select to authenticated
  using (created_by = auth.uid() or public.is_league_member(id));

create policy "Users can create leagues" on public.leagues
  for insert to authenticated
  with check (created_by = auth.uid());

create policy "Creator can update league" on public.leagues
  for update to authenticated
  using (created_by = auth.uid())
  with check (created_by = auth.uid());

create policy "Creator can delete league" on public.leagues
  for delete to authenticated
  using (created_by = auth.uid());

-- Members: see who is in your leagues and leave a league yourself.
-- No insert policy: joining happens through the trigger above and, in step 5, an invite code function.
create policy "Members can see co-members" on public.league_members
  for select to authenticated
  using (public.is_league_member(league_id));

create policy "Users can leave leagues" on public.league_members
  for delete to authenticated
  using (user_id = auth.uid());

-- Tips: only your own, for now. Seeing friends' tips and the start-time rule come in steps 4 and 6.
create policy "Users can see own tips" on public.tips
  for select to authenticated
  using (user_id = auth.uid());

create policy "Users can add own tips" on public.tips
  for insert to authenticated
  with check (user_id = auth.uid());

create policy "Users can change own tips" on public.tips
  for update to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

create policy "Users can delete own tips" on public.tips
  for delete to authenticated
  using (user_id = auth.uid());
