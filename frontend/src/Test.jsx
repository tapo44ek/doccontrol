import {
  useReactTable,
  flexRender,
  getCoreRowModel,
  getSortedRowModel
} from '@tanstack/react-table';
import { useState, useMemo, useEffect } from 'react';
import { parseISO, format, isValid } from 'date-fns';
import { ru } from 'date-fns/locale';

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

const processData = (data) => {
  return data.flatMap(item => {
    const children = parseChildren(item.children_controls);
    return children.length > 0
      ? children.map((child, idx) => ({
          ...item,
          ...child,
          _original: item,
          _isFirst: idx === 0,
          _groupSize: children.length
        }))
      : [{ ...item, _isFirst: true, _groupSize: 1 }];
  });
};

const filterByPerson = (data, selectedPerson) => {
  if (!selectedPerson) return data;
  return data.filter(item => {
    try {
      const children = parseChildren(item.children_controls);
      return children.some(child => child.person === selectedPerson);
    } catch (e) {
      console.error('Filter error:', e);
      return false;
    }
  });
};

const DateBadge = ({ date }) => {
  if (!date || typeof date !== 'string') return null;

  let parsed = parseISO(date.trim());

  if (!isValid(parsed)) {
    const match = date.trim().match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (match) {
      const [, y, m, d] = match.map(Number);
      parsed = new Date(y, m - 1, d);
    }
  }

  if (!isValid(parsed)) {
    console.error('DateBadge: Invalid date after all parsing attempts:', date);
    return null;
  }

  const today = new Date();
  const diff = (parsed.setHours(0, 0, 0, 0) - today.setHours(0, 0, 0, 0)) / (1000 * 60 * 60 * 24);

  let badgeColor = 'bg-green-100 text-green-800';
  if (diff < 0) badgeColor = 'bg-red-100 text-red-800';
  else if (diff <= 3) badgeColor = 'bg-yellow-100 text-yellow-800';

  const formatted = format(parsed, 'dd.MM.yyyy', { locale: ru });

  return (
    <span className={`inline-block px-2 py-0.5 text-xs font-semibold rounded-full ${badgeColor}`}>
      {formatted}
    </span>
  );
};

