const express = require("express");
const app = express();
app.use(express.json());

const players = [];
const guests = [];

let clientsCounter = 1;

function isUsernameTaken(name) {
  return (
    players.some((player) => player.details.username === name) ||
    guests.some((guest) => guest.details.username === name)
  );
}

function generateToken() {
  let token = "";
  for (let i = 0; i < 30; i++) {
    token += String(Math.floor(Math.random() * 10));
  }
  return token;
}

app.get("/new/:username", (req, res) => {
  const username = req.params.username.toLowerCase();
  if (isUsernameTaken(username)) {
    res.status(409).json({ ok: false, error: "Username taken" });
    return;
  } else {
    const newClient = {
        status: "",
      details: {
        username: username,
        user_id: String(clientsCounter),
        token: generateToken(),
      },
    };

    clientsCounter++;

    if (players.length >= 2) {
      newClient.status = "guest";
      guests.push(newClient);
      res.json(newClient);
    } else {
      newClient.status = "player";
      players.push(newClient);
      res.json(newClient);
    }
  }
});

app.get("/clients", (req, res) => {
  res.json({players: players.map((player) => player.details.username), guests: guests.map((guest) => guest.details.username)})
})

app.listen(3000, () => {
  console.log("Server listening to port 3000");
});
