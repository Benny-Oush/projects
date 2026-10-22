const mongoose = require("mongoose");

const schema = new mongoose.Schema({
  first_name: {
    type: String,
    required: [true, "First name required"],
    minLength: [3, "First name must be at least 3 letters long"],
  },
  last_name: {
    type: String,
    required: [true, "Last name required"],
    minLength: [3, "Last name must be at least 3 letters long"],
  },
  phone_number: {
    type: String,
    unique: [true, "Phone number already used"],
    required: [true, "Phone number required"],
    match: [/^05[0-9]{8}$/, "Invalid phone number"],
    trim: true,
  },
  id_number: {
    type: String,
    unique: [true, "ID number already used"],
    required: [true, "ID number required"],
    match: [/^[0-9]{9}$/, "Invalid ID number"]
  },
  max_borrowing: {
    type: Number,
    default: 3,
    min: 0,
  },
  borrowed_books: [{
    type: mongoose.ObjectId,
    ref: 'books',
  }]
});

const model = mongoose.model("readers", schema);

module.exports = model;
