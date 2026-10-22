const Reader = require("../models/readers.js");
const Book = require("../models/books.js");

async function read(id) {
  return await Reader.findById(id).populate("borrowed_books");
}

async function readMany(options) {
  return await Reader.find(options);
}

async function add(reader) {
  const newReader = new Reader(reader);
  await newReader.save();
  return newReader;
}

async function edit(id, reader) {
  delete reader.borrowed_books;
  const updatedReader = await Reader.findByIdAndUpdate(id, reader, {
    new: true,
    runValidators: true,
  });
  return updatedReader;
}

async function remove(id) {
  const reader = await Reader.findById(id);
  if (!reader) {
    return;
  }
  const borrowed_books = reader.borrowed_books;
  for (let i = 0; i < borrowed_books.length; i++) {
    await returnBook(id, borrowed_books[i]);
  }
  return await Reader.findByIdAndDelete(id);
}

async function borrowBook(reader_id, book_id) {
  const reader = await Reader.findById(reader_id);
  if (!reader || reader.borrowed_books.length >= reader.max_borrowing) {
    return;
  }
  const UpdatedBook = await Book.findOneAndUpdate(
    { _id: book_id, is_borrowed: false },
    { $set: { is_borrowed: true } },
    { new: true },
  );
  if (!UpdatedBook) {
    return;
  }
  await Reader.updateOne(
    { _id: reader_id },
    { $addToSet: { borrowed_books: book_id } },
  );

  return await read(reader_id);
}

async function returnBook(reader_id, book_id) {
  const book = await Book.findById(book_id);
  if (!book || !book.is_borrowed) {
    return;
  }
  const reader = await Reader.findById(reader_id);
  if (!reader) {
    return;
  }
  const hasBook = reader.borrowed_books.some(
    (bId) => bid.toString() === book_id.toString(),
  );
  if (!hasBook) {
    return;
  }

  const UpdatedBook = await Book.findOneAndUpdate(
    { _id: book_id, is_borrowed: true },
    { $set: { is_borrowed: false } },
    { new: true },
  );
  if (!UpdatedBook) {
    return
  }
  await Reader.updateOne(
    { _id: reader_id },
    { $pull: { borrowed_books: book_id } },
  );

  return await read(reader_id);
}

module.exports = {
  read,
  readMany,
  add,
  edit,
  remove,
  borrowBook,
  returnBook,
};
