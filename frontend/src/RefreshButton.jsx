import { useState } from 'react';
const backendUrl = import.meta.env.VITE_BACKEND_URL;

export default function RefreshButton({ onSuccess, id, disabled, nextAvailableTime }) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/update/all_docs`, {
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

  const isBlocked = loading || disabled;

  const buttonText = loading
    ? 'Обновление...'
    : disabled && nextAvailableTime
      ? `Обновление доступно с ${nextAvailableTime.toLocaleTimeString()}`
      : 'Обновить все';

  return (
    <button
      onClick={handleClick}
      disabled={isBlocked}
      className={`px-4 py-2 rounded text-white font-semibold transition ${
        isBlocked ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
      }`}
      title={disabled && nextAvailableTime ? `Доступно в ${nextAvailableTime.toLocaleTimeString()}` : ''}
    >
      {buttonText}
    </button>
  );
}