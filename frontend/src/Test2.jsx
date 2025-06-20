import { useState, useMemo, useEffect, useRef, useCallback, useReducer } from 'react';
import {
  useReactTable,
  flexRender,
  getCoreRowModel,
  getSortedRowModel
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';

import { parseISO, format, isValid, parse } from 'date-fns';
import { ru } from 'date-fns/locale';

import { RotateCcw, ChevronUp, ChevronDown, GripHorizontal } from 'lucide-react';

import { LetterStatusHeader } from './LetterStatusHeader';

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

const toArray = (maybeArray) => Array.isArray(maybeArray) ? maybeArray : [];

const statusDefs = {
  unassigned: (row) => !row.children_controls,
  not_prepared: (row) => !row.s_dgi_number && !row.s_started_at && !!row.children_controls,
  prepared: (row) => !!row.s_dgi_number && !row.s_started_at,
  in_approval: (row) => {
    const struct = toArray(row?.s_structure);
    return (
        !!row.s_started_at &&
        !struct.some(s => s.status === 'На подписании') &&
        !struct.some(s => s.status === 'Подписан') &&
        !row.s_registered_sedo_id
    );
    },
  on_signing: (row) => {
      const struct = toArray(row?.s_structure);
      return struct.some(s => s.status === 'На подписании');
    },
  on_registration: (row) => {const struct = toArray(row?.s_structure);
      return struct.some(s => s.status === 'Подписан');},
  registered: (row) => !!row.s_registered_sedo_id,
};


const processData = (data) => {
  return data.flatMap(item => {
    const children = parseChildren(item.children_controls);

    if (children.length === 0) {
      return [{ ...item, _isFirst: true, _groupSize: 1 }];
    }

    const groupedByPerson = new Map();

    for (const child of children) {
      const person = child.person || '___null___'; // подстраховка
      const due = child.due_date ? new Date(child.due_date) : null;
      const closed = child.closed_date;

      if (!groupedByPerson.has(person)) {
        groupedByPerson.set(person, []);
      }

      groupedByPerson.get(person).push({ ...child, _parsedDue: due, _isClosed: !!closed });
    }

    const selectedChildren = [];

    for (const [person, items] of groupedByPerson.entries()) {
      const openItems = items.filter(i => !i._isClosed);

      if (openItems.length > 0) {
        // выбрать ближайшую к сегодняшнему дню
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const closest = openItems.reduce((a, b) => {
          const diffA = Math.abs((a._parsedDue?.getTime() ?? Infinity) - today.getTime());
          const diffB = Math.abs((b._parsedDue?.getTime() ?? Infinity) - today.getTime());
          return diffA < diffB ? a : b;
        });

        selectedChildren.push(closest);
      } else {
        // только закрытые — оставить одну
        selectedChildren.push(items[0]);
      }
    }

    return selectedChildren.map((child, idx) => ({
      ...item,
      ...child,
      _original: item,
      _isFirst: idx === 0,
      _groupSize: selectedChildren.length
    }));
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

  let parsed = null;
  const trimmed = date.trim();

  // Пробуем ISO (2024-05-21)
  parsed = parseISO(trimmed);

  // Если не сработало — пробуем вручную несколько форматов
  if (!isValid(parsed)) {
    const formats = ['dd.MM.yyyy', 'dd-MM-yyyy', 'yyyy-MM-dd'];

    for (const fmt of formats) {
      parsed = parse(trimmed, fmt, new Date());
      if (isValid(parsed)) break;
    }
  }

  if (!isValid(parsed)) {
    console.error('DateBadge: нераспознанная дата:', date);
    return null;
  }

  // Сравнение с сегодняшним днём
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  parsed.setHours(0, 0, 0, 0);

  const diff = (parsed - today) / (1000 * 60 * 60 * 24);

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
  const clearDueFilter = () => setDueFilter(new Set());

  const [searchQuery, setSearchQuery] = useState('');
  const [sorting, setSorting] = useState([]);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [bossNames, setBossNames] = useState({ boss1: null, boss2: null, boss3: null });
  const [selected, setSelected] = useState(new Set());
  const [isBulkUpdating, setIsBulkUpdating] = useState(false);
  const [dueFilter, setDueFilter] = useState(new Set());
  const [showFilters, setShowFilters] = useState(true);
  const [statusFilter, setStatusFilter] = useState([]);
  // const [noDueData, setNoDueData] = useState([]);
  const [showNoDue, setShowNoDue] = useState(true);
// const [tableData, setTableData] = useState([]);

const handleClearAllFilters = () => {
  setDueFilter(new Set());
  setSelectedPerson(null);
  setShowNoDue(false);
};

const [tableData, setTableData] = useState([]);

const rawDataWithNoDue = useMemo(() => {
  const withDue = [];
  const noDue = [];

  for (const item of data) {
    let executorDue = item.executor_due_date;
    let generated = false;

    if (!executorDue) {
      const children = parseChildren(item.children_controls);

const dueDates = children
  .filter(child => child.due_date && !child.closed_date) // ← сначала фильтруем
  .map(child => new Date(child.due_date)); 

      if (dueDates.length > 0) {
        const latest = new Date(Math.max(...dueDates.map(d => d.getTime())));
        executorDue = latest.toISOString().split("T")[0];
        generated = true;
      }
    }

    const updatedItem = {
      ...item,
      executor_due_date: executorDue,
      executor_due_generated: generated,
    };

    if (executorDue) {
      withDue.push(updatedItem);
    } else {
      noDue.push(updatedItem);
    }
  }

  return {
    withDue,
    noDue,
    combined: [...withDue, ...noDue],
  };
}, [data]);

useEffect(() => {
  let combined = [...rawDataWithNoDue.withDue];

  if (showNoDue) {
    const ids = new Set(combined.map(el => el.res_id));
    const additional = rawDataWithNoDue.noDue.filter(el => !ids.has(el.res_id));
    combined = [...combined, ...additional];
  }

  if (statusFilter.length > 0) {
    combined = combined.filter(row =>
      statusFilter.some(key => statusDefs[key](row))
    );
  }

  setTableData(combined);
}, [rawDataWithNoDue, showNoDue, statusFilter]);



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

const handleCheckboxToggle = () => {
  setShowNoDue(prev => !prev);
};

// const [tableData, setTableData] = useState([...data]);

// useEffect(() => {
//   setTableData([...data]);
// }, [data]);

// useEffect(() => {
//   if (showNoDue && noDueData.length > 0) {
//     setTableData(prev => {
//       const existing = new Set(prev.map(el => el.res_id));
//       const toAdd = noDueData.filter(el => !existing.has(el.res_id));
//       return [...prev, ...toAdd];
//     });
//   } else {
//     // фильтруем те, у кого нет executor_due_date (то есть "без срока")
//     setTableData(prev => prev.filter(el => el.executor_due_date));
//   }
// }, [showNoDue, noDueData]);


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

// const [, forceUpdate] = useReducer(x => x + 1, 0);

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

// const fullData = useMemo(() => {
//   const base = [...tableData];
//   if (showNoDue && noDueData.length > 0) {
//     const baseIds = new Set(base.map(el => el.res_id));
//     const toAdd = noDueData.filter(el => !baseIds.has(el.res_id));
//     return [...base, ...toAdd];
//   }
//   return base;
// }, [tableData, noDueData, showNoDue]);

const flatData = useMemo(() => processData(tableData), [tableData]);

// const flatUnfilteredData = useMemo(() => processData(rawDataWithNoDue), [rawDataWithNoDue]);

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
        (dueFilter.has('ago') && date.getTime() < today.getTime()) ||
        (dueFilter.has('today') && date.getTime() === today.getTime()) ||
        (dueFilter.has('tomorrow') && date.getTime() === tomorrow.getTime()) ||
        (dueFilter.has('other') && date.getTime() > tomorrow.getTime())
      );
    });
  }
  if (searchQuery.trim()) {
  result = result.filter(row =>
    String(row.dgi_number || '')
      .toLowerCase()
      .includes(searchQuery.trim().toLowerCase())
    );
  }

  return result;
}, [flatData, selectedPerson, dueFilter, selected, searchQuery]);

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
<td rowSpan={row.original._groupSize} className="px-4 py-3 w-[200px] border-b border-gray-200 text-xs">
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
  <RotateCcw className="w-3 h-3" />
