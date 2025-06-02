import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { parseISO, format } from 'date-fns';
import { ru } from 'date-fns/locale';

const backendUrl = import.meta.env.VITE_BACKEND_URL;

const parseChildren = (controls) => {
  if (Array.isArray(controls)) return controls;
  if (!controls) return [];
  try {
    const cleanedString = controls.replace(/^"+|"+$/g, '').replace(/\\"/g, '"');
    return JSON.parse(cleanedString);
  } catch (e) {
    console.error('Parse error:', e);
    return [];
  }
};

const DateBadge = ({ date }) => {
  if (!date || typeof date !== 'string') return null;
  const parsed = parseISO(date);
  if (isNaN(parsed)) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  parsed.setHours(0, 0, 0, 0);
  const diff = (parsed - today) / (1000 * 60 * 60 * 24);
  let badgeColor = 'bg-green-100 text-green-800';
  if (diff < 0) badgeColor = 'bg-red-100 text-red-800';
  else if (diff <= 3) badgeColor = 'bg-yellow-100 text-yellow-800';
  const formatted = format(parsed, 'dd.MM.yyyy', { locale: ru });
  return <span className={`inline-block px-2 py-0.5 text-xs font-semibold rounded-full ${badgeColor}`}>{formatted}</span>;
};

const VirtualizedTableDivs = ({ data }) => {
  const [bossNames, setBossNames] = useState({ boss1: null, boss2: null, boss3: null });
  const [expandedRows, setExpandedRows] = useState({});

  useEffect(() => {
    fetch(`${backendUrl}/doccontrol/boss_names`, { credentials: 'include' })
      .then(res => res.json())
      .then(setBossNames)
      .catch(console.error);
  }, []);

  const flatData = useMemo(() => {
    if (!data) return [];
    return data.map(item => {
      const children = parseChildren(item.children_controls);
      return { ...item, _children: children };
    });
  }, [data]);

  const parentRef = useRef(null);
  const rowVirtualizer = useVirtualizer({
    count: flatData.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80,
    overscan: 10,
  });

  const columns = useMemo(() => [
    { key: 'dgi_number', title: '№ ДГИ', width: '160px' },
    { key: 'date', title: 'Дата', width: '100px' },
    { key: 'description', title: 'Содержание', width: '400px' },
    { key: 'executor_due_date', title: 'Срок исполнения', width: '120px' },
    ...(bossNames.boss1 ? [{ key: 'boss_due_date', title: `Срок: ${bossNames.boss1}`, width: '120px' }] : []),
    ...(bossNames.boss2 ? [{ key: 'boss2_due_date', title: `Срок: ${bossNames.boss2}`, width: '120px' }] : []),
    ...(bossNames.boss3 ? [{ key: 'boss3_due_date', title: `Срок: ${bossNames.boss3}`, width: '120px' }] : []),
    { key: 'child_table', title: 'Исполнители', width: '240px' },
  ], [bossNames]);

  const toggleExpand = (idx) =>
    setExpandedRows(prev => ({ ...prev, [idx]: !prev[idx] }));

  return (
<table className="w-full border-collapse">
  <thead>
    <tr className="sticky top-0 bg-white z-10 shadow-sm text-xs font-medium border-b border-gray-300">
      {columns.map(col => (
        <th key={col.key} style={{ width: col.width }} className="px-3 py-2 bg-gray-100">{col.title}</th>
      ))}
    </tr>
  </thead>
  <tbody style={{ height: rowVirtualizer.getTotalSize(), position: 'relative' }}>
    {rowVirtualizer.getVirtualItems().map(virtualRow => {
      const row = flatData[virtualRow.index];
      const isExpanded = expandedRows[virtualRow.index];

      return (
        <tr
          key={virtualRow.key}
          ref={el => rowVirtualizer.measureElement(el)}
          data-index={virtualRow.index}
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            width: '100%',
            transform: `translateY(${virtualRow.start}px)`,
          }}
          className="text-xs border-b border-gray-200 align-top"
        >
          {columns.map(col => (
            <td key={col.key} style={{ width: col.width, verticalAlign: 'top' }} className="px-3 py-2 align-top">
              {col.key === 'description' ? (
                <div>
                  {(isExpanded || !row[col.key] || row[col.key].length <= 80)
                    ? row[col.key]
                    : (
                      <>
                        {row[col.key].slice(0, 80) + '... '}
                        <button
                          className="text-blue-600 underline text-[11px]"
                          onClick={() => toggleExpand(virtualRow.index)}
                        >Показать полностью</button>
                      </>
                    )
                  }
                  {isExpanded && row[col.key] && row[col.key].length > 80 && (
                    <button
                      className="text-blue-600 underline text-[11px] ml-2"
                      onClick={() => toggleExpand(virtualRow.index)}
                    >Скрыть</button>
                  )}
                </div>
              ) : col.key === 'dgi_number' ? (
                <a
                  href={`https://mosedo.mos.ru/document.card.php?id=${row.sedo_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline"
                >
                  {row.dgi_number}
                </a>
              ) : col.key === 'child_table' ? (
                <div className="text-[11px]">
                  {row._children.length === 0 ? (
                    <span className="text-gray-400 italic">нет</span>
                  ) : (
                    <table className="w-full table-fixed border-collapse">
                      <thead>
                        <tr className="text-gray-500">
                          <th className="text-left">ФИО</th>
                          <th className="text-left">Срок</th>
                          <th className="text-left">Закрыто</th>
                        </tr>
                      </thead>
                      <tbody>
                        {row._children.map((child, idx) => (
                          <tr key={idx}>
                            <td className="w-1/3 pr-1 whitespace-nowrap">{child.person}</td>
                            <td className="w-1/3 pr-1"><DateBadge date={child.due_date} /></td>
                            <td className="w-1/3 text-gray-500">{child.closed_date || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              ) : col.key.includes('due_date') ? (
                <DateBadge date={row[col.key]} />
              ) : (
                row[col.key] || ''
              )}
            </td>
          ))}
        </tr>
      );
    })}
  </tbody>
</table>
  );
};

export default VirtualizedTableDivs;