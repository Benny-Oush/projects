const express = require("express");
const {
  read,
  readMany,
  add,
  edit,
  remove,
  borrowBook,
  returnBook,
} = require("../controllers/readers.js");

const router = new express.Router();

router.get("/", async (req, res) => {
  try {
    const result = await readMany(req.query);
    res.status(200).json({ success: true, result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.toString() });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const id = req.params.id;
    const result = await read(id);
    if (!result) {
      res.status(404).json({ success: false, error: "Not found" });
    } else {
      res.status(200).json({ success: true, result });
    }
  } catch (err) {
    res.status(500).json({ success: false, error: err.toString() });
  }
});

router.post("/", async (req, res) => {
  try {
    const reader = req.body;
    const result = await add(reader);
    res.status(201).json({ success: true, result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.toString() });
  }
});

router.patch("/:id", async (req, res) => {
  try {
    const id = req.params.id;
    const reader = req.body;
    const result = await edit(id, reader);
    if (!result) {
      res.status(404).json({ success: false, error: "Not found" });
    } else {
      res.status(200).json({ success: true, result });
    }
  } catch (err) {
    res.status(404).json({ success: false, error: err.toString() });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const id = req.params.id;
    const result = await remove(id);
    if (!result) {
      return res.status(404).json({ success: false, error: "Not found" });
    }
    res.status(200).json({ success: true, result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.toString() });
  }
});

router.post("/:reader_id/:book_id", async (req, res) => {
  try {
    const readerId = req.params.reader_id;
    const bookId = req.params.book_id;
    const result = await borrowBook(readerId, bookId);
    if (!result) {
      return res
        .status(400)
        .json({ success: false, error: "Cannot borrow book" });
    }
    res.status(200).json({ success: true, result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.toString() });
  }
});

router.delete("/:reader_id/:book_id", async (req, res) => {
  try {
    const readerId = req.params.reader_id;
    const bookId = req.params.book_id;
    const result = await returnBook(readerId, bookId);
    if (!result) {
      return res
        .status(400)
        .json({ success: false, error: "Cannot return book" });
    }
    res.status(200).json({ success: true, result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.toString() });
  }
});


module.exports = router;
