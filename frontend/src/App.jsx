import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import './Test'
import ParentChildTable from './Test'
import TableContainer from './TableContainer'
import RefreshButton from './RefreshButton'

function App() {

  return (
    <>
    <title> Контроль</title>
    <h1 className='top'>Контроль писем</h1>
      <div>
        <RefreshButton/>
      </div>
      <div>

        <TableContainer/>
        
      </div>
      
    </>
  )
}

export default App
