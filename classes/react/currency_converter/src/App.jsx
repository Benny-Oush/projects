import { useState, useEffect } from "react";
import "./App.css";
const dateObj = new Date();

const day = String(dateObj.getDate()).padStart(2, "0");
const month = String(dateObj.getMonth() + 1).padStart(2, "0");
const year = dateObj.getFullYear();

const currentDate = `${year}-${month}-${day}`;
console.log(currentDate);

function Converter() {
  const [currencies, setCurrencies] = useState([]);
  const [date, setDate] = useState(currentDate);
  const [from, setFrom] = useState("USD");
  const [to, setTo] = useState("ILS");
  const [amount, setAmount] = useState(1);
  const [result, setResult] = useState(0);

  useEffect(() => {
    fetch("https://api.frankfurter.dev/v2/currencies")
      .then((response) => response.json())
      .then((result) => setCurrencies(result));
    console.log("Done");
  }, []);
  useEffect(() => {
    fetch(`https://api.frankfurter.dev/v2/rate/${from}/${to}?date=${date}`)
      .then((response) => response.json())
      .then((res) => {
        setResult(res.rate);
        console.log(res);
      });
  }, [date, from, to]);
  return (
    <div className="cont">
      <p>Currency Exchange Rates</p>
      <div className="selection">
        <span>Date: </span>
        <input
          type="date"
          value={date}
          onChange={(e) => {
            const value = e.target.value;
            if (
              value >=
                currencies.find((obj) => obj.iso_code == from).start_date &&
              value >=
                currencies.find((obj) => obj.iso_code == to).start_date &&
              value <= currentDate
            ) {
              setDate(value);
            }
          }}
        />
      </div>
      <div className="selection">
        <span>From: </span>
        <select
          disabled={currencies.length == 0}
          value={from}
          onChange={(e) => setFrom(e.target.value)}
        >
          {currencies.map((obj) => (
            <option key={obj.iso_code} value={obj["iso_code"]}>
              {obj["name"]}
            </option>
          ))}
        </select>
      </div>
      <div className="selection">
        <span>To: </span>
        <select
          disabled={currencies.length == 0}
          value={to}
          onChange={(e) => setTo(e.target.value)}
        >
          {currencies.map((obj) => (
            <option key={obj.iso_code} value={obj["iso_code"]}>
              {obj["name"]}
            </option>
          ))}
        </select>
      </div>
      <div className="selection">
        <span>Amount: </span>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          min={0}
        />
      </div>
      <div className="selection">
        <span>Result: </span>
        <span className="result">{`${currencies.find((obj) => obj.iso_code == to)?.symbol || ""}${(result * amount).toFixed(3)}`}</span>
      </div>
    </div>
  );
}

function App() {
  return <Converter />;
}

export default App;
