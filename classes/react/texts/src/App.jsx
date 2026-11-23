import { useState } from "react";
import "./App.css";

function Check(props) {
  const [displayed, setDisplayed] = useState(-1);
  return (
    <div className="cont">
      {props.texts.map((text, index) => (
        <div
          key={index}
          style={{ border: displayed == index ? "1px solid red" : "none" }}
          className="text"
        >
          <input
            type="checkbox"
            checked={displayed == index}
            onChange={(e) => {
              console.log(displayed);
              setDisplayed(e.target.checked ? index : -1);
            }}
          ></input>
          <p>{text}</p>
        </div>
      ))}
    </div>
  );
}

function OnFocus(props) {
  const [onFocus, setOnFocus] = useState(0);
  const [list, setList] = useState(props.texts.slice());
  const textPlacementChange = (direction) => {
    if (direction == "down") {
      if (onFocus == list.length - 1) {
        return;
      }
    } else if (direction == "up") {
      if (onFocus == 0) {
        return;
      }
    }
    const newList = list.slice();
    const addition = direction == "up" ? -1 : 1;
    const newIdx = onFocus + addition;
    const onFocusText = newList[onFocus];
    const onBlurText = newList[newIdx];
    newList[newIdx] = onFocusText;
    newList[onFocus] = onBlurText;
    setOnFocus(onFocus + addition);
    setList(newList);
  };
  return (
    <div className="focus">
      <div className="buttons">
        <button onClick={() => textPlacementChange("up")}>👆</button>
        <button onClick={() => textPlacementChange("down")}>👇</button>
      </div>

      {list.map((text, index) => (
        <p
          key={index}
          onClick={() => {
            setOnFocus(index);
          }}
          className="focus-text"
          style={{
            backgroundColor: onFocus == index ? "#2a63ff" : "lightblue",
          }}
        >
          {text}
        </p>
      ))}
    </div>
  );
}

function App() {
  return (
    <>
      <Check
        texts={[
          `
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Dolorem
            maiores, labore nobis, sapiente ex pariatur consectetur ducimus
            ratione modi adipisci eos
          `,
          `
            perspiciatis laboriosam commodi aperiam blanditiis sunt quas rerum
            fuga repellendus a alias?
          `,
          `
            Architecto incidunt voluptatibus atque dignissimos sequi facere
            quis, corporis maxime, ut nemo numquam delectus expedita. Magnam
            aperiam recusandae quam perferendis incidunt quia!
          `,
        ]}
      />
      <OnFocus
        texts={[
          `1: Lorem ipsum dolor sit amet consectetur adipisicing elit. Dolorem
            maiores, labore nobis, sapiente ex pariatur consectetur ducimus
            ratione modi adipisci eos`,

          `2: perspiciatis laboriosam commodi aperiam blanditiis sunt quas rerum
            fuga repellendus a alias?
         `,
          `
            3: Architecto incidunt voluptatibus atque dignissimos sequi facere
            quis, corporis maxime, ut nemo numquam delectus expedita. Magnam
            aperiam recusandae quam perferendis incidunt quia!
          `,
        ]}
      />
    </>
  );
}

export default App;
