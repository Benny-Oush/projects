const Book = require("../models/books.js");
const Reader = require("../models/readers.js")

async function read(id) {
  return await Book.findById(id);
}

async function readMany(options) {
  return await Book.find(options);
}

async function findReaderByBookId(book_id) {
  return await Reader.find({borrowed_books: book_id}).populate('borrowed_books')
}

async function add(book) {
  const newBook = new Book(book);
  await newBook.save();
  return newBook;
}

async function edit(id, book) {
  const updatedBook = await Book.findByIdAndUpdate(id, book, {
    new: true,
    runValidators: true,
  });
  return updatedBook;
}

async function remove(id) {
  return await Book.findByIdAndDelete(id);
}

module.exports = {
  read,
  readMany,
  add,
  edit,
  remove,
  findReaderByBookId,
};
