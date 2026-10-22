const express = require("express");
const mongoose = require("mongoose");
const booksRouter = require("./routes/books.js");
const readersRouter = require("./routes/readers.js")

const app = express();

const mongoURL = "mongodb://localhost:27017/library";
mongoose.connect(mongoURL);

app.use(express.json())

app.use("/books", booksRouter);
app.use("/readers", readersRouter)

app.get("/ping", (req, res) => res.send("pong"));

app.listen(3000, () => console.log("Listening on port 3000"));