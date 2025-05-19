import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom';
import './App.css'
import './Test'
import Page from './Page';

function App() {

  return (
    <Routes>
      <Route path="/" element={<Page />} />
      {/* <Route path="/MusienkoOA" element={<Page id={2} />} />
      <Route path="/BiktimirovRG" element={<Page id={3} />} /> */}

      {/* Редирект на главную, если путь не найден */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}


export default App
