import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import Main from "./components/mainPage.jsx";
import Brows from "./components/brows.jsx";
import Liked from "./components/liked.jsx";
import Menu from './components/menu.jsx'

function App() {
  return (
    <BrowserRouter>
    <Menu/>
      <Routes>
        <Route index element={<Main />} />
        <Route path="brows" element={<Brows />} />
        <Route path="favorites" element={<Liked />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
