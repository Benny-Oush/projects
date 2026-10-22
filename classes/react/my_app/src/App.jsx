// import { useState } from 'react'
import { useState } from "react";
import "./App.css";

function App() {
  const [clicks, setClicks] = useState(0);
  return (
    <div>
      <button onClick={() => setClicks(clicks + 1)}>Click Me!</button>
      <br />
      <span>"You clicked {clicks} times!</span>
    </div>
  );
}

export default App;
