import { useState, useEffect, useRef } from 'react';
import { ChevronDown } from 'lucide-react';

const backendUrl = import.meta.env.VITE_BACKEND_URL;

export default function RefreshButton({ onSuccess, id, disabled: propDisabled, nextAvailableTime }) {
  const [loading, setLoading] = useState(false);
  const [serverReady, setServerReady] = useState(false); // Показывать кнопку или нет
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const getCookieUUID = () => {
    const match = document.cookie.match(/uuid=([^;]+)/);
    return match ? match[1] : null;
  };

  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  useEffect(() => {
    let isCancelled = false;

    const checkServerStatus = async () => {
      const localUUID = getCookieUUID();

      while (!isCancelled) {
        try {
          const res = await fetch(`${backendUrl}/update/check_status?id=1`, {
            credentials: 'include',
          });

          if (!res.ok) {
            throw new Error(`Ошибка статуса: ${res.status}`);
          }

          const data = await res.json();

          if (data.user_uuid !== localUUID) {
            setServerReady(true);
            break; // условие достигнуто — перестаём проверять
          }
        } catch (err) {
          console.error('Ошибка при проверке uuid:', err);
          break;
        }

        await delay(10000);
      }
    };

    checkServerStatus();

    return () => {
      isCancelled = true; // корректно завершаем при размонтировании
    };
  }, []);

  const checkStatusUntilReady = async () => {
    while (true) {
      try {
        const res = await fetch(`${backendUrl}/update/check_status?id=1`, {
          credentials: 'include',
        });

        if (!res.ok) {
          throw new Error(`Ошибка статуса: ${res.status}`);
        }

        const data = await res.json();

        if (!data.is_working) {
          break; // можно запускать обновление
        }
      } catch (err) {
        console.error('Ошибка при проверке статуса:', err);
        break;
      }

      await delay(10000);
    }
  };

  const handleClick = async () => {
    setLoading(true);
    try {
      await checkStatusUntilReady();

      const response = await fetch(`${backendUrl}/update/all_docs?force=true`, {
        method: 'PATCH',
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`Ошибка обновления: ${response.status}`);
      }

      await response.json();

      if (onSuccess) {
        await onSuccess();
      }
    } catch (error) {
      console.error('Ошибка при обновлении:', error);
    } finally {
      setLoading(false);
    }
  };

  const isBlocked = loading || propDisabled || !serverReady;

  const buttonText = loading || !serverReady
    ? 'Обновление...'
    : propDisabled && nextAvailableTime
      ? `Обновление доступно с ${nextAvailableTime.toLocaleTimeString()}`
      : 'Обновить все';


  const handleForceFullClick = async () => {
    setLoading(true);
    setDropdownOpen(false);
    try {
      await checkStatusUntilReady();

      const response = await fetch(`${backendUrl}/update/all_docs?force=false`, {
        method: 'PATCH',
        credentials: "include",
      });

      if (!response.ok) throw new Error(`Ошибка полного обновления: ${response.status}`);
      await response.json();
      onSuccess?.();
    } catch (error) {
      console.error('Ошибка при полном обновлении:', error);
    } finally {
      setLoading(false);
    }
  };

  // const isBlocked = loading || propDisabled || !serverReady;

  return (
    <div className={`relative inline-flex items-center ${
        isBlocked ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
      }`}>
    <button
      onClick={handleClick}
      disabled={isBlocked}
      className={`px-4 py-2 rounded text-white font-semibold transition ${
        isBlocked ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
      }`}
      title={propDisabled && nextAvailableTime ? `Доступно в ${nextAvailableTime.toLocaleTimeString()}` : ''}
    >
      {buttonText}
    </button>

          <button
        onClick={() => setDropdownOpen(prev => !prev)}
        disabled={isBlocked}
        className={`px-2 py-2 rounded-r border-l border-white text-white font-semibold transition ${
          isBlocked ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
        }`}
        title="Доп. действия"
      >
        <ChevronDown size={10} />
      </button>

      {dropdownOpen && (
        <div
          ref={dropdownRef}
          className="absolute left-0 top-full mt-2 z-50 bg-white border border-gray-200 rounded shadow-md w-full"
        >
          <button
            onClick={handleForceFullClick}
            className={`px-2 py-2 rounded-r border-l border-white text-white font-semibold transition ${
          isBlocked ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
        }`}
          >
            🔥 Обновить совсем всё
          </button>
        </div>
      )}
      </div>
  );
  
}