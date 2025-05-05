import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom';
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import './Test'
import Page from './Page';

function App() {

  return (
    <Routes>
      <Route path="/GabitovDS" element={<Page id={1} />} />
      <Route path="/MusienkoOA" element={<Page id={2} />} />
      <Route path="/BiktimirovRG" element={<Page id={3} />} />

      {/* Редирект на главную, если путь не найден */}
      <Route path="*" element={<Navigate to="/GabitovDS" />} />
    </Routes>
  );
}


export default App
