import { useEffect, useState } from "react";
import { getRandomJoke, getJokeById } from "../utils/jokes.js";
import { addId, removeId, getAllLikedIds } from "../utils/storage.js";
import { translate } from "../utils/translation.js";
import { BookmarkIcon } from "../assets/jsx-assets/bookmark.jsx";

function Brows() {
  const [nextBool, setNextBool] = useState(false);
  const [currentJoke, setCurrentJoke] = useState("");
  const [loading, setLoading] = useState(true);
  const [liked, setLiked] = useState(false);
  const [translateResult, setTranslateResult] = useState("");
  const [showTranslated, setShowTranslated] = useState(false);
  const [showPrev, setShowPrev] = useState(false);
  const [idStack, setIdStack] = useState([]);

  const getPrevJokeId = () => {
    if (idStack.length > 0) {
      const tmp = idStack.slice();
      const prev = tmp.pop();
      setIdStack(tmp);
      return prev;
    }
  };

  const addNewPrevId = (id) => {
    const tmp = idStack.slice();
    tmp.push(id);
    setIdStack(tmp);
  };

  const onTranslateClick = async () => {
    try {
      if (!showTranslated && !translateResult) {
        setLoading(true);
        setTranslateResult(await translate(currentJoke.joke));
      }
    } catch (error) {
      console.error(`Translation failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    async function fetchJoke() {
      let newJoke;
      try {
        if (showPrev) {
          newJoke = await getJokeById(getPrevJokeId());
        } else {
          newJoke = await getRandomJoke();
          if (currentJoke) {
            addNewPrevId(currentJoke.id);
          }
        }
      } catch (error) {
        console.error(`Joke Fatching failed: ${error}`);
      } finally {
        setCurrentJoke(newJoke);
        setShowPrev(false);
        setLoading(false);
        setLiked(!newJoke ? false : getAllLikedIds().includes(newJoke.id));
      }
    }
    fetchJoke();
  }, [nextBool]);
  return (
    <div className="cont">
      <div className="brows">
        <button
          disabled={!currentJoke || loading}
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
          className="prev"
            disabled={loading || idStack.length === 0}
            onClick={() => {
              setNextBool((prev) => {
                if (idStack.length > 0) {
                  setShowPrev(true);
                }
                return !prev;
              });
              setTranslateResult("");
              setShowTranslated(false);
              setLoading(true);
            }}
          >
            ↩
          </button>
          <button
            disabled={loading}
            onClick={() => {
              setNextBool((prev) => !prev);
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
            {liked ? <BookmarkIcon color="yellow" /> : <BookmarkIcon />}
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
