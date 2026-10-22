import { useState } from "react";
import "./App.css";

function Lights(props) {
  const [on, setOn] = useState(0);
  return (
    <div className="cont">
      {new Array(props.amount || 4).fill(0).map((_, x) => (
        <div
          className="light"
          onClick={() => setOn(x)}
          style={
            on == x
              ? { backgroundColor: "yellow", boxShadow: "0 0 20px yellow" }
              : { backgroundColor: "gray" }
          }
        />
      ))}
    </div>
  );
}

function App() {
  return (
    <div>
      <Lights amount={6}/>
      <Lights />
    </div>
  );
}

export default App;
