WITH RECURSIVE

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
    WHERE (jsonb_path_exists(controls, $1) OR 1 = 1)
      AND jsonb_path_exists(recipients, $2)
      AND doc_id = ANY($3::int[])
),

resolution_chain AS (
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



boss_node AS (
    SELECT DISTINCT ON (leaf_id)
        leaf_id,
        id AS boss_id,
        controls
    FROM resolution_chain
    WHERE type = 'Резолюция'
      AND jsonb_path_exists(
            recipients,
            $4
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
            $5
        )
    ORDER BY leaf_id, depth ASC
),

boss3_node AS (
    SELECT DISTINCT ON (leaf_id)
        leaf_id,
        id AS boss3_id,
        controls
    FROM resolution_chain
    WHERE type = 'Резолюция'
      AND jsonb_path_exists(
            recipients,
            $6
        )
    ORDER BY leaf_id, depth ASC
),

executor_due AS (
    SELECT DISTINCT ON (leaf_id)
        leaf_id,
        COALESCE(c ->> 'modified_date', c ->> 'due_date') AS due_date
    FROM initial_leafs,
         jsonb_array_elements(leaf_controls) AS c
    WHERE c ->> 'person' = $7
      AND c ->> 'closed_date' IS NULL
    ORDER BY leaf_id,
        CASE WHEN COALESCE(c ->> 'modified_date', c ->> 'due_date')::timestamp < NOW() THEN 0 ELSE 1 END,
        ABS(EXTRACT(EPOCH FROM (COALESCE(c ->> 'modified_date', c ->> 'due_date')::timestamp - NOW())))
),

boss_due AS (
    SELECT DISTINCT ON (b.leaf_id)
        b.leaf_id,
        COALESCE(c ->> 'modified_date', c ->> 'due_date') AS due_date
    FROM boss_node b,
         jsonb_array_elements(b.controls) AS c
    WHERE c ->> 'person' = $8
      AND c ->> 'closed_date' IS NULL
    ORDER BY b.leaf_id,
        CASE WHEN COALESCE(c ->> 'modified_date', c ->> 'due_date')::timestamp < NOW() THEN 0 ELSE 1 END,
        ABS(EXTRACT(EPOCH FROM (COALESCE(c ->> 'modified_date', c ->> 'due_date')::timestamp - NOW())))
),

boss2_due AS (
    SELECT DISTINCT ON (b.leaf_id)
        b.leaf_id,
        COALESCE(c ->> 'modified_date', c ->> 'due_date') AS due_date
    FROM boss2_node b,
         jsonb_array_elements(b.controls) AS c
    WHERE c ->> 'person' = $9
      AND c ->> 'closed_date' IS NULL
    ORDER BY b.leaf_id,
        CASE WHEN COALESCE(c ->> 'modified_date', c ->> 'due_date')::timestamp < NOW() THEN 0 ELSE 1 END,
        ABS(EXTRACT(EPOCH FROM (COALESCE(c ->> 'modified_date', c ->> 'due_date')::timestamp - NOW())))
),

boss3_due AS (
    SELECT DISTINCT ON (b.leaf_id)
        b.leaf_id,
        COALESCE(c ->> 'modified_date', c ->> 'due_date') AS due_date
    FROM boss3_node b,
         jsonb_array_elements(b.controls) AS c
    WHERE c ->> 'person' = $10
      AND c ->> 'closed_date' IS NULL
    ORDER BY b.leaf_id,
        CASE WHEN COALESCE(c ->> 'modified_date', c ->> 'due_date')::timestamp < NOW() THEN 0 ELSE 1 END,
        ABS(EXTRACT(EPOCH FROM (COALESCE(c ->> 'modified_date', c ->> 'due_date')::timestamp - NOW())))
),

recursive_children AS (
    -- стартуем с initial_leafs.id (а не их детей!)
    SELECT
        fr.id AS current_id,
        fr.parent_id,
        fr.type,
        fr.controls,
        fr.recipients,
        fr.author_id,
        i.leaf_id AS origin_leaf_id
    FROM initial_leafs i
    JOIN flat_resolution fr ON fr.parent_id = i.leaf_id

    UNION ALL

    SELECT
        fr.id,
        fr.parent_id,
        fr.type,
        fr.controls,
        fr.recipients,
        fr.author_id,
        rc.origin_leaf_id
    FROM flat_resolution fr
    JOIN recursive_children rc ON fr.parent_id = rc.current_id
),

child_controls AS (

    -- 1. Контроли от нужного автора в "Резолюции" или "Направлении"
    SELECT
        rc.origin_leaf_id AS leaf_id,
        jsonb_agg(
            jsonb_build_object(
                'person', c ->> 'person',
                'due_date', c ->> 'due_date',
                'closed_date', c ->> 'closed_date',
                'is_control', c ->> 'is_control',
                'modified_date', c ->> 'modified_date'
            )
        ) FILTER (
            WHERE 
                c ->> 'person' IS NOT NULL OR
                c ->> 'due_date' IS NOT NULL OR
                c ->> 'closed_date' IS NOT NULL OR
                c ->> 'is_control' IS NOT NULL OR
                c ->> 'modified_date' IS NOT NULL
        ) AS children_controls
    FROM recursive_children rc,
         jsonb_array_elements(rc.controls) AS c
    WHERE rc.type IN ('Резолюция', 'Направление')
      AND rc.author_id = $11
    GROUP BY rc.origin_leaf_id

    UNION ALL

    -- 2. Если контролей нет — recipients с тем же sedo_id от "Резолюции" или "Направления"
    SELECT
        rc.origin_leaf_id AS leaf_id,
        jsonb_agg(
            jsonb_build_object(
                'person', r ->> 'fio',
                'due_date', NULL,
                'closed_date', NULL,
                'is_control', NULL,
                'modified_date', NULL
            )
        ) AS children_controls
    FROM recursive_children rc,
    jsonb_array_elements(rc.recipients) AS r
    WHERE rc.author_id = $11
      AND rc.type IN ('Резолюция', 'Направление документа. ')
--      AND rc.author_id = $11
      AND (
        NOT jsonb_path_exists(rc.controls, '$[*] ? (@.person != null)')
      )
    GROUP BY rc.origin_leaf_id
),

crazy AS (
    SELECT 
        i.leaf_id AS res_id,
        i.doc_id,
        ed.due_date AS executor_due_date,
        bd.due_date AS boss_due_date,
        b2d.due_date AS boss2_due_date,
        b3d.due_date AS boss3_due_date,
        cc.children_controls,
        EXISTS (
            SELECT 1
            FROM jsonb_array_elements(i.recipients) AS r
            WHERE r ->> 'sedo_id' = $11::text
            AND r ->> 'text' LIKE '+%'
        ) AS is_additional
    FROM initial_leafs i
    LEFT JOIN child_controls cc ON cc.leaf_id = i.leaf_id
    LEFT JOIN executor_due ed ON ed.leaf_id = i.leaf_id
    LEFT JOIN boss_due bd ON bd.leaf_id = i.leaf_id
    LEFT JOIN boss2_due b2d ON b2d.leaf_id = i.leaf_id
    LEFT JOIN boss3_due b3d ON b3d.leaf_id = i.leaf_id
),

filtered_sogly AS (
  SELECT *
  FROM public.sogly
  WHERE NOT jsonb_path_exists(
    structure,
    '$.** ? (@.status == "Не согласовано")'
  )
)

SELECT 
    d.sedo_id,
    d.dgi_number,
    d.date,
    d.description,
    d.signed_by_fio AS author,
    d.signed_by_company AS author_company,
    best.res_id,
    best.is_additional,
    (best.executor_due_date)::date,
    (best.boss_due_date)::date,
    (best.boss2_due_date)::date,
    (best.boss3_due_date)::date,
    best.children_controls,
    s.dgi_number as s_dgi_number,
    s.date as s_date,
    s.sedo_id as s_sedo_id,
    s.registered_sedo_id as s_registered_sedo_id,
    s.registered_number as s_registered_number,
    s.started_at as s_started_at,
    s.structure as s_structure,
    d.updated_at
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
                    CASE WHEN boss3_due_date IS NULL THEN 1 ELSE 0 END,
                    ABS(EXTRACT(EPOCH FROM ((boss3_due_date)::timestamp - NOW()))),
                    CASE WHEN children_controls IS NOT NULL THEN 0 ELSE 1 END
            ) AS rn
        FROM crazy
    ) ranked
    WHERE rn = 1
) best ON d.sedo_id = best.doc_id
LEFT JOIN filtered_sogly s
  ON jsonb_path_exists(
       s.answer,
       '$[*] ? (@.answer_id == $id)',
       jsonb_build_object('id', to_jsonb(d.sedo_id))
     )
 AND (jsonb_path_exists(
       s.structure,
       '$.** ? (@.sedo_id == $target)',
       jsonb_build_object('target', to_jsonb($11))
     )
 OR EXISTS (
  SELECT 1
  FROM jsonb_path_query(s.structure, '$.**') AS node
  WHERE (node->>'sedo_id')::int = ANY($12::int[])
)
    )
ORDER BY d.sedo_id ASC;