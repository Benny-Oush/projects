const express = require("express");
const { read, readMany, edit, remove, add } = require("./collection");
const router = new express.Router();

router.get("/", (req, res) => {
    try {
        const result = readMany(req.query)
        res.status(200).json({success: true, result})
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
});

router.get("/:id", (req, res) => {
    try {
        const id = req.params.id
        const result = read(id)
        if (!result) {
            res.status(404).json({saccess: false, error: "Not found"})
        } else {
            res.status(200).json({success: true, result})
        }
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
});

router.post("/", (req, res) => {
    try {
        const {name, birthdate} = req.body;
        if (!name || !birthdate) {
            return res.status(400).json({success: false, error: "Missing parameters"})
        }
        const result = add(name, birthdate)
        res.status(201).json({success: true, result})
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
});

router.patch("/:id", (req, res) => {
    try {
        const id = req.params.id
        const {name, birthdate} = req.body
        if (!name && !birthdate) {
            return res.status(400).json({success: false, error: "Nothing to modify"})
        }
        const result = edit(id, name, birthdate)
        if (!result) {
            res.status(404).json({success: false, error: "Not found"})
        } else {
            res.status(200).json({success: true, result})
        }
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
});

router.delete("/:id", (req, res) => {
    try {
        const id = req.params.id
        const result = remove(id)
        if (!result) {
            return res.status(404).json({success: false, error: "Not found"})
        }
        res.status(200).json({success: true, result})
        
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
});

module.exports = router