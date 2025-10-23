import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import routes from "./routes/index.js";

dotenv.config();
const app = express();
const PORT = process.env.PORT || 8000;

app.use(cors());
app.use(express.json());

// Routes
app.use("/api", routes);

app.get("/", (req, res) => {
  res.send("✅ Backend is running");
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://127.0.0.1:${PORT}`);
});
