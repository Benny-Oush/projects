const mongoose = require("mongoose");

const schema = new mongoose.Schema({
  title: {
    type: String,
    required: [true, "Title required"],
    minLength: [3, "Title must be at least 3 letters long"],
  },
  author: {
    type: String,
    required: [true, "Author required"],
    minLength: [3, "Author must be at least 3 letters long"],
  },
  publish_year: {
    type: Number,
    required: [true, "Publish year required"],
  },
  is_borrowed: {
    type: Boolean,
    default: false,
  },
  language: {
    type: String,
    enum: ["Hebrew", "English", "Arabic", "French"],
    default: "Hebrew",
  },
});

const model = mongoose.model("books", schema);

module.exports = model