import express from 'express';
import { uploadMiddleware, uploadAndMintCertificate } from '../controllers/uploadMintController.js';

const router = express.Router();

/**
 * @route   POST /api/upload/certificate
 * @desc    Upload certificate, verify with AI, upload to IPFS, and mint NFT
 * @access  Public
 * @body    {
 *   certificate: File (PDF/PNG/JPG),
 *   wallet_address: String,
 *   student_name: String,
 *   course_name: String,
 *   issuer_name: String (optional),
 *   issue_date: String (optional, YYYY-MM-DD),
 *   tier: 'free' | 'fast_track'
 * }
 */
router.post('/certificate', uploadMiddleware, uploadAndMintCertificate);

export default router;
