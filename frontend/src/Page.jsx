import { useRef, useState } from 'react';
import RefreshButton from './RefreshButton';
import TableContainer from './TableContainer';

function Page({ id }) {
  const tableRef = useRef();
  const [minUpdatedAt, setMinUpdatedAt] = useState(null);

  const now = new Date();
  const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
  const isBlocked = minUpdatedAt && minUpdatedAt > oneHourAgo;
  const nextAvailableTime = isBlocked
    ? new Date(minUpdatedAt.getTime() + 60 * 60 * 1000)
    : null;

  return (
    <>
    <title> Контроль</title>
      <header className="flex items-center justify-between px-4 py-5 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center">
          <RefreshButton
            id={id}
            disabled={isBlocked}
            nextAvailableTime={nextAvailableTime}
            onSuccess={() => tableRef.current?.refetch()} // 🔁 вот оно!
          />
        </div>
        <div className="absolute left-1/2 transform -translate-x-1/2 text-2xl font-medium text-gray-900 dark:text-gray-100">Контроль Писем</div>
      </header>

      <TableContainer id={id} ref={tableRef} onMinUpdatedAtChange={setMinUpdatedAt} />
    </>
  );
}

export default Page;