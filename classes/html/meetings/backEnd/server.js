const express = require("express");
const mongoose = require("mongoose");
const meetingsRouter = require("./routes/meetings.js");

const mongoURL = "mongodb://localhost:27017/meetings";
mongoose.connect(mongoURL);

const app = express();

app.use(express.json());

app.use("/meeting", meetingsRouter);

app.get("/ping", (req, res) => res.send("pong"));

app.listen(3000, () => console.log("Listening on port 3000"));