</button>
    <span className="text-xs text-gray-500 text-[9px]">
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
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200 text-xs">
              {new Date(row.getValue('date')).toLocaleDateString()}
            </td>
          ),
        size: 100,
      },
{
  accessorKey: 'description',
  enableSorting: true,
  header: 'Содержание',
  cell: ({ row }) => {
    if (!row.original._isFirst) return null;

    const full = row.getValue('description') || '';
    const limit = 40;

    const [expanded, setExpanded] = useState(false);
    const short = full.slice(0, limit);

    return (
      <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b item-center border-gray-200 text-xs max-w-[350px]">
        {expanded || full.length <= limit ? full : `${short}... `}
        {full.length > limit && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-gray-600 hover:underline"
          >
            {expanded ? 'Скрыть' : <GripHorizontal />}
          </button>
        )}
      </td>
    );
  },
  size: 350,
},
      {
        accessorKey: 'executor_due_date',
        enableSorting: true,
        header: 'Срок исполнения',
cell: ({ row }) =>
  row.original._isFirst && (
    <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200 text-xs space-y-1">
      <DateBadge date={row.getValue('executor_due_date')} />
      {row.original.is_additional && (
        <div className="inline-block px-2 py-0.5 text-blue-600 bg-blue-100 rounded-full text-[10px] font-semibold">
          в плюсе
        </div>
      )}
      {row.original.executor_due_generated && (
  <div className="inline-block px-1 py-0.2 text-[6px] text-orange-800 bg-orange-100 rounded-full text-[10px] font-semibold">
    generated
  </div>
)}
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
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200 text-xs">
              <DateBadge date={row.getValue('boss_due_date')} />
            </td>
          ),
        size: 120,
      });
    }
  
    if (bossNames.boss2) {
      base.push({
        accessorKey: 'boss2_due_date',
        enableSorting: true,
        header: `Срок: ${bossNames.boss2}`,
        cell: ({ row }) =>
          row.original._isFirst && (
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200 text-xs">
              <DateBadge date={row.getValue('boss2_due_date')} />
            </td>
          ),
        size: 120,
      });
    }
  
    if (bossNames.boss3) {
      base.push({
        accessorKey: 'boss3_due_date',
        enableSorting: true,
        header: `Срок: ${bossNames.boss3}`,
        cell: ({ row }) =>
          row.original._isFirst && (
            <td rowSpan={row.original._groupSize} className="px-4 py-3 border-b border-gray-200 text-xs">
              <DateBadge date={row.getValue('boss3_due_date')} />
            </td>
          ),
        size: 200,
      });
    }

    base.push(
      {
        accessorKey: 's_dgi_number',
        enableSorting: true,
        header: 'согл',
        cell: ({ row }) =>
          row.original._isFirst && (
<td rowSpan={row.original._groupSize} className="px-4 py-3 w-[200px] border-b border-gray-200 text-xs">
  <a
    href={`https://mosedo.mos.ru/document.card.php?id=${row.original.s_sedo_id}`}
    className="text-blue-600 underline block"
    target="_blank"
    rel="noopener noreferrer"
  >
    {row.getValue('s_dgi_number')}
  </a>
  <div className="flex items-center gap-1 mt-1">
{/* <button
  onClick={() => handleUpdate(row.original.s_sedo_id)}
  className={`${
    !handleBulkUpdate
      ? 'text-gray-400 cursor-not-allowed'
      : 'text-blue-600 hover:text-blue-800'
  }`}
  title="Обновить"
  disabled={!handleBulkUpdate}
>
  <RotateCcw className="w-3 h-3" />
</button> */}
{row.original.s_dgi_number != null && !row.original.s_registered_sedo_id &&(
    <span className="text-xs text-gray-500 text-[9px]">
      запущен: {row.original.s_started_at
  ? format(parseISO(row.original.s_started_at), 'dd.MM.yyyy HH:mm')
  : '—'}
    </span>
)}
</div>
<div className="flex items-center gap-1 mt-1">

        {/* бейдж: зарегистрирован */}
        {row.original.s_registered_sedo_id && (
          <div>
          {/* <div className="inline-flex items-center gap-2">
            <span className="px-2 py-0.5 text-green-700 bg-green-100 rounded-full text-[10px] font-semibold">
              Зарегистрирован
            </span>
          </div> */}
          <div className="inline-flex items-center gap-2">
            <span className="px-2 py-0.5 text-green-700 bg-green-100 rounded-full text-[8px] font-semibold">
                <a
    href={`https://mosedo.mos.ru/document.card.php?id=${row.original.s_registered_sedo_id}`}
    className="text-blue-600 underline block"
    target="_blank"
    rel="noopener noreferrer"
  >
    рег: {row.original.s_registered_number}
  </a>
              {/* {row.original.s_registered_number} */}
            </span>
          </div>
          </div>
        )}
  </div>
</td>
          ),
        size: 100,
      }
    )
  
