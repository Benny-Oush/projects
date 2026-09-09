const express = require("express");

const app = express();

// Use this to serve static files from the public folder
app.use(express.static("./public"));
app.use(express.json());

const visitors = [];
app.get("/", (req, res) => {
  res.send(`
    <a href="/sod">See the secret</a><br>
    <p>The folowing have visited the name page:</p>
    <input id="name-input" type="text" placeholder="Enter a name:">
    <button id="name-button">Add</button>
    <ol>${visitors.map((visitor) => `<li>${visitor}</li>`).join("")}</ol>
    <script src="/script.js"></script>
`);
});

let visits = 0;

app.get("/sod", (req, res) => {
  visits++;
  res.send(`
        you've been here ${visits} times
        The secret is 🫴 6 7 🫴
        <br>
        <a href="/">Go Back</a>
        `);
});

app.get("/name/:txt", (req, res) => {
  const name = req.params.txt;
  if (!visitors.includes(name)) {
    visitors.push(name);
  }
  res.send(`
        Hello, ${name}!
        <br>
        <a href="/">HOME</a>
    `);
});

app.get("/names", (req, res) => {
  res.json({ success: true, names: visitors });
});

app.post("/names", (req, res) => {
  const { name } = req.body;
  if (!visitors.includes(name)) {
    res.json({ success: true, name: name });
    visitors.push(name)
  } else {
    res.json({ success: false, error: "Name already exists" });
  }
});

app.listen(3000, () => {
  console.log("Listening to port 3000");
});
