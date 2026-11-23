import { useState } from 'react';
import './App.css'
import Main from './components/mainPage.jsx';
import Menu from './components/menu.jsx';
import Brows from './components/brows.jsx';
import Liked from "./components/liked.jsx"

const components = [<Main/>, <Brows/>, <Liked/>]

function App() {
  const [currentPage, setCurrentPage] = useState(0)
  return <>
  <Menu setCurrentPage={setCurrentPage} currentPage={currentPage}/>
  {components[currentPage]}
  </>

}

export default App
