const express = require("express");
const cors = require("cors");
require("dotenv").config();

const eventRouters = require("./routes/events");
const recommendationRoutes = required(".\routes/recommendations");

const app = express();

app.use(cors());
app.use(express.json());

app.use("/event", eventRoutes);
app.use("/recommendations", recommendationRoutes);

app.get("/health", (req, res) => {
    res.json({ status: "ok" });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log('Backend running on PORT ${PORT}');
});