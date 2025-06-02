import { useEffect, useState, useImperativeHandle, forwardRef } from 'react';
import ParentChildTable from './Test2';
import NestedVirtualizedTable from './NestedVirtualizedTable';
import VirtualizedTableDivs from './VirtualizedTableDivs';
const backendUrl = import.meta.env.VITE_BACKEND_URL;

const TableContainer = forwardRef(({ onMinUpdatedAtChange }, ref) => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      // const payload = { user_id: id };

      const response = await fetch(`${backendUrl}/doccontrol/user`, {
        method: 'GET',
        credentials: "include",
      });

      if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);

      const responseData = await response.json();
      setData(responseData);

      const allDates = responseData
        .map(item => item.updated_at)
        .filter(Boolean)
        .map(str => new Date(str));

      if (allDates.length > 0) {
        const minUpdatedAt = new Date(Math.min(...allDates));
        onMinUpdatedAtChange?.(minUpdatedAt);
      }

    } catch (err) {
      console.error('Ошибка при запросе:', err);
      setError(err.message);
    }
  };

  // 🔁 наружу доступен fetchData как refetch
  useImperativeHandle(ref, () => ({
    refetch: fetchData
  }));

  useEffect(() => {
    fetchData();
  }, []);

  if (error) return <div className="text-red-500">Ошибка: {error}</div>;

  if (!data) {
    return (
      <div className="absolute inset-0 bg-white/60 z-20 flex items-center justify-center text-lg font-medium text-gray-700">
        Загрузка…
      </div>
    );
  }

  return <ParentChildTable data={data} />;
});

export default TableContainer;