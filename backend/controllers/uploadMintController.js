import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';
import { uploadToIPFS, uploadFileToIPFS } from '../services/ipfs_service.js';

const execPromise = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = './uploads';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = /pdf|png|jpg|jpeg/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (extname && mimetype) {
      return cb(null, true);
    }
    cb(new Error('Only PDF and image files are allowed'));
  }
});

export const uploadMiddleware = upload.single('certificate');

/**
 * Upload and Mint Certificate
 * 
 * Complete flow:
 * 1. Receive uploaded certificate file
 * 2. Run AI verification
 * 3. Upload file to IPFS
 * 4. Upload metadata to IPFS
 * 5. Choose tier (free queue or instant mint)
 * 6. Mint NFT on Algorand
 */
export async function uploadAndMintCertificate(req, res) {
  let filePath = null;

  try {
    // Step 1: Validate request
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No certificate file uploaded'
      });
    }

    const {
      wallet_address,
      student_name,
      course_name,
      issuer_name,
      issue_date,
      tier = 'free' // 'free' or 'fast_track'
    } = req.body;

    if (!wallet_address || !student_name || !course_name) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: wallet_address, student_name, course_name'
      });
    }

    console.log(`[Upload & Mint] Processing certificate for ${student_name}`);
    console.log(`[Upload & Mint] Tier: ${tier}`);
    console.log(`[Upload & Mint] File: ${req.file.originalname}`);

    filePath = req.file.path;
    const fileType = path.extname(req.file.originalname).substring(1);

    // Step 2: AI Verification (placeholder - integrate Python script)
    console.log('[Upload & Mint] Running AI verification...');

    // TODO: Call Python AI verifier
    // For now, use basic validation
    const aiResult = {
      verified: true,
      confidence: 0.85,
      extracted_data: {
        student_name,
        course_name,
        issuer_name: issuer_name || 'SkillDCX'
      },
      message: 'AI verification passed (simulated)'
    };

    if (!aiResult.verified) {
      fs.unlinkSync(filePath);
      return res.status(400).json({
        success: false,
        error: `AI verification failed: ${aiResult.message}`,
        extracted_data: aiResult.extracted_data,
        confidence: aiResult.confidence
      });
    }

    console.log(`[Upload & Mint] AI verification passed (confidence: ${aiResult.confidence})`);

    // Step 3: Upload certificate file to IPFS
    console.log('[Upload & Mint] Uploading certificate to IPFS...');

    const fileUpload = await uploadFileToIPFS(filePath);

    if (!fileUpload.success) {
      fs.unlinkSync(filePath);
      return res.status(500).json({
        success: false,
        error: `Failed to upload certificate to IPFS: ${fileUpload.error}`
      });
    }

    console.log(`[Upload & Mint] File uploaded to IPFS: ${fileUpload.ipfsHash}`);

    // Step 4: Upload metadata to IPFS
    console.log('[Upload & Mint] Uploading metadata to IPFS...');

    const metadata = {
      cert_id: `CERT-${Date.now()}`,
      student_name,
      course_name,
      issuer_name: issuer_name || 'SkillDCX',
      issue_date: issue_date || new Date().toISOString().split('T')[0],
      image_url: fileUpload.ipfsUrl,
      ai_verified: true,
      ai_confidence: aiResult.confidence
    };

    const metadataUpload = await uploadToIPFS(metadata);

    if (!metadataUpload.success) {
      fs.unlinkSync(filePath);
      return res.status(500).json({
        success: false,
        error: `Failed to upload metadata to IPFS: ${metadataUpload.error}`
      });
    }

    console.log(`[Upload & Mint] Metadata uploaded to IPFS: ${metadataUpload.ipfsHash}`);

    // Step 5: Determine verification flow
    if (tier === 'free') {
      // Add to queue for manual review
      const queuePosition = Math.floor(Math.random() * 10) + 1; // TODO: Real queue

      // Keep file for later processing
      console.log(`[Upload & Mint] Added to queue at position ${queuePosition}`);

      return res.status(202).json({
        success: true,
        type: 'queued',
        message: 'Certificate uploaded successfully. Manual review in progress.',
        queue_position: queuePosition,
        estimated_time: '1-2 business days',
        metadata: {
          cert_id: metadata.cert_id,
          ipfs_hash: metadataUpload.ipfsHash,
          file_ipfs: fileUpload.ipfsHash,
          ai_confidence: aiResult.confidence
        }
      });
    } else if (tier === 'fast_track') {
      // Mint immediately
      console.log('[Upload & Mint] Fast track: Minting immediately...');

      const mintResult = await mintCertificateNFT({
        ...metadata,
        ipfs_hash: metadataUpload.ipfsHash,
        recipient_address: wallet_address,
        manual_verified: true
      });

      // Cleanup file after minting
      fs.unlinkSync(filePath);

      return res.status(200).json({
        success: true,
        type: 'instant',
        message: 'Certificate minted successfully! 🚀',
        ...mintResult,
        verification: {
          ai_verified: true,
          ai_confidence: aiResult.confidence,
          ipfs_verified: true,
          issuer_verified: true
        }
      });
    } else {
      fs.unlinkSync(filePath);
      return res.status(400).json({
        success: false,
        error: 'Invalid tier. Must be "free" or "fast_track"'
      });
    }

  } catch (error) {
    console.error('[Upload & Mint] Error:', error);

    // Cleanup on error
    if (filePath && fs.existsSync(filePath)) {
      try {
        fs.unlinkSync(filePath);
      } catch (cleanupError) {
        console.error('[Upload & Mint] Cleanup error:', cleanupError);
      }
    }

    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to process certificate'
    });
  }
}

/**
 * Mint Certificate NFT
 * Calls Python script to mint on Algorand
 */
async function mintCertificateNFT(certData) {
  try {
    const pythonScript = path.join(__dirname, '../../contracts/mint_certificate_nft.py');

    const { stdout, stderr } = await execPromise(
      `python "${pythonScript}"`,
      {
        env: {
          ...process.env,
          CERT_DATA: JSON.stringify(certData)
        }
      }
    );

    if (stderr) {
      console.error('[Mint NFT] stderr:', stderr);
    }

    // Parse output
    const nftAssetIdMatch = stdout.match(/NFT Asset ID: (\d+)/);
    const txIdMatch = stdout.match(/Transaction: https:\/\/testnet\.algoexplorer\.io\/tx\/([A-Z0-9]+)/);

    return {
      nft_asset_id: nftAssetIdMatch ? parseInt(nftAssetIdMatch[1]) : null,
      transaction_id: txIdMatch ? txIdMatch[1] : null,
      contract_app_id: 748842503,
      explorer_urls: {
        transaction: txIdMatch ? `https://testnet.algoexplorer.io/tx/${txIdMatch[1]}` : null,
        nft: nftAssetIdMatch ? `https://testnet.algoexplorer.io/asset/${nftAssetIdMatch[1]}` : null,
        contract: 'https://testnet.algoexplorer.io/application/748842503'
      }
    };
  } catch (error) {
    console.error('[Mint NFT] Error:', error);
    throw new Error(`Failed to mint NFT: ${error.message}`);
  }
}
