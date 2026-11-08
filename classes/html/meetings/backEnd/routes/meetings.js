const express = require("express");
const {
  read,
  readAll,
  add,
  edit,
  remove,
} = require("../controllers/meetings.js");

const router = new express.Router();

router.get("/", async (req, res) => {
  try {
    const result = await readAll(req.query);
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
    const meeting = req.body;
    const result = await add(meeting);
    res.status(201).json({ success: true, result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.toString() });
  }
});

router.patch("/:id", async (req, res) => {
  try {
    const id = req.params.id;
    const meeting = req.body;
    const result = await edit(id, meeting);
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
      res.status(404).json({ success: false, error: "Not found" });
    } else {
      res.status(200).json({ success: true, result });
    }
  } catch (err) {
    res.status(500).json({ success: false, error: err.toString() });
  }
});

module.exports = router;
