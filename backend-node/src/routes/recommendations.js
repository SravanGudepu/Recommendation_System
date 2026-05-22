const express = require("express");
const router = express.Router();
const pool = require("../db/postgres");

router.get("/", async (req, res) => {
    try {
        const { user_id, product_id } = req.query;

        if(!user_id || !product_id) {
            return res.status(400).json({error: "user_id and product_id are required" });     
        }

        // Get clicked/context product
        const productResult = await pool.query(
            "SELECT * FROM products WHERE product_id = $1",
            [product_id]
        );

        if (productResult.rows.length === 0) {
            return res.status(404).json({ error: "Product not found" });
        }

        const contextProduct = productResult.rows[0];

        // Simple candidate generation: same category, in stock, excluding clicked product
        const candidatesResult = await pool.query(
            `
            SELECT * FROM products
            WHERE category = $1
            AND inventory_status != 'out_of_stock'
            AND product_id != $2
            ORDER BY popularity_score DESC, rating DESC
            LIMIT 10;
            `,
            [contextProduct.category, product_id]
        );

        res.json({
            user_id,
            context_product: contextProduct,
            recommendations: candidatesResult.rows,
        });
    } catch (error) {
        console.error("Error getting recommendations:", error.message);
        res.status(500).json({ error: "Failed to get recommendations"});
    }
});

module.exports = router;