// I'll answer as фронтенд-лид по React UI от @tanstack/react-table с опытом в ГосИТ и Tailwind UI production
// Переписываю тебе виртуализированную таблицу с динамической высотой строк, валидной структурой и синхронным выравниванием колонок.

import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender
} from '@tanstack/react-table';
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

const NestedVirtualizedTable = ({ data }) => {
  const [bossNames, setBossNames] = useState({ boss1: null, boss2: null, boss3: null });

  useEffect(() => {
    fetch(`${backendUrl}/doccontrol/boss_names`, { credentials: 'include' })
      .then(res => res.json())
      .then(setBossNames)
      .catch(console.error);
  }, []);

  const flatData = useMemo(() => {
    return data.map(item => ({
      ...item,
      _children: parseChildren(item.children_controls)
    }));
  }, [data]);

  const columns = useMemo(() => {
    const base = [
      {
        accessorKey: 'dgi_number',
        header: '№ ДГИ',
        size: 160,
        cell: ({ row }) => (
          <a
            href={`https://mosedo.mos.ru/document.card.php?id=${row.original.sedo_id}`}
            className="text-blue-600 underline"
            target="_blank"
            rel="noopener noreferrer"
          >{row.original.dgi_number}</a>
        ),
      },
      {
        accessorKey: 'date',
        header: 'Дата',
        size: 100,
        cell: ({ row }) => row.original.date,
      },
      {
        accessorKey: 'description',
        header: 'Содержание',
        size: 400,
        cell: ({ row }) => row.original.description,
      },
      {
        accessorKey: 'executor_due_date',
        header: 'Срок исполнения',
        size: 120,
        cell: ({ row }) => <DateBadge date={row.original.executor_due_date} />,
      },
      ...(bossNames.boss1 ? [{
        accessorKey: 'boss_due_date',
        header: `Срок: ${bossNames.boss1}`,
        size: 120,
        cell: ({ row }) => <DateBadge date={row.original.boss_due_date} />,
      }] : []),
      ...(bossNames.boss2 ? [{
        accessorKey: 'boss2_due_date',
        header: `Срок: ${bossNames.boss2}`,
        size: 120,
        cell: ({ row }) => <DateBadge date={row.original.boss2_due_date} />,
      }] : []),
      ...(bossNames.boss3 ? [{
        accessorKey: 'boss3_due_date',
        header: `Срок: ${bossNames.boss3}`,
        size: 120,
        cell: ({ row }) => <DateBadge date={row.original.boss3_due_date} />,
      }] : []),
      {
        id: 'child_table',
        header: 'Исполнители',
        size: 240,
        cell: ({ row }) => (
          <table className="w-full table-fixed border-collapse text-[11px]">
            <thead>
              <tr className="text-gray-500">
                <th className="text-left">ФИО</th>
                <th className="text-left">Срок</th>
                <th className="text-left">Закрыто</th>
              </tr>
            </thead>
            <tbody>
              {row.original._children.length === 0 ? (
                <tr><td colSpan={3} className="text-gray-400 italic">нет</td></tr>
              ) : (
                row.original._children.map((child, idx) => (
                  <tr key={idx}>
                    <td className="w-1/3 pr-1 whitespace-nowrap">{child.person}</td>
                    <td className="w-1/3 pr-1"><DateBadge date={child.due_date} /></td>
                    <td className="w-1/3 text-gray-500">{child.closed_date || '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )
      }
    ];
    return base;
  }, [bossNames]);

  const table = useReactTable({
    data: flatData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel()
  });

  const parentRef = useRef(null);
  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 70,
    overscan: 10,
    observeElementResize: true,
  });

  const virtualRows = rowVirtualizer.getVirtualItems();
  const totalSize = rowVirtualizer.getTotalSize();

  return (
    <div ref={parentRef} className="overflow-auto h-[calc(100vh-10rem)] border rounded">
      {/* Заголовки */}
      <table className="min-w-full table-fixed text-sm">
        <colgroup>
          {table.getAllLeafColumns().map(col => (
            <col key={col.id} style={{ width: col.columnDef.size }} />
          ))}
        </colgroup>
        <thead className="sticky top-0 bg-white z-10 shadow-sm">
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => (
                <th
                  key={header.id}
                  className="px-3 py-2 text-left bg-gray-100 border-b border-gray-300 text-xs font-medium"
                >
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
      </table>

      {/* Виртуализированные строки */}
      <div style={{ height: `${totalSize}px`, position: 'relative' }}>
        {virtualRows.map(virtualRow => {
          const row = table.getRowModel().rows[virtualRow.index];
          return (
            <div
              key={row.id}
              ref={rowVirtualizer.measureElement}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualRow.start}px)`
              }}
              className="border-b border-gray-200"
            >
              <table className="min-w-full table-fixed text-sm">
                <colgroup>
                  {table.getAllLeafColumns().map(col => (
                    <col key={col.id} style={{ width: col.columnDef.size }} />
                  ))}
                </colgroup>
                <tbody>
                  <tr>
                    {row.getVisibleCells().map(cell => (
                      <td
                        key={cell.id}
                        className="px-3 py-2 align-top text-xs"
                      >
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default NestedVirtualizedTable;