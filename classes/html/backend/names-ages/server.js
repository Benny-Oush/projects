const express = require("express");
const app = express();

app.use(express.static("./public"));
app.use(express.json());

const visitors = [];
const ages = [];

app.get("/", (req, res) => {
  res.send(`
    <input type="text" id="name-input" placeholder="Enter a name:" value="Benny"><br><br>
    <input type="number" id="age-input" min="1" max="99" value="21" placeholder="Age:"><br><br>
    <button id="add-button">Add</button><br><br>
    <p>The folowing have visited here:</p>
    <table>
    </table>
    <script src="script.js"></script>
    `);
});

app.get("/names", (req, res) => {
  res.json({ success: true, visitors: visitors.map((visitor, index) => ({ name: visitor, age: ages[index]})) });
});

app.post("/names", (req, res) => {
  const { name, age } = req.body;
  if (!visitors.some((visitor, index) => visitor === name && ages[index] === age)) {
    res.json({
      success: true,
      visitor: {
        name: name,
        age: age,
      },
    });
    visitors.push(name);
    ages.push(age);
  } else {
    res.json({ success: false, error: "Visitor already exists" });
  }
});

app.listen(3000, () => {
    console.log("Listening to port 3000");
})
