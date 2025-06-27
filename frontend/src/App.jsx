import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom';
import './App.css'
import './Test'
import Page from './Page';
import Player from './VideoTest';

function App() {

  return (
    <Routes>
      <Route path="/" element={<Page />} />
      {/* <Route path="/MusienkoOA" element={<Page id={2} />} />
      <Route path="/BiktimirovRG" element={<Page id={3} />} /> */}
      <Route path="/player" element={<Player kp_id={"6802577"} />} />
      {/* Редирект на главную, если путь не найден */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}


export default App
