const express = require("express");

const mongoose = require('mongoose')

const app = express();
const mongoURL = 'mongodb://localhost:27017/library'
mongoose.connect(mongoURL)

app.get("/ping", (req, res) => res.send("pong"));

app.listen(3000, () => console.log("Listening on port 3000"));