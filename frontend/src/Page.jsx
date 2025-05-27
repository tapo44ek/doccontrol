import { useRef, useState, useEffect } from 'react';
import RefreshButton from './RefreshButton';
import TableContainer from './TableContainer';
import RefreshSoglButton from './RefreshSoglButton';
const authUrl = import.meta.env.VITE_AUTH_URL;



function Page() {
  const tableRef = useRef();
  const [minUpdatedAt, setMinUpdatedAt] = useState(null);
  const [now, setNow] = useState(new Date());

    useEffect(() => {
    const interval = setInterval(() => {
      setNow(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
  const cookies = document.cookie.split(';').map(c => c.trim());
  const hasUuid = cookies.some(cookie => cookie.startsWith('uuid='));

  if (!hasUuid) {
    window.location.href = authUrl; // 🔁 укажи нужную ссылку
  }
}, []);

  const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
  const isBlocked = minUpdatedAt && minUpdatedAt > oneHourAgo;
  const nextAvailableTime = isBlocked
    ? new Date(minUpdatedAt.getTime() + 60 * 60 * 1000)
    : null;

return (
  <>
    <title> Контроль</title>
    <header className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center">
        <div className='px-2'>
        <RefreshButton
          disabled={isBlocked}
          nextAvailableTime={nextAvailableTime}
          onSuccess={() => tableRef.current?.refetch()}
        />
        </div>
        <div className='px-2'>
        <RefreshSoglButton
          disabled={isBlocked}
          nextAvailableTime={nextAvailableTime}
          onSuccess={() => tableRef.current?.refetch()}
        />
        </div>
      </div>
      <div className="absolute left-1/2 transform -translate-x-1/2 text-2xl font-medium text-gray-900 dark:text-gray-100">
        Контроль Писем
      </div>
      <div>
        <button
          onClick={() => {
            document.cookie = "uuid=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC";
            window.location.href = authUrl;
          }}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
        >
          Выход
        </button>
      </div>
    </header>

    <TableContainer ref={tableRef} onMinUpdatedAtChange={setMinUpdatedAt} />
  </>
);
}

export default Page;