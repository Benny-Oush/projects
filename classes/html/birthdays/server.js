const express = require("express");
const birthdays = require("./collection");

const app = express();
const userRoutes = require('./router')
app.use(express.json())

app.use('/birthdays', userRoutes);

app.get("/", (req, res) => {
  res.send("Ahoy");
});

app.listen(3000, () => console.log("Listening on port 3000"));
