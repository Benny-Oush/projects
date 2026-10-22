const express = require('express')
const {read, readMany, add, edit, remove, findReaderByBookId} = require('../controllers/books.js')

const router = new express.Router();

router.get('/', async (req, res) => {
    try {
        const result = await readMany(req.query)
        res.status(200).json({success: true, result})
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
});

router.get("/:id", async (req, res) => {
    try {
        const id = req.params.id
        const result = await read(id)
        if (!result) {
            res.status(404).json({success: false, error: "Not found"})
        } else {
            res.status(200).json({success: true, result})
        } 
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
})

router.get("/:id/reader", async (req, res) => {
    try {
        const id = req.params.id
        const result = await findReaderByBookId(id)
        if (!result || result.length === 0) {
            return res.status(404).json({success: false, error: "Not found"})
        }
        res.status(200).json({success: true, result})
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
})

router.post("/", async (req, res) => {
    try {
        const book = req.body
        const result = await add(book)
        res.status(201).json({success: true, result})
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
});

router.patch('/:id', async (req, res) => {
    try {
        const id = req.params.id
        const book = req.body
        const result = await edit(id, book)
        if (!result) {
            res.status(404).json({success: false, error: "Not found"})
        } else {
            res.status(200).json({success: true, result})
        }
    } catch(err) {
        res.status(404).json({success: false, error: err.toString()})
    }
})

router.delete("/:id", async (req, res) => {
    try {
        const id = req.params.id
        const result = await remove(id)
        if (!result) {
            res.status(404).json({success: false, error: "Not found"})
        } else {
            res.status(200).json({success: true, result})
        }
    } catch(err) {
        res.status(500).json({success: false, error: err.toString()})
    }
});

module.exports = router