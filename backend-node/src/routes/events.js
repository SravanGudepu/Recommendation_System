const express = require("express");
const router = express.Router();
const pool = require("../db/postgres");

router.post("/", async (requestAnimationFrame, res) => {
    try {
        const { user_id, product_id, event_type, session_id, source} = req.body;

        if (!user_id || !product_id || !event_type) {
            return res.status(400).json({ error: "user_id, product_id, and event_type are required"});         
        }

        const query = `
            INSERT INTO events (user_id, product_id, event_type, session_id, source)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *;
        `;

        const values = [
            user_id,
            product_id,
            event_type,
            session_id || null,
            source || "app",
        ];

        const result = await pool.query(query, values);

        res.status(201).json({
            message: "Event saved successfully",
            event: result.rows[0],
        });
    } catch (error) {
        console.error("Error saving event:", error);
        res.status(500).json({ error: "An error occurred while saving the event" });
    }
    });

    module.exports = router;