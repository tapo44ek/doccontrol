import {
  useReactTable,
  flexRender,
  getCoreRowModel,
  getSortedRowModel
} from '@tanstack/react-table';
import { useState, useMemo, useEffect } from 'react';
import { parseISO, format, isValid } from 'date-fns';
import { ru } from 'date-fns/locale';
import { RotateCcw } from 'lucide-react';
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


export default function ParentChildTable({ data }) {
  const [sorting, setSorting] = useState([]);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [noDueData, setNoDueData] = useState([]);
  const [showNoDue, setShowNoDue] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [bossNames, setBossNames] = useState({ boss1: null, boss2: null, boss3: null });
  const [selected, setSelected] = useState(new Set());
  const [isBulkUpdating, setIsBulkUpdating] = useState(false);
  const [dueFilter, setDueFilter] = useState(new Set());
  const clearDueFilter = () => setDueFilter(new Set());

  const handleClearAllFilters = () => {
  clearDueFilter();           // очищает dueFilter
  setSelectedPerson(null);    // сбрасывает выбранного исполнителя
  setShowNoDue(false);        // сбрасывает галочку "показать без срока"
};

  const toggleSelect = (res_id) => {
    setSelected(prev => {
      const next = new Set(prev);
      next.has(res_id) ? next.delete(res_id) : next.add(res_id);
      return next;
    });
  };

  // const handleUpdate = (res_id) => {
  //   alert(`Обновление письма с res_id = ${res_id}`);
  // };

  // const handleBulkUpdate = () => {
  //   alert(`Обновление писем: ${Array.from(selected).join(', ')}`);
  // };


  useEffect(() => {
    const loadBossNames = async () => {
      try {
        const res = await fetch(`${backendUrl}/doccontrol/boss_names`, {
          method: 'GET',
          credentials: "include",
        });
        const data = await res.json();
        setBossNames(data); // { boss1: "Иванов", boss2: null, boss3: "Петрова" }
      } catch (e) {
        console.error('Ошибка при получении имён начальников:', e);
      }
    };

    loadBossNames();
  }, []);

  const handleCheckboxToggle = async () => {
    const next = !showNoDue;
    setShowNoDue(next); // галка ставится сразу
  
    if (next && noDueData.length === 0) {
      setIsLoading(true);
      try {
        const res = await fetch(`${backendUrl}/doccontrol/user_wo`, {
          method: 'GET',
          credentials: "include"
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

const [tableData, setTableData] = useState([...data]);

useEffect(() => {
  setTableData([...data]);
}, [data]);

useEffect(() => {
  if (showNoDue && noDueData.length > 0) {
    setTableData(prev => {
      const existing = new Set(prev.map(el => el.res_id));
      const toAdd = noDueData.filter(el => !existing.has(el.res_id));
      return [...prev, ...toAdd];
    });
  } else {
    // фильтруем те, у кого нет executor_due_date (то есть "без срока")
    setTableData(prev => prev.filter(el => el.executor_due_date));
  }
}, [showNoDue, noDueData]);


// 3. Универсальный handler обновления
const handleUpdateMany = async (doclist) => {
  if (!doclist || doclist.length === 0) return;

  const isBulk = doclist.length > 0;
  if (isBulk) setIsBulkUpdating(true);
  else setUpdatingDocs(prev => [...prev, doclist[0]]); // << заменить Set на Array

  try {
    const res = await fetch(`${backendUrl}/update/docs_by_id`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doclist }),
      credentials: "include",
    });

    if (!res.ok) throw new Error('Ошибка обновления');

    const updatedDocs = await res.json();
    const map = new Map(updatedDocs.map(doc => [doc.sedo_id, doc]));
    setTableData(prev =>
      prev.map(item => map.has(item.sedo_id) ? map.get(item.sedo_id) : item)
    );
    setSelected(new Set());
  } catch (e) {
    console.error('Ошибка при обновлении:', e);
  } finally {
    if (isBulk) {
      setIsBulkUpdating(false);
    } else {
      setUpdatingDocs(prev => prev.filter(id => id !== doclist[0]));
    }
  }
};



const handleBulkUpdate = () => {
  const doclist = Array.from(selected);
  handleUpdateMany(doclist);
};

const handleUpdate = (sedo_id) => {
  handleUpdateMany([sedo_id]);
};

const toggleDueFilter = (key) => {
  setDueFilter(prev => {
    const next = new Set(prev);
    next.has(key) ? next.delete(key) : next.add(key);
    return next;
  });
};

const fullData = useMemo(() => {
  const base = [...tableData];
  if (showNoDue && noDueData.length > 0) {
    const baseIds = new Set(base.map(el => el.res_id));
    const toAdd = noDueData.filter(el => !baseIds.has(el.res_id));
    return [...base, ...toAdd];
  }
  return base;
}, [tableData, noDueData, showNoDue]);

const flatData = useMemo(() => processData(fullData), [fullData]);

const filteredData = useMemo(() => {
  let result = [...flatData];

  if (selectedPerson) {
    result = filterByPerson(result, selectedPerson);
  }

  if (dueFilter.size > 0) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    result = result.filter(row => {
      const rawDue = row.executor_due_date;

      const children = parseChildren(row.children_controls);
      if ((!row.children_controls || children.length === 0) && dueFilter.has('none')) {
        return true;
      }

      if (!rawDue) return false;

      const date = new Date(rawDue);
      date.setHours(0, 0, 0, 0);

      return (
        (dueFilter.has('today') && date.getTime() === today.getTime()) ||
        (dueFilter.has('tomorrow') && date.getTime() === tomorrow.getTime())
      );
    });
  }

  return result;
}, [flatData, selectedPerson, dueFilter]);

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
    className="text-blue-600 underline block"
    target="_blank"
    rel="noopener noreferrer"
  >
    {row.getValue('dgi_number')}
  </a>
  <div className="flex items-center gap-1 mt-1">
<button
  onClick={() => handleUpdate(row.original.sedo_id)}
  className={`${
    !handleBulkUpdate
      ? 'text-gray-400 cursor-not-allowed'
      : 'text-blue-600 hover:text-blue-800'
  }`}
  title="Обновить"
  disabled={!handleBulkUpdate}
>
  <RotateCcw className="w-4 h-4" />
</button>
    <span className="text-xs text-gray-500">
      обн: {format(parseISO(row.original.updated_at), 'dd.MM.yyyy HH:mm')}
    </span>
  </div>
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
    getSortedRowModel: getSortedRowModel()
  });

  return (
    <div className="relative flex flex-col h-[calc(100vh-3.5rem)] bg-gray-50 w-full p-4">
<div className="flex items-center justify-between mb-4">
  <div className="flex items-center gap-6 flex-wrap">

    {/* Блок "Исполнители" */}
    <div className="flex flex-col items-center">
      <span className="text-sm text-gray-500 mb-1 text-center">Исполнители</span>
      <div className="flex gap-4 items-center">
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
      </div>
    </div>

    {/* Вертикальная линия */}
    <div className="w-px bg-gray-300 mx-1 self-stretch" />

    {/* Блок "Показать без срока" */}
    <div className="flex flex-col items-center">
      <span className="text-sm text-gray-500 mb-1 text-center">Без срока</span>
      <div className="flex gap-4 items-center py-2">
        <label className="inline-flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={showNoDue}
            onChange={handleCheckboxToggle}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
          />
          Показать
        </label>
      </div>
    </div>

    
    
    {/* Вертикальная линия */}
    <div className="w-px bg-gray-300 mx-1 self-stretch" />

    {/* Блок фильтров */}
    <div className="flex items-start gap-6 flex-wrap">

      {/* Сроки */}
      <div className="flex flex-col items-center">
        <span className="text-sm text-gray-500 mb-1 text-center">Сроки</span>
        <div className="flex gap-2 flex-wrap">
          {[
            { key: 'today', label: 'Сегодня' },
            { key: 'tomorrow', label: 'Завтра' },
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => toggleDueFilter(key)}
              className={`px-2 py-1 rounded text-sm border ${
                dueFilter.has(key) ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Вертикальная линия */}
    <div className="w-px bg-gray-300 mx-1 self-stretch" />

      {/* Роспись */}
      <div className="flex flex-col items-center">
        <span className="text-sm text-gray-500 mb-1 text-center">Роспись</span>
        <div className="flex gap-2 flex-wrap">
          <button
            key="none"
            onClick={() => toggleDueFilter('none')}
            className={`px-2 py-1 rounded text-sm border ${
              dueFilter.has('none') ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'
            }`}
          >
            Не расписано
          </button>
        </div>
      </div>

      {/* Вертикальная линия */}
    <div className="w-px bg-gray-300 mx-1 self-stretch" />

      {/* Сброс фильтров */}
      <div className="flex flex-col items-center">
        <span className="text-sm text-gray-500 mb-1 invisible">Сброс</span>
        <button
          onClick={handleClearAllFilters}
          className="px-2 py-1 rounded text-sm border bg-white text-gray-700"
        >
          Сбросить фильтры
        </button>
      </div>
    </div>
  </div>

  {/* Кнопка массового обновления */}
  <button
    disabled={selected.size === 0 || isBulkUpdating}
    onClick={handleBulkUpdate}
    className={`px-4 py-2 text-sm rounded ${
      selected.size === 0 || isBulkUpdating
        ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
        : 'bg-blue-600 text-white'
    }`}
  >
    {isBulkUpdating ? 'Обновляется…' : 'Обновить выбранное'}
  </button>
</div>
      <div className="text-sm text-gray-600 py-2">
        Всего: <span className="font-semibold">{filteredData.length}</span>
      </div>

      <div className="overflow-auto rounded-lg border border-gray-300 shadow-sm h-full scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100">
        <table className="min-w-full text-sm text-left bg-white border-separate border-spacing-0">
          <thead className="bg-white sticky top-0 z-10 shadow-sm">
            
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id} className="bg-gray-100 border-b text-gray-700">
                <th></th>
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
  {table.getRowModel().rows.map(row => {
    const id = Number(row.original.sedo_id);
    const isFirst = row.original._isFirst;
    const span = row.original._groupSize;

    return (
      <tr
        key={row.id}
        // className="bg-gray-50 border-b hover:bg-gray-100 transition-colors"
      >
        {isFirst && (
          <td rowSpan={span} className="px-2 py-3 w-6 border-b border-gray-200">
            <input
              type="checkbox"
              checked={selected.has(id)}
              onChange={() => toggleSelect(id)}
              className="h-4 w-4 text-gray-600 border-gray-300 rounded appearance-auto"
            />
          </td>
        )}

        {row.getVisibleCells().map(cell =>
          flexRender(cell.column.columnDef.cell, cell.getContext())
        )}
      </tr>
    );
  })}
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