import { useRef, useState, useEffect } from 'react';
import RefreshButton from './RefreshButton';
import TableContainer from './TableContainer';
import RefreshSoglButton from './RefreshSoglButton';
const authUrl = import.meta.env.VITE_AUTH_URL;
const authBackendUrl = import.meta.env.VITE_AUTH_BACKEND_URL;



function Page() {
  const tableRef = useRef();
  const [minUpdatedAt, setMinUpdatedAt] = useState(null);
  const [now, setNow] = useState(new Date());

  const [user, setUser] = useState({
  "user_uuid": null,
  "first_name": null,
  "middle_name": null,
  "last_name": null,});

  const fetchData  = async (_uuid) => {
    try {
      // const payload = { user_id: id };

      const response = await fetch(`${authBackendUrl}/v1/user/get_user/${_uuid}`, {
        method: 'GET',
        credentials: "include",
      });

      if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);

      const responseData = await response.json();
      if (responseData) {
        setUser(responseData);
      }
      else {
        console.error(`Ошибка при запросе по uuid, ответ :${responseData}`)
      }
      setUser(responseData);

    } catch (err) {
      console.error('Ошибка при запросе:', err);
      setError(err.message);
    }
  };

    useEffect(() => {
    const interval = setInterval(() => {
      setNow(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
  const cookies = document.cookie.split(';').map(c => c.trim());
  const uuidCookie = cookies.find(cookie => cookie.startsWith('uuid='));
  const uuid = uuidCookie ? uuidCookie.split('=')[1] : null;

  if (!uuidCookie) {
    window.location.href = authUrl; // 🔁 укажи нужную ссылку
  }
  else {
    fetchData(uuid);

    console.log(uuid);
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
      {/* <div className="absolute left-1/2 transform -translate-x-1/2 text-2xl font-medium text-gray-900 dark:text-gray-100">
        Контроль Писем
      </div> */}
      <div className="absolute left-1/2 transform -translate-x-2/3 text-2xl font-medium text-gray-900 dark:text-gray-100">
        Письма {user.first_name} {user.last_name}
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