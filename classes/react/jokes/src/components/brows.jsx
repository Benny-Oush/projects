import { useEffect, useState } from "react";
import { getRandomJoke } from "../utils/jokes.js";
import { addId, removeId } from "../utils/storage.js";
import { translate } from "../utils/translation.js";
import { BookmarkEmptyIcon, BookmarkFilledIcon } from "../assets/jsx-assets/bookmark.jsx";

function Brows() {
  const [nextBool, setNextBool] = useState(false);
  const [currentJoke, setCurrentJoke] = useState("");
  const [loading, setLoading] = useState(true);
  const [liked, setLiked] = useState(false);
  const [translateResult, setTranslateResult] = useState("");
  const [showTranslated, setShowTranslated] = useState(false);

  const onTranslateClick = async () => {
    setLoading(true);
    if (!showTranslated && !translateResult) {
      setTranslateResult(await translate(currentJoke.joke));
    }
    setLoading(false);
  };
  useEffect(() => {
    async function fetchJoke() {
      setCurrentJoke(await getRandomJoke());
      setLoading(false);
    }
    fetchJoke();
  }, [nextBool]);
  return (
    <div className="cont">
      <div className="brows">
        <button
          disabled={!currentJoke}
          className="translate"
          onClick={() => {
            setShowTranslated((prev) => !prev);
            onTranslateClick();
          }}
        >
          {showTranslated ? "Original" : "Translate"}
        </button>
        <span>
          {loading
            ? "Loading..."
            : !showTranslated
              ? currentJoke.joke
              : translateResult}
        </span>
        <div className="brows-buttons">
          <button
            disabled={loading}
            onClick={() => {
              setNextBool((prev) => !prev);
              setLiked(false);
              setTranslateResult("");
              setShowTranslated(false);
              setLoading(true);
            }}
          >
            Next Joke
          </button>
          <button
            disabled={loading}
            className="like"
            onClick={() => {
              if (!liked) {
                addId(currentJoke.id);
                setLiked(true);
              } else {
                removeId(currentJoke.id);
                setLiked(false);
              }
            }}
          >
            {liked ? <BookmarkFilledIcon/> : <BookmarkEmptyIcon/>}
          </button>
        </div>
      </div>
      <span className="notice">
        *Notice: You might miss the punch if you translate the joke 🥁
      </span>
    </div>
  );
}

export default Brows;