export default function ParentChildTable({ data, id }) {
  const [sorting, setSorting] = useState([]);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [noDueData, setNoDueData] = useState([]);
  const [showNoDue, setShowNoDue] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [bossNames, setBossNames] = useState({ boss1: null, boss2: null, boss3: null });

  useEffect(() => {
    const loadBossNames = async () => {
      try {
        const res = await fetch('http://10.9.96.160:5152/doccontrol/boss_names', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: id }),
        });
        const data = await res.json();
        setBossNames(data); // { boss1: "Иванов", boss2: null, boss3: "Петрова" }
      } catch (e) {
        console.error('Ошибка при получении имён начальников:', e);
      }
    };

    loadBossNames();
  }, [id]);

  const handleCheckboxToggle = async () => {
    const next = !showNoDue;
    setShowNoDue(next); // галка ставится сразу
  
    if (next && noDueData.length === 0) {
      setIsLoading(true);
      try {
        const res = await fetch('http://10.9.96.160:5152/doccontrol/user_wo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: id }),
        });
  
        if (!res.ok) throw new Error('Ошибка при получении данных без срока');
        const newData = await res.json();
        setNoDueData(newData);
      } catch (err) {
        console.error('Ошибка загрузки без срока:', err);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const tableData = useMemo(() => {
    if (showNoDue) {
      return [...data, ...noDueData].filter(
        (item, index, self) => index === self.findIndex(el => el.res_id === item.res_id)
      );
    }
    return data;
  }, [showNoDue, data, noDueData]);

  const flatData = useMemo(() => processData(tableData), [tableData]);

  const filteredData = useMemo(() => {
    return selectedPerson ? filterByPerson(flatData, selectedPerson) : flatData;
  }, [flatData, selectedPerson]);

  const personOptions = useMemo(() => {
    const persons = new Set();
    tableData.forEach(item => {
      const children = parseChildren(item.children_controls);
      children.forEach(child => {
        if (child.person) persons.add(child.person);
      });
    });
    return Array.from(persons).sort();
  }, [tableData]);

  const columns = useMemo(() => {
    const base = [
      {
        accessorKey: 'dgi_number',
        enableSorting: true,
        header: '№ ДГИ',
        cell: ({ row }) =>
          row.original._isFirst && (
            <td rowSpan={row.original._groupSize} className="px-4 py-3 w-[200px] border-b border-gray-200">
              <a
                href={`https://mosedo.mos.ru/document.card.php?id=${row.original.sedo_id}`}
                className="text-blue-600 underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                {row.getValue('dgi_number')}
              </a>
            </td>
          ),
        size: 100,
      },
      {
        accessorKey: 'date',
        enableSorting: true,
        header: 'Дата',
        cell: ({ row }) =>
          row.original._isFirst && (
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200">
              {new Date(row.getValue('date')).toLocaleDateString()}
            </td>
          ),
        size: 100,
      },
      {
        accessorKey: 'description',
        enableSorting: true,
        header: 'Содержание',
        cell: ({ row }) =>
          row.original._isFirst && (
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200">
              {row.getValue('description')}
            </td>
          ),
        size: 600,
      },
      {
        accessorKey: 'executor_due_date',
        enableSorting: true,
        header: 'Срок исполнения',
        cell: ({ row }) =>
          row.original._isFirst && (
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200">
              <DateBadge date={row.getValue('executor_due_date')} />
            </td>
          ),
        size: 100,
      }
    ];
  
    if (bossNames.boss1) {
      base.push({
        accessorKey: 'boss_due_date',
        enableSorting: true,
        header: `Срок: ${bossNames.boss1}`,
        cell: ({ row }) =>
          row.original._isFirst && (
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200">
              <DateBadge date={row.getValue('boss_due_date')} />
            </td>
          ),
        size: 100,
      });
    }
  
    if (bossNames.boss2) {
      base.push({
        accessorKey: 'boss2_due_date',
        enableSorting: true,
        header: `Срок: ${bossNames.boss2}`,
        cell: ({ row }) =>
          row.original._isFirst && (
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200">
              <DateBadge date={row.getValue('boss2_due_date')} />
            </td>
          ),
        size: 100,
      });
    }
  
    if (bossNames.boss3) {
      base.push({
        accessorKey: 'boss3_due_date',
        enableSorting: true,
        header: `Срок: ${bossNames.boss3}`,
        cell: ({ row }) =>
          row.original._isFirst && (
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200">
              <DateBadge date={row.getValue('boss3_due_date')} />
            </td>
          ),
        size: 100,
      });
    }
  
    base.push(
      {
        accessorKey: 'person',
        enableSorting: false,
        header: 'Исполнитель',
        cell: ({ row }) => (
          <td className="px-4 py-3 border-b border-gray-200">{row.getValue('person')}</td>
        ),
        size: 150,
      },
      {
        accessorKey: 'due_date',
        enableSorting: false,
        header: 'Срок',
        cell: ({ row }) => (
          <td className="px-4 py-3 border-b border-gray-200">{row.getValue('due_date')}</td>
        ),
        size: 100,
      },
      {
        accessorKey: 'closed_date',
        enableSorting: false,
        header: 'Дата закрытия',
        cell: ({ row }) => (
          <td className="px-4 py-3 border-b border-gray-200">{row.getValue('closed_date')}</td>
        ),
        size: 100,
      }
    );
  
    return base;
  }, [bossNames]);

  const table = useReactTable({
    data: filteredData,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    debugTable: false,
  });

  return (
    <div className="relative flex flex-col h-[calc(100vh-3.5rem)] bg-gray-50 w-full p-4">
      <div className="flex items-center gap-4 mb-4">
        <select
          value={selectedPerson || ''}
          onChange={(e) => setSelectedPerson(e.target.value || null)}
          className="block w-fit rounded-md border border-gray-300 bg-white px-4 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Все исполнители</option>
          {personOptions.map(person => (
            <option key={person} value={person}>{person}</option>
          ))}
        </select>

        <label className="inline-flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={showNoDue}
            onChange={handleCheckboxToggle}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
          />
          Показать без срока
        </label>
      </div>

      <div className="overflow-auto rounded-lg border border-gray-300 shadow-sm h-full scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100">
        <table className="min-w-full text-sm text-left bg-white border-separate border-spacing-0">
          <thead className="bg-white sticky top-0 z-10 shadow-sm">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id} className="bg-gray-100 border-b text-gray-700">
                {headerGroup.headers.map(header => {
                  const isSortable = header.column.getCanSort();
                  return (
                    <th
                      key={header.id}
                      onClick={isSortable ? header.column.getToggleSortingHandler() : undefined}
                      className={`px-4 py-3 border-b border-gray-300 text-sm font-semibold ${
                        isSortable ? 'cursor-pointer hover:bg-gray-100' : ''
                      }`}
                      style={{ width: `${header.column.columnDef.size}px` }}
                    >
                      <div className="flex items-center gap-1">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {isSortable && header.column.getIsSorted() && (
                          <span>{header.column.getIsSorted() === 'asc' ? '▲' : '▼'}</span>
                        )}
                      </div>
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map(row => (
              <tr key={row.id} className="bg-gray-50 border-b hover:bg-gray-100 transition-colors">
                {row.getVisibleCells().map(cell =>
                  flexRender(cell.column.columnDef.cell, cell.getContext())
                )}
              </tr>
            ))}
          </tbody>
        </table>
        {isLoading && (
  <div className="absolute inset-0 bg-white/60 z-20 flex items-center justify-center text-lg font-medium text-gray-700">
    Загрузка…
  </div>
)}
      </div>
    </div>
  );
}