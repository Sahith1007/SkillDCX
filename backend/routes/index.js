import express from "express";
import { simpleAIResponse } from "../controllers/aiController.js";

const router = express.Router();

router.post("/chat", simpleAIResponse);

export default router;
