import { useEffect, useState } from "react";
import "./App.css";

function Clock() {
  const [date, setDate] = useState(new Date());
  useEffect(() => {
    const intervalId = setInterval(() => {
      setDate(new Date());
    }, 1000);
    return () => clearInterval(intervalId);
  }, []);
  return (
    <div className="clock">
      <span>{date.toLocaleTimeString().substring(0, 2)}</span>
      <span className="sep">:</span>
      <span>{date.toLocaleTimeString().substring(3, 5)}</span>
      <span className="sep">:</span>
      <span>{date.toLocaleTimeString().substring(6, 8)}</span>
    </div>
  );
}

function Stopper({ seconds, setSeconds, on, setOn }) {
  useEffect(() => {
    if (seconds == 9999) {
      setSeconds(0);
      localStorage.setItem("stopperSeconds", "0");
    }
  }, [seconds]);
  useEffect(() => {
    if (!on) {
      return;
    }
    const intervalId = setInterval(() => {
      setSeconds((prev) => {
        localStorage.setItem("stopperSeconds", (prev + 1).toString());
        return prev + 1;
      });
    }, 10);

    return () => clearInterval(intervalId);
  }, [on]);
  return (
    <div className="stopper">
      <span>
        {seconds ? (
          <div>
            <span>
              {Math.floor(seconds / 100)
                .toString()
                .padStart(2, "0")}
            </span>
            <span className="sep">.</span>
            <span>{(seconds % 100).toString().padStart(2, "0")}</span>
          </div>
        ) : (
          <div>
            <span>00</span>
            <span className="sep">.</span>
            <span>00</span>
          </div>
        )}
      </span>
      <div className="buttons">
        <button onClick={() => setOn((prev) => !prev)}>
          {on ? "⏸️" : "▶️"}
        </button>
        <button
          onClick={() => {
            setSeconds(0);
            localStorage.setItem("stopperSeconds", "0");
          }}
        >
          🔄️
        </button>
      </div>
    </div>
  );
}

function Timer({
  seconds,
  setSeconds,
  countDown,
  setCountDown,
  running,
  setRunning,
}) {
  useEffect(() => {
    if (seconds == 0) {
      setCountDown(false);
      setRunning(false);
      setSeconds(0);
      localStorage.setItem("timerSeconds", "0");
    }
  }, [seconds]);
  const [toAdd, setToAdd] = useState(60);
  useEffect(() => {
    if (!countDown) {
      return;
    }
    const intervalId = setInterval(() => {
      setSeconds((prev) => {
        localStorage.setItem("timerSeconds", (prev - 1).toString());
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(intervalId);
  }, [countDown]);
  return (
    <div className="timer">
      <span style={{ color: !running && toAdd == 60 ? "red" : "black" }}>
        {Math.floor(seconds / 60)
          .toString()
          .padStart(2, "0")}
      </span>
      <span>:</span>
      <span style={{ color: !running && toAdd == 10 ? "red" : "black" }}>
        {(seconds % 60).toString().padStart(2, "0")}
      </span>
      {running ? (
        <div className="buttons">
          <button
            onClick={() => {
              setCountDown((prev) => !prev);
            }}
          >
            {countDown ? "⏸️" : "▶️"}
          </button>
          <button
            onClick={() => {
              setCountDown(false);
              setRunning(false);
              setSeconds(0);
              localStorage.setItem("timerSeconds", "0");
            }}
          >
            🔄️
          </button>
        </div>
      ) : (
        <div className="buttons">
          <button
            onClick={() => {
              setSeconds((prev) => {
                localStorage.setItem("timerSeconds", prev + toAdd);
                return prev + toAdd;
              });
            }}
          >
            ⬆️
          </button>
          <button
            onClick={() => {
              if (seconds - toAdd >= 0)
                setSeconds((prev) => {
                  localStorage.setItem("timerSeconds", prev - toAdd);
                  return prev - toAdd;
                });
            }}
          >
            ⬇️
          </button>
        </div>
      )}
      <div className="buttons">
        <button
          disabled={running}
          onClick={() => setToAdd(toAdd == 60 ? 10 : 60)}
        >
          ↔️
        </button>
        <button
          disabled={running || seconds == 0}
          onClick={() => {
            setCountDown(true);
            setRunning(true);
          }}
        >
          ▶️
        </button>
      </div>
    </div>
  );
}

function App() {
  const [stopperSeconds, setStopperSeconds] = useState(
    Number(localStorage.getItem("stopperSeconds")) || 0,
  );
  const [on, setOn] = useState(false);
  const [countDown, setCountDown] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(
    Number(localStorage.getItem("timerSeconds")) || 0,
  );
  const [running, setRunning] = useState(false);
  const [onDisplay, setOnDisplay] = useState(0);
  const buttonTexts = ["Clock", "Stopper", "Timer"];
  const components = [
    <Clock />,
    <Stopper
      seconds={stopperSeconds}
      setSeconds={setStopperSeconds}
      on={on}
      setOn={setOn}
    />,
    <Timer
      countDown={countDown}
      setCountDown={setCountDown}
      seconds={timerSeconds}
      setSeconds={setTimerSeconds}
      running={running}
      setRunning={setRunning}
    />,
  ];

  return (
    <>
      <div>
        <button
          className="switch"
          onClick={() => setOnDisplay((onDisplay + 1) % 3)}
        >
          Switch to {buttonTexts[(onDisplay + 1) % 3]}
        </button>
        {components[onDisplay]}
      </div>
    </>
  );
}

export default App;
