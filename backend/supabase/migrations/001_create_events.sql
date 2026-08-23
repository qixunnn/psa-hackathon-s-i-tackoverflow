create table if not exists public.events (
    id text primary key,
    title text not null,
    event_type text not null check (
        event_type in (
            'CHOKEPOINT_DISRUPTION',
            'CANAL_CLOSURE',
            'CARRIER_REROUTING',
            'PORT_STRIKE',
            'PORT_DISRUPTION',
            'SEVERE_WEATHER',
            'SECURITY_INCIDENT',
            'TRADE_RESTRICTION',
            'SANCTIONS',
            'PIRACY',
            'OTHER'
        )
    ),
    status text not null check (
        status in (
            'MONITORING',
            'ACTIVE',
            'ESCALATING',
            'STABILISING',
            'RESOLVED',
            'ARCHIVED'
        )
    ),
    summary text not null,
    primary_location jsonb not null check (
        jsonb_typeof(primary_location) = 'object'
        and primary_location ? 'name'
    ),
    severity text not null check (
        severity in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    ),
    confidence double precision not null check (
        confidence >= 0.0 and confidence <= 1.0
    ),
    first_seen timestamptz not null,
    last_updated timestamptz not null,
    source_ids text[] not null default '{}',
    evidence_ids text[] not null default '{}',
    development_ids text[] not null default '{}',
    route_exposure jsonb check (
        route_exposure is null
        or (
            jsonb_typeof(route_exposure) = 'object'
            and route_exposure ?& array[
                'chokepointIds',
                'affectedTradeCorridors',
                'alternativeRoutes',
                'explanation',
                'resolved'
            ]
        )
    ),
    latest_scenario_run_id text,
    latest_operational_impact_id text,
    recommendation_ids text[] not null default '{}',
    is_synthetic boolean not null,
    constraint events_dates_valid check (first_seen <= last_updated)
);

create index if not exists events_last_updated_idx
    on public.events (last_updated desc);

alter table public.events enable row level security;

revoke all on table public.events from anon, authenticated;
grant all privileges on table public.events to service_role;
