import { useEffect, useState } from "react";
import "./App.css";

function Circle() {
  const colors = ["yellow", "pink", "orange", "red", "purple", "blue"];
  const [colorIdx, setColorIdx] = useState(0);
  return (
    <div
      className="circle"
      onClick={() => setColorIdx((colorIdx + 1) % colors.length)}
      style={{ backgroundColor: colors[colorIdx] }}
    ></div>
  );
}

function RandomNumber(props) {
  const [number, setNumber] = useState(Math.floor(Math.random() * props.max));
  return (
    <div className="number">
      <p>Number: {number}</p>
      <button onClick={() => setNumber(Math.floor(Math.random() * props.max))}>
        Generate new number
      </button>
    </div>
  );
}

function GenerateDiv() {
  const [color, setColor] = useState("green");
  const [size, setSize] = useState(200);
  const [radius, setRadius] = useState(10);
  return (
    <div className="inputs">
      <span>Choose color </span>
      <input
        type="color"
        value={color}
        onChange={(e) => setColor(e.target.value)}
      />
      <span>Choose size</span>
      <input
        type="number"
        min={0}
        value={size}
        onChange={(e) => setSize(e.target.value)}
      />
      <span>Choose radius</span>
      <input
        type="number"
        min={0}
        max={50}
        value={radius}
        onChange={(e) => setRadius(e.target.value)}
      />
      <br />
      <div
        style={{
          backgroundColor: color,
          height: `${size}px`,
          width: `${size}px`,
          borderRadius: `${radius}%`,
        }}
      ></div>
    </div>
  );
}

function CatFact() {
  const [count, setCount] = useState(1);
  const [facts, setFacts] = useState([]);
  useEffect(() => {
    fetch("https://meowfacts.herokuapp.com/?count=" + count)
      .then((response) => response.json())
      .then((result) => setFacts(result.data));
  }, [count]);
  return (
    <div>
      <span>Number of facts </span>
      <input
        type="number"
        value={count}
        onChange={(event) =>
          setCount(event.target.value < 1 ? 1 : event.target.value)
        }
      />
        <ul>
          {facts.map((f, i) => (
            <li key={i}>{f}</li>
          ))}
        </ul>
    </div>
  );
}

function DateConvertion() {
  const [result, setResult] = useState('')
  const [date, setDate] = useState('01/01/2000')
  useEffect(() => {
    fetch(`https://www.hebcal.com/converter?cfg=json&date=${date}&g2h=1&strict=1`)
    .then(response => response.json())
    .then(res => setResult(res.hebrew))
  }, [date])
  return <div>
    <input type="date" value={date} min={1} max={31} onChange={(e) => setDate(e.target.value)} />
    <p>Converted date: -- {result} --</p>
  </div>
}

function App() {
  return (
    <>
      <DateConvertion/>
      <Circle />
      <RandomNumber max={50} />
      <GenerateDiv />
      <CatFact />
    </>
  );
}

export default App;
