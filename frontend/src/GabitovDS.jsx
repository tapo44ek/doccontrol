import './App.css'
import TableContainer from './TableContainer'
import RefreshButton from './RefreshButton'

function GabitovDS() {

  return (
    <>
    <title> Контроль</title>
    <header className="flex items-center justify-between px-4 py-5 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
  {/* Левая кнопка */}
  <div className="flex items-center">
  <RefreshButton id={1}/>
  </div>

  {/* Центрированный заголовок */}
  <div className="absolute left-1/2 transform -translate-x-1/2 text-2xl font-medium text-gray-900 dark:text-gray-100">
    Контроль Писем
  </div>
</header>

      <div>
        <TableContainer id={1}/>
        
      </div>
      
    </>
  )
}

export default GabitovDS