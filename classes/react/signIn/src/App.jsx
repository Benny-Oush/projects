import { useEffect, useState } from "react";
import "./App.css";

function EmailPage(props) {
  const onEmailFill = props.onEmailFill;
  const [input, setInput] = useState("");
  const [showErrors, setShowErrors] = useState(false);
  return (
    <div
      style={{ display: props.onDisplay == 0 ? "block" : "none" }}
      className="page"
    >
      <div className="email">
        <span className="welcome">Welcome</span>
        <span>Enter your email: </span>
        <input
          style={{
            border: showErrors && !props.email ? "red 2px solid" : "none",
          }}
          type="email"
          placeholder="example@gmail.com"
          onChange={(e) => setInput(e.target.value)}
        />
        <span
          style={
            !props.email && showErrors ? { color: "red" } : { display: "none" }
          }
        >
          Enter a valid email
        </span>
      </div>
      <button
        onClick={() => {
          setShowErrors(true);
          onEmailFill(input);
        }}
      >
        NEXT
      </button>
    </div>
  );
}

function NamePage(props) {
  const onAgeFill = props.onAgeFill;
  const [showErrors, setShowErrors] = useState(false);
  return (
    <div
      style={{ display: props.onDisplay == 1 ? "block" : "none" }}
      className="page name"
    >
      <div className="nameInput">
        <span>Enter your name: </span>
        <input
          onChange={(e) => props.setName(e.target.value)}
          type="text"
          placeholder="Name..."
          style={{
            border: !props.name && showErrors ? "2px red solid" : "none",
          }}
        />
      </div>
      <div className="age">
        <span>Enter your age: </span>
        <input
          min={10}
          max={120}
          type="number"
          style={{
            border: !props.age && showErrors ? "2px solid red" : "none",
          }}
          onChange={(e) => onAgeFill(e.target.value)}
        />
      </div>
      {!props.age && showErrors ? (
        <div style={{ color: "red", marginTop: "10px" }}>
          Age must be beetwen 10 and 120
        </div>
      ) : (
        <br />
      )}
      <div className="colorInput">
        <span>Choose your favorite color: </span>
        <input
          value={props.favoriteColor}
          type="color"
          onChange={(e) => props.setFavoriteColor(e.target.value)}
        />
      </div>
      <div className="buttons">
        <button onClick={() => props.setOnDisplay(0)}>BACK</button>
        <button
          onClick={() => {
            props.validNamePage();
            setShowErrors(true);
          }}
        >
          NEXT
        </button>
      </div>
    </div>
  );
}

function FindingPage(props) {
  const [showErrors, setShowErrors] = useState(false);
  const options = [
    "other",
    "online search",
    "social media",
    "an ad",
    "friends",
  ];
  return (
    <div
      style={{ display: props.onDisplay == 2 ? "block" : "none" }}
      className="page"
    >
      <div className="finding">
        <span>How did you find us? </span>
        <select onChange={(e) => props.setFindingMethod(e.target.value)}>
          {options.map((option) => (
            <option value={option} key={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
      {props.findingMethod == "other" && (
        <div className="expand">
          <span>Explain: </span>
          <textarea
            style={{
              border:
                !props.expandMethod && showErrors ? "red 2px solid" : "none",
            }}
            type="text"
            onChange={(e) => props.setExpandMethod(e.target.value)}
          ></textarea>
        </div>
      )}
      <div className="buttons">
        <button onClick={() => props.setOnDisplay(1)}>BACK</button>
        <button
          onClick={() => {
            props.validFindingPage();
            setShowErrors(true);
          }}
        >
          FINISH
        </button>
      </div>
    </div>
  );
}

function FinishPage(props) {
  useEffect(() => {
    if (props.onDisplay == 3) {
      const findingMethod =
        props.findingMethod == "other"
          ? { method: "other", details: props.expand }
          : props.findingMethod;
      const details = {
        email: props.email,
        name: props.name,
        age: props.age,
        favoriteColor: props.favoriteColor,
        findingMethod: findingMethod,
      };
      console.log(details);
    }
  }, [props.onDisplay]);

  return (
    <div
      className="page finish"
      style={{ display: props.onDisplay == 3 ? "block" : "none" }}
    >
      Thank You!
    </div>
  );
}

function App() {
  const [onDisplay, setOnDisplay] = useState(0);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [age, setAge] = useState(0);
  const [favoriteColor, setFavoriteColor] = useState("#FFFF00");
  const [findingMethod, setFindingMethod] = useState("other");
  const [expandMethod, setExpandMethod] = useState("");

  const onEmailFill = (email) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (emailRegex.test(email)) {
      setEmail(email);
      setOnDisplay(1);
    } else {
      setEmail("");
    }
  };
  const onAgeFill = (age) => {
    if (age <= 120 && age >= 10) {
      setAge(age);
    } else {
      setAge(0);
    }
  };
  const validNamePage = () => {
    if (name && age) {
      setOnDisplay(2);
    }
  };
  const validFindingPage = () => {
    if (findingMethod != "other") {
      setOnDisplay(3);
    } else {
      if (expandMethod) {
        setOnDisplay(3);
      }
    }
  };
  return (
    <>
      <EmailPage
        onEmailFill={onEmailFill}
        onDisplay={onDisplay}
        setOnDisplay={setOnDisplay}
        email={email}
      />
      <NamePage
        onDisplay={onDisplay}
        setOnDisplay={setOnDisplay}
        validNamePage={validNamePage}
        onAgeFill={onAgeFill}
        age={age}
        name={name}
        setName={setName}
        setFavoriteColor={setFavoriteColor}
        favoriteColor={favoriteColor}
      />
      <FindingPage
        onDisplay={onDisplay}
        setOnDisplay={setOnDisplay}
        validFindingPage={validFindingPage}
        expandMethod={expandMethod}
        setExpandMethod={setExpandMethod}
        findingMethod={findingMethod}
        setFindingMethod={setFindingMethod}
      />
      <FinishPage
        email={email}
        name={name}
        age={age}
        favoriteColor={favoriteColor}
        findingMethod={findingMethod}
        expand={expandMethod}
        onDisplay={onDisplay}
      />
    </>
  );
}

export default App;
