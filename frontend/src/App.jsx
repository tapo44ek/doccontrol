import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom';
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import './Test'
import GabitovDS from './GabitovDS';

function App() {

  return (
    <Routes>
      <Route path="/GabitovDS" element={<GabitovDS />} />

      {/* Редирект на главную, если путь не найден */}
      <Route path="*" element={<Navigate to="/GabitovDS" />} />
    </Routes>
  );
}


export default App
