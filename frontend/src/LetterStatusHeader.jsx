import React from "react";


const toArray = (maybeArray) => Array.isArray(maybeArray) ? maybeArray : [];


const statusDefs = {
    'unassigned': {
    
    label: 'Не расписано',
    condition: (row) => !row.children_controls
  },
    'not_prepared': {
    
    label: 'Не подготовлен',
    condition: (row) => !row.s_dgi_number && !row.s_started_at && row.children_controls
  },
    'prepared': {
    
    label: 'Подготовлен',
    condition: (row) => !!row.s_dgi_number && !row.s_started_at
  },
    'in_approval': {
    label: 'Идет согласование',
    condition: (row) => {
if (!row) return false;
      const struct = toArray(row?.s_structure);
      return (
        !!row.s_started_at &&
        !struct.some(s => s.status === 'На подписании') &&
        !struct.some(s => s.status === 'Подписан') &&
        !row.s_registered_sedo_id
      );
    }
  },
    'on_signing':  {

    label: 'На подписании',
    condition: (row) => {
      const struct = toArray(row?.s_structure);
      return struct.some(s => s.status === 'На подписании');
    }
  },
    'on_registration': {

    label: 'На регистрации',
    condition: (row) => {
      const struct = toArray(row?.s_structure);
      return struct.some(s => s.status === 'Подписан');
    }
  },
    'registered': {

    label: 'Зарегистрирован',
    condition: (row) => !!row.s_registered_sedo_id
  }
};



export const LetterStatusHeader = ({ allData, onFilterChange, activeStatus }) => {
  const counts = Object.fromEntries(
    Object.entries(statusDefs).map(([key, def]) => [
      key,
      new Set(allData.filter(def.condition).map(item => item.res_id)).size,
    ])
  );
  // console.log(allData)
  return (
    <div className="bg-gray-100 rounded-xl items-center text-xs">
      <div className="gap-2 flex-wrap bg-gray-100 p-1 rounded-xl items-center text-center text-sm" >Этапы работы</div>
    <div className="flex gap-2 flex-wrap bg-gray-100 p-1 rounded-xl items-center text-xs">
      <button
        onClick={() => onFilterChange([])}
        className={`px-1 py-1 rounded-md border ${
          activeStatus.length === 0
            ? "bg-blue-600 text-white"
            : "bg-white text-gray-800"
        }`}
      >
        Все ({new Set(allData.map(item => item.res_id)).size})
      </button>
      {Object.entries(statusDefs).map(([key, def]) => (
        <button
          key={key}
          onClick={() => {
            const newSet = activeStatus.includes(key)
              ? activeStatus.filter((k) => k !== key)
              : [...activeStatus, key];
            onFilterChange(newSet);
          }}
          className={`px-1 py-1 rounded-md border ${
            activeStatus.includes(key)
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800"
          }`}
        >
          {def.label} ({counts[key]})
        </button>
      ))}
    </div>
    </div>
  );
};