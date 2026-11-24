async function getRandomJoke() {
  const response = await fetch("https://icanhazdadjoke.com/", {
    headers: {
      Accept: "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Joke request failed: ${response.status}`);
  }
  return response.json();
}

async function getJokeById(id) {
  const response = await fetch(`https://icanhazdadjoke.com/j/${id}`, {
    headers: {
      Accept: "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`Joke Request failed: ${response.status}`);
  }
  return response.json();
}

export { getRandomJoke, getJokeById };
