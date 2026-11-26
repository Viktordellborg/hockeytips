-- Step 5: join a league with an invite code.
-- Run once in Supabase (SQL Editor), after schema.sql.
--
-- Why a function? RLS hides leagues you are not in, and there is no insert policy on
-- league_members. This function runs with the owner's rights (security definer), but it only
-- does one thing: find the league with the code and add the logged-in user to it.

create function public.join_league(code text)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  found_league uuid;
begin
  if auth.uid() is null then
    raise exception 'Du måste vara inloggad.';
  end if;

  select id into found_league
  from public.leagues
  where invite_code = upper(trim(code));

  if found_league is null then
    raise exception 'Ingen liga har den koden.';
  end if;

  -- "on conflict do nothing": joining a league you are already in is not an error.
  insert into public.league_members (league_id, user_id)
  values (found_league, auth.uid())
  on conflict do nothing;

  return found_league;
end;
$$;

-- Only logged-in users may call it.
revoke execute on function public.join_league(text) from public, anon;
grant execute on function public.join_league(text) to authenticated;
