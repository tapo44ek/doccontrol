SELECT *
FROM public.flat_resolution
-- ищем человека + нет даты снятия с контроля
WHERE jsonb_path_exists(
    controls,
    '$[*] ? (@.person == "Мусиенко О.А." && @.closed_date == null)'
  )
-- сверяем фамилию и сэдо айди
AND jsonb_path_exists(
    recipients,
    '$[*] ? (@.sedo_id == "70045")'
  )
-- нет отметки об исполнении
AND NOT jsonb_path_exists(
    executions,
    '$[*] ? (@.author like_regex "Мусиенко О.А.")'
  )
ORDER BY doc_id ASC;