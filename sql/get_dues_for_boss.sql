WITH RECURSIVE resolution_chain AS (
    SELECT 
        i.leaf_id,
        r.id,
        r.parent_id,
        r.doc_id,
        i.leaf_controls,
        r.controls,
        r.recipients,
        r.executions,
        0 AS depth
    FROM initial_leafs i
    JOIN public.flat_resolution r ON r.id = i.leaf_id

    UNION ALL

    SELECT 
        rc.leaf_id,
        p.id,
        p.parent_id,
        p.doc_id,
        rc.leaf_controls,
        p.controls,
        p.recipients,
        p.executions,
        rc.depth + 1
    FROM public.flat_resolution p
    JOIN resolution_chain rc ON p.id = rc.parent_id
),

initial_leafs AS (
    SELECT 
        fr.id AS leaf_id,
        fr.parent_id,
        fr.id,
        fr.doc_id,
        fr.controls AS leaf_controls,
        fr.recipients,
        fr.executions
    FROM public.flat_resolution fr
    WHERE jsonb_path_exists(
        controls,
        '$[*] ? (@.person == "Мусиенко О.А." && @.closed_date == null)'
    )
    AND jsonb_path_exists(
        recipients,
        '$[*] ? (@.sedo_id == "70045")'
    )
    AND NOT jsonb_path_exists(
        executions,
        '$[*] ? (@.author like_regex "Мусиенко О.А.")'
    )
),



boss_node AS (
    SELECT DISTINCT ON (leaf_id)
        leaf_id,
        id AS boss_id,
        controls
    FROM resolution_chain
    WHERE jsonb_path_exists(
        recipients,
        '$[*] ? (@.sedo_id == "78164285")'
    )
    ORDER BY leaf_id, depth ASC
),

executor_due AS (
    SELECT DISTINCT ON (leaf_id)
        leaf_id,
        c ->> 'due_date' AS due_date
    FROM initial_leafs,
         jsonb_array_elements(leaf_controls) AS c
    WHERE c ->> 'person' = 'Мусиенко О.А.'
      AND c ->> 'closed_date' IS NULL
    ORDER BY leaf_id,
      CASE 
        WHEN c ->> 'due_date' IS NOT NULL AND (c ->> 'due_date')::timestamp < NOW() THEN 0
        ELSE 1
      END,
      ABS(EXTRACT(EPOCH FROM ((c ->> 'due_date')::timestamp - NOW())))
)

,

boss_due AS (
    SELECT DISTINCT ON (b.leaf_id)
        b.leaf_id,
        c ->> 'due_date' AS due_date
    FROM boss_node b,
         jsonb_array_elements(b.controls) AS c
    WHERE c ->> 'person' = 'Биктимиров Р.Г.'
      AND c ->> 'closed_date' IS NULL
    ORDER BY b.leaf_id,
      CASE 
        WHEN c ->> 'due_date' IS NOT NULL AND (c ->> 'due_date')::timestamp < NOW() THEN 0
        ELSE 1
      END,
      ABS(EXTRACT(EPOCH FROM ((c ->> 'due_date')::timestamp - NOW())))
)

SELECT 
    i.leaf_id AS res_id,
	i.parent_id as parent_id,
    i.doc_id,
    'Мусиенко О.А.' AS executor_name,
    ed.due_date AS executor_due_date,
    'Биктимиров Р.Г.' AS boss_name,
    bd.due_date AS boss_due_date
FROM initial_leafs i
LEFT JOIN executor_due ed ON ed.leaf_id = i.leaf_id
LEFT JOIN boss_due bd ON bd.leaf_id = i.leaf_id
ORDER BY i.leaf_id;