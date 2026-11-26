-- Step 6: display names and seeing league friends' tips, for the leaderboard.
-- Run once in Supabase (SQL Editor), after schema.sql and join-league.sql.
--
-- A tip on a tie is saved as picked_team = 'TIE'. It already passes the check on tips
-- (three capital letters), so the tips table does not need to change.

-- Do the logged-in user and this user share at least one league?
-- security definer for the same reason as is_league_member: it reads league_members without RLS.
create function public.shares_league(other_user uuid)
returns boolean
language sql
security definer
set search_path = ''
stable
as $$
  select exists (
    select 1
    from public.league_members mine
    join public.league_members theirs on theirs.league_id = mine.league_id
    where mine.user_id = auth.uid() and theirs.user_id = other_user
  );
$$;

-- Display names. Email addresses stay private, so others see this name instead.
create table public.profiles (
  id uuid primary key default auth.uid() references auth.users on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 30),
  updated_at timestamptz not null default now()
);

grant select, insert, update on public.profiles to authenticated;
grant execute on function public.shares_league(uuid) to authenticated;

alter table public.profiles enable row level security;

create policy "Users can see own and league friends' profiles" on public.profiles
  for select to authenticated
  using (id = auth.uid() or public.shares_league(id));

create policy "Users can create own profile" on public.profiles
  for insert to authenticated
  with check (id = auth.uid());

create policy "Users can change own profile" on public.profiles
  for update to authenticated
  using (id = auth.uid())
  with check (id = auth.uid());

-- Tips: league friends may now read each other's tips. Policies are combined with OR,
-- so "Users can see own tips" from schema.sql still applies.
-- Note: the start-time rule is only in the page, so friends can see tips before a game starts.
create policy "League friends can see tips" on public.tips
  for select to authenticated
  using (public.shares_league(user_id));
