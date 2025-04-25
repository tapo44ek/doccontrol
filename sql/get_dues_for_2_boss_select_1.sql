WITH RECURSIVE resolution_chain AS (
    SELECT 
        i.leaf_id,
        r.id,
        r.parent_id,
        r.doc_id,
        r.type,
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
        p.type,
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
    WHERE type = 'Резолюция'
      AND jsonb_path_exists(
            recipients,
            '$[*] ? (@.sedo_id == "78164285")'
        )
    ORDER BY leaf_id, depth ASC
),

boss2_node AS (
    SELECT DISTINCT ON (leaf_id)
        leaf_id,
        id AS boss2_id,
        controls
    FROM resolution_chain
    WHERE type = 'Резолюция'
      AND jsonb_path_exists(
            recipients,
            '$[*] ? (@.sedo_id == "1558294")'
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
        CASE WHEN (c ->> 'due_date')::timestamp < NOW() THEN 0 ELSE 1 END,
        ABS(EXTRACT(EPOCH FROM ((c ->> 'due_date')::timestamp - NOW())))
),

boss_due AS (
    SELECT DISTINCT ON (b.leaf_id)
        b.leaf_id,
        c ->> 'due_date' AS due_date
    FROM boss_node b,
         jsonb_array_elements(b.controls) AS c
    WHERE c ->> 'person' = 'Биктимиров Р.Г.'
      AND c ->> 'closed_date' IS NULL
    ORDER BY b.leaf_id,
        CASE WHEN (c ->> 'due_date')::timestamp < NOW() THEN 0 ELSE 1 END,
        ABS(EXTRACT(EPOCH FROM ((c ->> 'due_date')::timestamp - NOW())))
),

boss2_due AS (
    SELECT DISTINCT ON (b.leaf_id)
        b.leaf_id,
        c ->> 'due_date' AS due_date
    FROM boss2_node b,
         jsonb_array_elements(b.controls) AS c
    WHERE c ->> 'person' = 'Гаман М.Ф.'
      AND c ->> 'closed_date' IS NULL
    ORDER BY b.leaf_id,
        CASE WHEN (c ->> 'due_date')::timestamp < NOW() THEN 0 ELSE 1 END,
        ABS(EXTRACT(EPOCH FROM ((c ->> 'due_date')::timestamp - NOW())))
),

child_controls AS (
    SELECT
        fr.parent_id AS leaf_id,
        jsonb_agg(
            jsonb_build_object(
                'person', c ->> 'person',
                'due_date', c ->> 'due_date',
                'closed_date', c ->> 'closed_date',
                'is_control', c ->> 'is_control',
                'modified_date', c ->> 'modified_date'
            )
        ) AS children_controls
    FROM flat_resolution fr,
         jsonb_array_elements(fr.controls) AS c
    WHERE fr.type = 'Резолюция'
      AND fr.author_id = 70045
      AND fr.parent_id IN (SELECT leaf_id FROM initial_leafs)
    GROUP BY fr.parent_id
),

crazy AS (
    SELECT 
        i.leaf_id AS res_id,
        i.doc_id,
        'Мусиенко О.А.' AS executor_name,
        ed.due_date AS executor_due_date,
        'Биктимиров Р.Г.' AS boss_name,
        bd.due_date AS boss_due_date,
        'Гаман М.Ф.' AS boss2_name,
        b2d.due_date AS boss2_due_date,
        cc.children_controls 
    FROM initial_leafs i
    LEFT JOIN child_controls cc ON cc.leaf_id = i.leaf_id
    LEFT JOIN executor_due ed ON ed.leaf_id = i.leaf_id
    LEFT JOIN boss_due bd ON bd.leaf_id = i.leaf_id
    LEFT JOIN boss2_due b2d ON b2d.leaf_id = i.leaf_id
)

SELECT 
    d.sedo_id,
    d.dgi_number,
    d.date,
    d.description,
    d.signed_by_fio AS author,
    d.signed_by_company AS author_company,
    best.res_id,
    best.executor_name,
    (best.executor_due_date)::date,
    best.boss_name,
    (best.boss_due_date)::date,
    best.boss2_name,
    (best.boss2_due_date)::date,
    best.children_controls
FROM public.documents d
JOIN (
    SELECT *
    FROM (
        SELECT 
            crazy.*,
            ROW_NUMBER() OVER (
                PARTITION BY doc_id
                ORDER BY
                    CASE WHEN executor_due_date IS NULL THEN 1 ELSE 0 END,
                    ABS(EXTRACT(EPOCH FROM ((executor_due_date)::timestamp - NOW()))),
                    CASE WHEN boss_due_date IS NULL THEN 1 ELSE 0 END,
                    ABS(EXTRACT(EPOCH FROM ((boss_due_date)::timestamp - NOW()))),
                    CASE WHEN boss2_due_date IS NULL THEN 1 ELSE 0 END,
                    ABS(EXTRACT(EPOCH FROM ((boss2_due_date)::timestamp - NOW()))),
                    CASE WHEN children_controls IS NOT NULL THEN 0 ELSE 1 END
            ) AS rn
        FROM crazy
    ) ranked
    WHERE rn = 1
) best ON d.sedo_id = best.doc_id
ORDER BY d.sedo_id ASC;