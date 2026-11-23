import { useEffect, useState } from "react";
import { getJokeById } from "../utils/jokes";
import { removeId } from "../utils/storage";
import { translate } from "../utils/translation.js";

function Joke({ jokeObj, setGetJokesBool }) {
  const [translateResult, setTranslateResult] = useState("");
  const [showTranslated, setShowTranslated] = useState(false);
  const [loading, setLoading] = useState(false)

  const onTranslateClick = async () => {
    setLoading(true)
    if (!showTranslated && !translateResult) {
      setTranslateResult(await translate(jokeObj.joke));
    }
    setLoading(false)
  };
  return (
    <div className="joke">
      <button
        disabled={!jokeObj}
        className="translate liked-translate"
        onClick={() => {
          setShowTranslated((prev) => !prev);
          onTranslateClick();
        }}
      >
        {showTranslated ? "Original" : "Translate"}
      </button>
      <span>{loading ? "Loading..." : !showTranslated ? jokeObj.joke : translateResult}</span>
      <button
        className="remove"
        onClick={() => {
          removeId(jokeObj.id);
          setGetJokesBool((prev) => !prev);
        }}
      >
        REMOVE
      </button>
    </div>
  );
}

function Liked() {
  const [jokes, setJokes] = useState([]);
  const [getJokesBool, setGetJokesBool] = useState(true);
  useEffect(() => {
    Promise.all(
      JSON.parse(localStorage.getItem("liked") || "[]").map((id) =>
        getJokeById(id),
      ),
    ).then((allJokes) => setJokes(allJokes));
  }, [getJokesBool]);
  return (
    <div className="liked">
      {jokes.length != 0 ? (
        jokes.map((jokeObj) => (
          <Joke
            key={jokeObj.id}
            jokeObj={jokeObj}
            setGetJokesBool={setGetJokesBool}
          />
        ))
      ) : (
        <span>Like some jokes to see them here</span>
      )}
    </div>
  );
}

export default Liked;
