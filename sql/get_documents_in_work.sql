SELECT *
FROM public.flat_resolution
WHERE jsonb_path_exists(
    controls,
    '$[*] ? (@.person == "Мусиенко О.А." && @.closed_date != null)'
  )
AND jsonb_path_exists(
    recipients,
    '$[*] ? (@.sedo_id == "70045")'
  );