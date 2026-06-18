const express = require("express");
const axios = require("axios");
const router = express.Router();
const pool = require("../db/postgres");

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || "http://localhost:8000";

router.get("/", async (req, res) => {
  try {
    const { user_id, product_id } = req.query;

    if (!user_id || !product_id) {
      return res.status(400).json({
        error: "user_id and product_id are required",
      });
    }

    // 1. Get clicked/context product
    const productResult = await pool.query(
      "SELECT * FROM products WHERE product_id = $1",
      [product_id]
    );

    if (productResult.rows.length === 0) {
      return res.status(404).json({ error: "Product not found" });
    }

    const contextProduct = productResult.rows[0];

    // 2. Candidate generation: same category, in stock, excluding clicked product
    const candidatesResult = await pool.query(
      `
      SELECT 
        product_id,
        name,
        category,
        subcategory,
        brand,
        price::float,
        rating::float,
        popularity_score::float
      FROM products
      WHERE category = $1
        AND inventory_status != 'out_of_stock'
        AND product_id != $2
      ORDER BY popularity_score DESC, rating DESC
      LIMIT 50;
      `,
      [contextProduct.category, product_id]
    );

    const candidateProducts = candidatesResult.rows;

    if (candidateProducts.length === 0) {
      return res.json({
        user_id,
        context_product: contextProduct,
        recommendations: [],
        message: "No candidate products found",
      });
    }

    // 3. Call Python ML inference service
    const mlResponse = await axios.post(`${ML_SERVICE_URL}/rank`, {
      user_id,
      context_product_id: contextProduct.product_id,
      context_category: contextProduct.category,
      context_brand: contextProduct.brand,
      context_price: Number(contextProduct.price),
      candidate_products: candidateProducts,
    });

    const rankedProducts = mlResponse.data.ranked_products;

    // 4. Merge ML scores with full candidate product details
    const productMap = new Map(
      candidateProducts.map((product) => [product.product_id, product])
    );

    const recommendations = rankedProducts
      .map((ranked) => {
        const product = productMap.get(ranked.product_id);
        return {
          ...product,
          ml_score: ranked.score,
        };
      })
      .filter(Boolean)
      .slice(0, 10);

    // 5. Return final ranked recommendations
    res.json({
      user_id,
      context_product: contextProduct,
      recommendations,
      ranking_source: "ml-service",
    });
  } catch (error) {
    console.error("Error getting recommendations:", error.message);

    res.status(500).json({
      error: "Failed to get recommendations",
      details: error.message,
    });
  }
});

module.exports = router;