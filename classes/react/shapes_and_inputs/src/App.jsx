import { useState } from "react";
import "./App.css";

function Shape(props) {
  const [circle, setCircle] = useState(false);
  const [color, setColor] = useState("red");
  const box = (
    <div
      className="circle"
      style={{ borderRadius: circle ? "50%" : 0, backgroundColor: color }}
    ></div>
  );
  const [isTextual, setIsTextual] = useState(false);
  const text = (
    <p className="text">
      A {color} {!circle ? "square" : "circle"}
    </p>
  );
  return (
    <div className="cont">
      <div>
        <input type="checkBox" onChange={() => setCircle(!circle)} />
        <span>Circle</span>
        <br />
      </div>
      <select onClick={(e) => setColor(e.target.value)}>
        {props.colors.map((color) => (
          <option value={color} key={color}>
            {color}
          </option>
        ))}
      </select>
      <div>
        <input type="checkBox" onChange={() => setIsTextual(!isTextual)} />
        <span>Text</span>
      </div>
      {isTextual ? text : box}
    </div>
  );
}

function TextInputs(props) {
  const [isInput, setIsInput] = useState(false);
  const [innerText, setInnerText] = useState("missing");
  const changeText = (e) => {
    setInnerText(e.target.value || "missing");
    setIsInput(false);
  };
  return (
    <div className="cont">
      <p>
        {props.label}:{" "}
        {!isInput ? (
          <span onDoubleClick={() => setIsInput(true)}>{innerText}</span>
        ) : (
          <input
            type="text"
            placeholder={innerText}
            onBlur={(e) => changeText(e)}
            onKeyDown={(e) => (e.key == "Enter" ? changeText(e) : "")}
          ></input>
        )}
      </p>
    </div>
  );
}

function App() {
  return (
    <>
      <TextInputs label={"Name"} />
      <TextInputs label={"Age"} />
      <TextInputs label={"City"} />
      <TextInputs label={"Profession"} />
      <Shape
      colors={[
          "red",
          "green",
          "blue",
          "lightBlue",
          "pink",
          "yellow",
          "black",
          "purple",
          "orange",
        ]}
        />
    </>
  );

}

export default App;
