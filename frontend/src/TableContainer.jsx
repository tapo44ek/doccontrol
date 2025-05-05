import { useEffect, useState } from 'react'
import './App.css'
import './Test'
import ParentChildTable from './Test'

function TableContainer({ id }) {
  const [count, setCount] = useState(0)
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const payload = {
          user_id: id
        };

        const response = await fetch('http://127.0.0.1:8000/doccontrol/user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`Ошибка сервера: ${response.status}`);
        }

        const responseData = await response.json();
        setData(responseData);
      } catch (err) {
        console.error('Ошибка при запросе:', err);
        setError(err.message);
      }
    };

    fetchData();
  }, []);

  if (error) {
    return <div className="text-red-500">Ошибка: {error}</div>;
  }

  if (!data) {
    return   <div className="absolute inset-0 bg-white/60 z-20 flex items-center justify-center text-lg font-medium text-gray-700">
    Загрузка…
  </div>;
  }

  return (
    <>
      <div>

        <ParentChildTable data={data} id={id} />
        
      </div>
      
    </>
  )
}

export default TableContainer