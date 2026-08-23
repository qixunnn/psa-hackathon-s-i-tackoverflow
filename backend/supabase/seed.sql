delete from public.developments where event_id = 'EVT-001';
delete from public.articles
where id in ('ART-001', 'ART-002', 'ART-003', 'ART-004');

insert into public.events (
    id,
    title,
    event_type,
    status,
    summary,
    primary_location,
    severity,
    confidence,
    first_seen,
    last_updated,
    source_ids,
    evidence_ids,
    development_ids,
    route_exposure,
    latest_scenario_run_id,
    latest_operational_impact_id,
    recommendation_ids,
    is_synthetic
)
values (
    'EVT-001',
    'Bab el-Mandeb Security Disruption',
    'CHOKEPOINT_DISRUPTION',
    'ESCALATING',
    'Security incidents near Bab el-Mandeb have led to increasing carrier rerouting activity.',
    '{
        "name": "Bab el-Mandeb",
        "latitude": 12.58,
        "longitude": 43.33,
        "region": "Red Sea"
    }'::jsonb,
    'HIGH',
    0.84,
    '2026-08-20T08:00:00Z'::timestamptz,
    '2026-08-23T12:00:00Z'::timestamptz,
    array['SRC-001', 'SRC-002'],
    array['EVD-001'],
    array[]::text[],
    '{
        "chokepointIds": ["CHK-BAB"],
        "affectedTradeCorridors": ["Asia-Europe"],
        "alternativeRoutes": ["Cape of Good Hope"],
        "explanation": "The disruption may affect services using the Red Sea and Suez corridor.",
        "resolved": true
    }'::jsonb,
    'SCN-004',
    'IMP-004',
    array['REC-021', 'REC-022'],
    true
)
on conflict (id) do update set
    title = excluded.title,
    event_type = excluded.event_type,
    status = excluded.status,
    summary = excluded.summary,
    primary_location = excluded.primary_location,
    severity = excluded.severity,
    confidence = excluded.confidence,
    first_seen = excluded.first_seen,
    last_updated = excluded.last_updated,
    source_ids = excluded.source_ids,
    evidence_ids = excluded.evidence_ids,
    development_ids = excluded.development_ids,
    route_exposure = excluded.route_exposure,
    latest_scenario_run_id = excluded.latest_scenario_run_id,
    latest_operational_impact_id = excluded.latest_operational_impact_id,
    recommendation_ids = excluded.recommendation_ids,
    is_synthetic = excluded.is_synthetic;
