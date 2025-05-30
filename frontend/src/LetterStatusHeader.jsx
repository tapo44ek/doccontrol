import React from "react";


const toArray = (maybeArray) => Array.isArray(maybeArray) ? maybeArray : [];


const statusDefs = {
    'unassigned': {
    
    label: 'Не расписано',
    condition: (row) => !row.children_controls
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
    Object.entries(statusDefs).map(([ key, def ]) => [key, allData.filter(def.condition).length])
  );

  return (
    <div className="flex gap-3 flex-wrap bg-gray-100 p-2 rounded-xl items-center text-sm">
        <button
            onClick={() => onFilterChange(null)}
            className={`px-3 py-1 rounded-md border ${
            activeStatus === null
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-800"
            }`}
        >
            Все ({allData.length})
        </button>
        {Object.entries(statusDefs).map(([ key, def ]) => (   
            <button
            key={key}
            onClick={() => onFilterChange(key)}
            className={`px-3 py-1 rounded-md border ${
                activeStatus === key
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-800"
            }`}
            >
            {def.label} ({counts[key]})
            </button>
        ))}

    </div>
  );
};