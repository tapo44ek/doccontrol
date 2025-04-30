import { useState } from 'react';

export default function RefreshButton({ onSuccess , id}) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://10.9.96.160:5152/update/user', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: id }), // если нужно тело запроса
      });

      if (!response.ok) {
        throw new Error(`Ошибка обновления: ${response.status}`);
      }

      await response.json(); // если сервер возвращает что-то (даже пустой объект)

      if (onSuccess) {
        await onSuccess(); // если успех — вызываем перезагрузку данных таблицы
      }
    } catch (error) {
      console.error('Ошибка при обновлении:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className={`px-4 py-2 rounded text-white font-semibold transition ${
        loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
      }`}
    >
      {loading ? 'Обновление...' : 'Обновить данные'}
    </button>
  );
}