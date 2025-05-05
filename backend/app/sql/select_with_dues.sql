SELECT DISTINCT f.doc_id
FROM public.flat_resolution f
WHERE jsonb_path_exists(
    f.recipients,
    '$[*] ? (@.sedo_id == "78264321")'
)
	AND jsonb_path_exists(
    f.controls,
    '$[*] ? (@.person == "Габитов Д.Ш." && @.due_date != null && @.closed_date == null)');