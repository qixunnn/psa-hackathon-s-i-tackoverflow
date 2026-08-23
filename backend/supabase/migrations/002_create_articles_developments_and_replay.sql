create table if not exists public.articles (
    id text primary key,
    title text not null,
    content text not null,
    source_name text not null,
    source_type text not null check (
        source_type in (
            'NEWS',
            'MARITIME_BULLETIN',
            'CARRIER_ADVISORY',
            'AUTHORITY_NOTICE',
            'WEATHER_SOURCE',
            'REPLAY_DATA',
            'OTHER'
        )
    ),
    url text,
    published_at timestamptz not null,
    ingested_at timestamptz not null,
    is_synthetic boolean not null,
    content_hash text
);

create unique index if not exists articles_content_hash_idx
    on public.articles (content_hash)
    where content_hash is not null;

create table if not exists public.developments (
    id text primary key,
    event_id text not null references public.events (id) on delete cascade,
    timestamp timestamptz not null,
    title text not null,
    summary text not null,
    source_ids text[] not null default '{}',
    evidence_ids text[] not null default '{}',
    previous_severity text check (
        previous_severity is null
        or previous_severity in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    ),
    new_severity text check (
        new_severity is null
        or new_severity in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    ),
    previous_confidence double precision check (
        previous_confidence is null
        or (previous_confidence >= 0.0 and previous_confidence <= 1.0)
    ),
    new_confidence double precision check (
        new_confidence is null
        or (new_confidence >= 0.0 and new_confidence <= 1.0)
    )
);

create index if not exists developments_event_timestamp_idx
    on public.developments (event_id, timestamp asc);

alter table public.articles enable row level security;
alter table public.developments enable row level security;

revoke all on table public.articles, public.developments from anon, authenticated;
grant all privileges on table public.articles, public.developments to service_role;

-- Migration 001 seeded placeholder IDs before Development persistence existed.
update public.events
set development_ids = '{}'
where id = 'EVT-001'
  and development_ids = array['DEV-001', 'DEV-002']
  and not exists (
      select 1 from public.developments where event_id = 'EVT-001'
  );

create or replace function public.replay_demo_article(
    p_article_id text,
    p_title text,
    p_content text,
    p_source_name text,
    p_source_type text,
    p_url text,
    p_published_at timestamptz,
    p_ingested_at timestamptz,
    p_is_synthetic boolean,
    p_content_hash text,
    p_event_id text,
    p_event_summary text,
    p_new_status text,
    p_new_severity text,
    p_new_confidence double precision,
    p_development_id text,
    p_development_timestamp timestamptz,
    p_development_title text,
    p_development_summary text
)
returns void
language plpgsql
security invoker
set search_path = public
as $$
declare
    v_previous_severity text;
    v_previous_confidence double precision;
begin
    if not p_is_synthetic then
        raise exception 'Demo replay articles must be synthetic.'
            using errcode = '22023';
    end if;

    select severity, confidence
    into v_previous_severity, v_previous_confidence
    from public.events
    where id = p_event_id
    for update;

    if not found then
        raise exception 'Event % does not exist.', p_event_id
            using errcode = 'P0002';
    end if;

    insert into public.articles (
        id,
        title,
        content,
        source_name,
        source_type,
        url,
        published_at,
        ingested_at,
        is_synthetic,
        content_hash
    )
    values (
        p_article_id,
        p_title,
        p_content,
        p_source_name,
        p_source_type,
        p_url,
        p_published_at,
        p_ingested_at,
        p_is_synthetic,
        p_content_hash
    );

    insert into public.developments (
        id,
        event_id,
        timestamp,
        title,
        summary,
        source_ids,
        evidence_ids,
        previous_severity,
        new_severity,
        previous_confidence,
        new_confidence
    )
    values (
        p_development_id,
        p_event_id,
        p_development_timestamp,
        p_development_title,
        p_development_summary,
        '{}',
        '{}',
        v_previous_severity,
        p_new_severity,
        v_previous_confidence,
        p_new_confidence
    );

    update public.events
    set summary = p_event_summary,
        status = p_new_status,
        severity = p_new_severity,
        confidence = p_new_confidence,
        last_updated = p_development_timestamp,
        development_ids = array_append(development_ids, p_development_id)
    where id = p_event_id;
end;
$$;

revoke execute on function public.replay_demo_article(
    text,
    text,
    text,
    text,
    text,
    text,
    timestamptz,
    timestamptz,
    boolean,
    text,
    text,
    text,
    text,
    text,
    double precision,
    text,
    timestamptz,
    text,
    text
) from public, anon, authenticated;

grant execute on function public.replay_demo_article(
    text,
    text,
    text,
    text,
    text,
    text,
    timestamptz,
    timestamptz,
    boolean,
    text,
    text,
    text,
    text,
    text,
    double precision,
    text,
    timestamptz,
    text,
    text
) to service_role;
