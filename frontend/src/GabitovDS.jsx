import './App.css'
import TableContainer from './TableContainer'
import RefreshButton from './RefreshButton'

function GabitovDS() {

  return (
    <>
    <title> Контроль</title>
    <h1 className='top'>Контроль писем</h1>
      <div>
        <RefreshButton id={1}/>
      </div> 
      <div>
        <TableContainer id={1}/>
        
      </div>
      
    </>
  )
}

export default GabitovDS