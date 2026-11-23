import { useState } from "react";
import "./App.css";

function Calculator() {
  const [firstToken, setFirstToken] = useState("");
  const [operator, setOperator] = useState("");
  const [lastToken, setLastToken] = useState("");
  const [renderingResult, setRenderingResult] = useState(false);
  const calculate = () => {
    if (!firstToken || !operator || !lastToken) {
      return;
    }
    switch (operator) {
      case "+":
        setFirstToken(`${Number(firstToken) + Number(lastToken)}`);
        break;
      case "-":
        setFirstToken(`${Number(firstToken) - Number(lastToken)}`);
        break;
      case "x":
        setFirstToken(`${Number(firstToken) * Number(lastToken)}`);
        break;
      case "/":
        setFirstToken(`${Number(firstToken) / Number(lastToken)}`);
        break;
    }
    setLastToken("");
    setOperator("");
  };
  const onNumClick = (num) => {
    if (firstToken.length + lastToken.length >= 13) {
      return;
    }
    if ((!firstToken && firstToken != "-") || renderingResult) {
      setFirstToken(num);
      if (renderingResult) {
        setRenderingResult(false);
      }
      return;
    }
    if (!operator) {
      setFirstToken((prev) => `${prev}${num}`);
    } else {
      setLastToken((prev) => `${prev}${num}`);
    }
  };

  const onOperatorClick = (operator) => {
    if (renderingResult) {
      setRenderingResult(false);
    }
    if (!firstToken && operator == "-") {
      setFirstToken("-");
      return;
    }
    if (firstToken == "-" || !firstToken) {
      return;
    }
    if (!lastToken) {
      setOperator(operator);
    } else {
      calculate();
      setOperator(operator);
    }
  };

  const toDecimal = () => {
    if (!operator) {
      if (renderingResult) {
        setFirstToken("0.");
        setRenderingResult(false);
        return;
      }
      if (firstToken == "-") {
        setFirstToken("-0.");
      } else if (!firstToken) {
        setFirstToken("0.");
      } else {
        if (firstToken.includes(".")) {
          return;
        }
        setFirstToken((prev) => `${prev}.`);
      }
    } else {
      if (lastToken == "-") {
        setLastToken("-0.");
      } else if (!lastToken) {
        setLastToken("0.");
      } else {
        if (lastToken.includes(".")) {
          return;
        }
        setLastToken((prev) => `${prev}.`);
      }
    }
  };

  return (
    <div className="cont">
      <div className="row">
        <button
          className="c"
          onClick={() => {
            if (renderingResult) {
              setRenderingResult(false);
            }
            setFirstToken("");
            setLastToken("");
            setOperator("");
          }}
        >
          C
        </button>
        <div className="result">
          <>{`${firstToken}${operator}${lastToken}`.substring(0, 14) || "|"}</>
        </div>
      </div>
      <div className="row">
        <button onClick={() => onNumClick("9")} className="number">
          9
        </button>
        <button onClick={() => onNumClick("8")} className="number">
          8
        </button>
        <button onClick={() => onNumClick("7")} className="number">
          7
        </button>
        <button onClick={() => onOperatorClick("/")}>/</button>
      </div>
      <div className="row">
        <button onClick={() => onNumClick("6")} className="number">
          6
        </button>
        <button onClick={() => onNumClick("5")} className="number">
          5
        </button>
        <button onClick={() => onNumClick("4")} className="number">
          4
        </button>
        <button onClick={() => onOperatorClick("x")}>X</button>
      </div>
      <div className="row">
        <button onClick={() => onNumClick("3")} className="number">
          3
        </button>
        <button onClick={() => onNumClick("2")} className="number">
          2
        </button>
        <button onClick={() => onNumClick("1")} className="number">
          1
        </button>
        <button onClick={() => onOperatorClick("-")}>-</button>
      </div>
      <div className="row">
        <button onClick={toDecimal}>.</button>
        <button
          onClick={() => {
            if (renderingResult) {
              return;
            }
            if (!operator) {
              if (
                (!+firstToken && !firstToken.includes(".")) ||
                firstToken == "-"
              ) {
                return;
              }
              setFirstToken((prev) => `${prev}0`);
            } else {
              if (
                (!+lastToken && !lastToken.includes(".")) ||
                lastToken == "-"
              ) {
                return;
              }
              setLastToken((prev) => `${prev}0`);
            }
          }}
          className="number"
        >
          0
        </button>
        <button
          onClick={() => {
            calculate();
            setRenderingResult(true);
          }}
        >
          =
        </button>
        <button onClick={() => onOperatorClick("+")}>+</button>
      </div>
    </div>
  );
}

function Exercise(props) {
  const [answer, setAnswer] = useState(0);
  const [display, setDisplay] = useState(false);
  const check = () => {
    switch (props.op) {
      case "+":
        return props.n + props.m == answer;
      case "-":
        return props.n - props.m == answer;
      case "*":
        return props.n * props.m == answer;
      case "/":
        return props.n / props.m == answer;
    }
  };
  return (
    <div className="exercise">
      <span>
        {props.n} {props.op} {props.m} = ?
      </span>
      <span>Enter your answer: </span>
      <input
        value={answer || ""}
        disabled={display}
        type="number"
        onChange={(e) => setAnswer(e.target.value)}
      />
      <button
        disabled={!answer}
        onClick={() => {
          setDisplay((prev) => !prev);
          if (display) {
            setAnswer(0);
          }
        }}
      >
        {display ? "Reset" : "Check Your Answer"}
      </button>
      {display && <div className="correct" >{check() ? "Correct!" : "Incorrect!"}</div>}
    </div>
  );
}

function App() {
  return (
    <>
      <Calculator />
      <br />
      <Exercise n={2} m={3} op={"+"} />
    </>
  );
}

export default App;