//     base.push(
//       {
//         accessorKey: 'person',
//         enableSorting: false,
//         header: 'Исполнитель',
//         cell: ({ row }) => (
//           <td className="px-4 py-3 border-b border-gray-200 text-xs">{row.getValue('person')}</td>
//         ),
//         size: 150,
//       },
// {
//   accessorKey: 'due_date',
//   enableSorting: false,
//   header: 'Срок',
//   cell: ({ row }) => {
//     const closed = row.getValue('closed_date');
//     const due = row.getValue('due_date');
//     return (
//       <td className="px-4 py-3 border-b border-gray-200 text-xs">
//         {!closed ? <DateBadge date={due} /> :  <span className={`inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-100 text-gray-800`}>
//       {due}
//     </span> || '-'}
//       </td>
//     );
//   },
//   size: 100,
// },
//       {
//         accessorKey: 'closed_date',
//         enableSorting: false,
//         header: 'Дата закрытия',
//         cell: ({ row }) => (
//           <td className="px-4 py-3 border-b border-gray-200 text-xs"><span className={`inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-100 text-gray-800`}>{row.getValue('closed_date')}</span></td>
//         ),
//         size: 100,
//       }
//     );

base.push({
  id: 'person_info',
  header: 'Исполнитель / Срок / Закрытие',
  enableSorting: false,
  cell: ({ row }) => {
    const person = row.original.person;
    const due = row.original.due_date;
    const closed = row.original.closed_date;

    return (
      <td className="px-4 py-3 border-b border-gray-200 text-xs space-y-1">
        <div>{person}</div>
        <div>
          {!closed ? (
            <DateBadge date={due} />
          ) : (
            <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
              {due || '-'}
            </span>
          )}
        </div>
        <div>
          {closed && (
            <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
              {closed || '-'}
            </span>
          )}
        </div>
      </td>
    );
  },
  size: 220,
});
  
    return base;
  }, [bossNames]);

  const table = useReactTable({
    data: filteredData,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });


  const parentRef = useRef(null);

  const rowVirtualizer = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: useCallback(() => 48, []), // базовая высота строки; подгоните при необходимости
    overscan: 20,
  });

  const virtualRows = rowVirtualizer.getVirtualItems();
  const paddingTop = virtualRows.length ? virtualRows[0].start : 0;
  const paddingBottom = virtualRows.length
    ? rowVirtualizer.getTotalSize() - virtualRows[virtualRows.length - 1].end
    : 0;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);

    const dueCounts = {
    all: 0,
    ago: 0,
    today: 0,
    tomorrow: 0,
    other: 0,
    };

    const seenSedoIds = new Set();

    for (const row of flatData) {
    const sedoId = row.sedo_id;
    if (sedoId == null || seenSedoIds.has(sedoId)) continue;

    seenSedoIds.add(sedoId);

    const rawDue = row.executor_due_date;
    if (!rawDue) continue;

    const date = new Date(rawDue);
    date.setHours(0, 0, 0, 0);
    dueCounts.all++;
    if (date < today) dueCounts.ago++;
    else if (date.getTime() === today.getTime()) dueCounts.today++;
    else if (date.getTime() === tomorrow.getTime()) dueCounts.tomorrow++;
    else if (date > tomorrow) dueCounts.other++;
    }

  return (
    <div className="relative flex flex-col h-[calc(100vh-3.5rem)] bg-gray-50 w-full p-4">

      <div className="mb-4">

  <div className="flex justify-between items-center">
    <button
      onClick={() => setShowFilters(prev => !prev)}
      className="flex items-center gap-1 text-sm text-blue-600 hover:underline"
    >
      {showFilters ? 'Скрыть фильтры' : 'Показать фильтры'}
      {showFilters ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
    </button>
  </div>

  {showFilters && (
    <div className="flex items-center justify-between mt-2 gap-6 flex-wrap">
      <div className="flex items-center gap-6 flex-wrap">

        {/* Блок "Исполнители" */}
        <div className="flex flex-col items-center">
          <span className="text-sm text-gray-500 mb-1 text-center text-xs">Исполнители</span>
          <div className="flex gap-2 items-center">
            <select
              value={selectedPerson || ''}
              onChange={(e) => setSelectedPerson(e.target.value || null)}
              className="block w-fit rounded-md border border-gray-300 bg-white px-4 py-2 text-xs shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Все исполнители</option>
              {personOptions.map(person => (
                <option key={person} value={person}>{person}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="w-px bg-gray-300 mx-1 self-stretch" />

        {/* Без срока */}
        <div className="flex flex-col items-center">
          <span className="text-sm text-gray-500 mb-1 text-center text-xs">Без срока</span>
          <div className="flex gap-1 items-center py-2">
            <label className="inline-flex items-center gap-1 text-xs">
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

        <div className="w-px bg-gray-300 mx-1 self-stretch" />

        {/* Сроки */}
        <div className="flex flex-col items-center">
          <span className="text-sm text-gray-500 mb-1 text-xs text-center">Сроки</span>
          <div className="flex gap-1 flex-wrap">

  <button
    key='all'
    className={`px-2 py-1 rounded text-xs border ${
      dueFilter.has('all') ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'
    }`}
  >
    Все ({dueCounts['all']})
  </button>
{[
  // { key: 'all', label: 'Все' },
  { key: 'ago', label: 'Просрочено' },  
  { key: 'today', label: 'Сегодня' },
  { key: 'tomorrow', label: 'Завтра' },
  { key: 'other', label: 'Потом' },
].map(({ key, label }) => (
  <button
    key={key}
    onClick={() => toggleDueFilter(key)}
    className={`px-2 py-1 rounded text-xs border ${
      dueFilter.has(key) ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'
    }`}
  >
    {label} ({dueCounts[key]})
  </button>
))}
          </div>
        </div>

        <div className="w-px bg-gray-300 mx-1 self-stretch" />

        {/* Роспись
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

        <div className="w-px bg-gray-300 mx-1 self-stretch" /> */}

        {/* Сброс */}
        <div className="flex flex-col items-center">
          <span className="text-sm text-gray-500 mb-1 invisible">Сброс</span>
          <button
            onClick={handleClearAllFilters}
            className="px-2 py-1 rounded text-xs border bg-white text-gray-700"
          >
            Сбросить фильтры
          </button>
        </div>
      </div>

      {/* Кнопка массового обновления */}
      <button
        disabled={selected.size === 0 || isBulkUpdating}
        onClick={handleBulkUpdate}
        className={`px-4 py-2 text-xs rounded ${
          selected.size === 0 || isBulkUpdating
            ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
            : 'bg-blue-600 text-white'
        }`}
      >
        {isBulkUpdating ? 'Обновляется…' : 'Обновить выбранное'}
      </button>
    </div>
  )}
</div>
        <div className="flex justify-center items-center">
<LetterStatusHeader
  allData={filteredData}
  activeStatus={statusFilter}
  onFilterChange={setStatusFilter}
/>
</div>

<div className="flex items-center justify-between py-1 text-sm w-full text-gray-600">
  <div className="flex flex-col items-start">
    <input
      type="text"
      value={searchQuery}
      onChange={(e) => setSearchQuery(e.target.value)}
      placeholder="Поиск № ДГИ ..."
      className="block w-[160px] rounded-md border border-gray-300 bg-white px-2 py-1 text-xs shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
    />
  </div>

  <div>
    Всего: <span className="font-semibold">
      {new Set(filteredData.filter(row => row.sedo_id != null).map(row => row.sedo_id)).size}
    </span>
  </div>
</div>
      <div
        ref={parentRef}
        className="overflow-auto rounded-lg border border-gray-300 shadow-sm h-full scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100"
      >
        <table className="min-w-full text-sm text-left bg-white border-separate border-spacing-0">

          <thead className="bg-white sticky top-0 z-10 shadow-sm">
            
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id} className="bg-gray-100 border-b text-gray-700">
                <th
                className='grid place-items-center h-16'>
                <input
                  type="checkbox"
                  checked={filteredData.length > 0 && filteredData.every(row => selected.has(Number(row.sedo_id)))}
                  onChange={(e) => {
                    if (e.target.checked) {
                      const newSelected = new Set(selected);
                      filteredData.forEach(row => newSelected.add(Number(row.sedo_id)));
                      setSelected(newSelected);
                      // forceUpdate();
                    } else {
                      const newSelected = new Set(selected);
                      filteredData.forEach(row => newSelected.delete(Number(row.sedo_id)));
                      setSelected(newSelected);
                      // forceUpdate();
                    }
                  }}
                  className="h-4 w-4 text-gray-600 border-gray-300 rounded appearance-auto"
                />
              </th>
                {headerGroup.headers.map(header => {
                  const isSortable = header.column.getCanSort();
                  return (
                    <th
                      key={header.id}
                      onClick={isSortable ? header.column.getToggleSortingHandler() : undefined}
                      className={`px-4 py-3 border-b border-gray-300 text-xs font-semibold ${
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
            {paddingTop > 0 && (
              <tr>
                <td style={{ height: `${paddingTop}px`, padding: 0 }} colSpan={1000} />
              </tr>
            )}

            {virtualRows.map((virtualRow) => {
              const row = table.getRowModel().rows[virtualRow.index];
              const id = Number(row.original.sedo_id);
              const isFirst = row.original._isFirst;
              const span = row.original._groupSize;

              return (
                <tr 
                key={row.id} 
                ref={rowVirtualizer.measureElement} 
                data-index={virtualRow.index} 
                className="bg-white border-b hover:bg-gray-50 transition-colors">
                  {isFirst && (
                    <td rowSpan={span} className="px-2 py-3 w-8 border-b items-center justify-center border-gray-200">
                      <input
                        type="checkbox"
                        checked={selected.has(id)}
                        onChange={() => toggleSelect(id)}
                        className="h-4 w-4 text-gray-600 border-gray-300 rounded appearance-auto"
                      />
                    </td>
                  )}

                  {row.getVisibleCells().map((cell) =>
                    flexRender(cell.column.columnDef.cell, cell.getContext())
                  )}
                </tr>
              );
            })}

            {paddingBottom > 0 && (
              <tr>
                <td style={{ height: `${paddingBottom}px`, padding: 0 }} colSpan={1000} />
              </tr>
            )}
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