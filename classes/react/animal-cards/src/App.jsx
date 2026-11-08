import { useState } from "react";

import "./App.css";

import images from "./assets/images.json";

function Card(props) {
  const [like, setLike] = useState(false);
  const emptyHeart = "🤍";
  const filledHeart = "♥️";
  return (
    <div className="card">
      <div className="heart" onClick={() => setLike(!like)}>
        {like ? filledHeart : emptyHeart}
      </div>
      <img src={props.url} />
      <p className="type">{props.type}</p>
    </div>
  );
}

function Filter() {
  const [displayTypes, setDisplayTypes] = useState(["duck", "dog", "fox"]);
  const click = (type) => {
    displayTypes.includes(type)
      ? setDisplayTypes(displayTypes.filter((animal) => animal != type))
      : setDisplayTypes([...displayTypes, type]);
  };
  return (
    <div className="cont">
      <div className="nuv">
        <div className="animal" onClick={() => click("duck")}>
          Ducks
        </div>
        <div className="animal" onClick={() => click("dog")}>
          Dogs
        </div>
        <div className="animal" onClick={() => click("fox")}>
          Foxes
        </div>
      </div>
      <div className="cards-cont">
        {images
          .filter((item) => displayTypes.includes(item.type))
          .map((item) => (
            <Card key={item.id} type={item.type} url={item.img} />
          ))}
      </div>
    </div>
  );
}

function App() {
  return <Filter />;
}

export default App;
