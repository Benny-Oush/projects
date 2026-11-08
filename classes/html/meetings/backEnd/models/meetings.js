const mongoose = require("mongoose");

const schema = new mongoose.Schema({
  title: {
    type: String,
    required: [true, "Title required"],
    minLength: [3, "Title must be at least 3 letters long"],
  },
  date: {
    type: Date,
    required: [true, "Date required"],
  },
  start_hour: {
    type: Number,
    required: [true, "Start hour required"],
    min: 0,
    max: 23,
  },
  end_hour: {
    type: Number,
    required: [true, "End hour required"],
    min: 0,
    max: 23,
  },
  is_online: {
    type: Boolean,
    default: false,
    required: [true, "'is_online' value required"],
  },
  address: {
    type: String,
    minLength: 5,
    required: [true, "Meeting address required"],
  },
});

const model = mongoose.model("meetings", schema);

module.exports = model;
