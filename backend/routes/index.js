import express from "express";
import { simpleAIResponse } from "../controllers/aiController.js";
import { 
  mintCertificateNFT, 
  getCertificateInfo, 
  verifyCertificate 
} from "../controllers/certificateController.js";
import {
  requestCertificateMinting,
  getQueueStatus,
  manuallyVerifyCertificate,
  getInstantVerificationPricing
} from "../controllers/verificationController.js";

const router = express.Router();

// AI routes
router.post("/chat", simpleAIResponse);

// Certificate NFT routes (legacy)
router.post("/certificates/mint", mintCertificateNFT);
router.get("/certificates/:recipient_address", getCertificateInfo);
router.post("/certificates/verify", verifyCertificate);

// Verification routes (new instant verification flow)
router.post("/verification/request", requestCertificateMinting);
router.get("/verification/queue/:cert_id?", getQueueStatus);
router.post("/verification/manual", manuallyVerifyCertificate);
router.get("/verification/pricing", getInstantVerificationPricing);

export default router;
