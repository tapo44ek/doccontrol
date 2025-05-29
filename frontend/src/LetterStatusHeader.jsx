import React from "react";

const statusDefs = [
  { key: 'unassigned', label: 'Не расписано', condition: (row) => !row.children_controls },
  { key: 'prepared', label: 'Подготовлен', condition: (row) => !!row.s_dgi_number && !row.s_started_at },
  { key: 'in_approval', label: 'Идет согласование', condition: (row) => !!row.s_started_at && Array.isArray(row.s_structure) && !row.s_structure.some(s => s.status === 'На подписании') && !row.s_structure.some(s => s.status === 'Подписан') && !row.s_registered_sedo_id },
  { key: 'on_signing', label: 'На подписании', condition: (row) =>
      Array.isArray(row.s_structure) && row.s_structure.some(s => s.status === 'На подписании')
  },
  { key: 'on_registration', label: 'На регистрации', condition: (row) =>
      Array.isArray(row.s_structure) && row.s_structure.some(s => s.status === 'Подписан')
  },
  { key: 'registered', label: 'Зарегистрирован', condition: (row) => !!row.s_registered_sedo_id },
];

export const LetterStatusHeader = ({ data, onFilterChange, activeStatus }) => {
  const counts = Object.fromEntries(
    statusDefs.map(({ key, condition }) => [key, data.filter(condition).length])
  );

  return (
    <div className="flex gap-3 flex-wrap bg-gray-100 p-2 rounded-xl text-sm">
      {statusDefs.map(({ key, label }) => (
        <button
          key={key}
          onClick={() => onFilterChange(key)}
          className={`px-3 py-1 rounded-md border ${
            activeStatus === key
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-800"
          }`}
        >
          {label} ({counts[key]})
        </button>
      ))}
      <button
        onClick={() => onFilterChange(null)}
        className={`px-3 py-1 rounded-md border ${
          activeStatus === null
            ? "bg-blue-600 text-white"
            : "bg-white text-gray-800"
        }`}
      >
        Все ({data.length})
      </button>
    </div>
  );
};