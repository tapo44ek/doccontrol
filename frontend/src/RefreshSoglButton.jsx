import { useState, useEffect } from 'react';

const backendUrl = import.meta.env.VITE_BACKEND_URL;

export default function RefreshSoglButton({ onSuccess, id, disabled: propDisabled, nextAvailableTime }) {
  const [loading, setLoading] = useState(false);
  const [serverReady, setServerReady] = useState(false); // Показывать кнопку или нет

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
          const res = await fetch(`${backendUrl}/update/check_status`, {
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
        const res = await fetch(`${backendUrl}/update/check_status`, {
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

      const response = await fetch(`${backendUrl}/update/all_sogl`, {
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

  const isBlocked = loading || !serverReady;

  const buttonText = loading || !serverReady
    ? 'Обновление...'
    : nextAvailableTime
      ? `Обновление доступно с ${nextAvailableTime.toLocaleTimeString()}`
      : 'Обновить соглы';

  return (
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
  );
}