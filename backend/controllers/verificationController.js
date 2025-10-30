import { exec } from "child_process";
import { promisify } from "util";
import path from "path";
import { fileURLToPath } from "url";

const execPromise = promisify(exec);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// In-memory queue (use database in production)
const verificationQueue = [];
const verifiedCertificates = new Map();

// Payment contract configuration
const PAYMENT_CONTRACT_APP_ID = null; // Set after deploying payment contract
const INSTANT_VERIFICATION_FEE = 1; // 1 ALGO
const CONTRACTS_DIR = path.join(__dirname, "../../contracts");

/**
 * Request Certificate Minting
 * 
 * Two options:
 * - Free (normal): Goes to manual verification queue
 * - Paid (instant): Skips queue if payment confirmed
 */
export const requestCertificateMinting = async (req, res) => {
  try {
    const {
      cert_id,
      ipfs_hash,
      student_name,
      course_name,
      recipient_address,
      timestamp,
      instant_verification = false,
      payment_tx_id = null
    } = req.body;

    // Validate required fields
    if (!cert_id || !ipfs_hash || !student_name || !course_name || !recipient_address) {
      return res.status(400).json({
        success: false,
        error: "Missing required fields"
      });
    }

    console.log(`[Verification Request] Certificate ${cert_id}, Instant: ${instant_verification}`);

    // Run basic 3-layer verification
    const aiVerified = await verifyWithAI({ student_name, course_name, cert_id });
    const ipfsValid = await verifyIPFSHash(ipfs_hash);

    if (!aiVerified || !ipfsValid) {
      return res.status(400).json({
        success: false,
        error: "Certificate failed automated verification"
      });
    }

    const certData = {
      cert_id,
      ipfs_hash,
      student_name,
      course_name,
      recipient_address,
      timestamp: timestamp || new Date().toISOString(),
      created_at: new Date().toISOString(),
      ai_verified: true,
      ipfs_verified: true
    };

    // Check if instant verification requested
    if (instant_verification) {
      // Verify payment
      if (!payment_tx_id) {
        return res.status(400).json({
          success: false,
          error: "Payment transaction ID required for instant verification"
        });
      }

      // Verify payment on blockchain
      const paymentVerified = await verifyPaymentTransaction(payment_tx_id, recipient_address);

      if (!paymentVerified) {
        return res.status(400).json({
          success: false,
          error: "Payment verification failed"
        });
      }

      // Mark as manually verified (paid for instant)
      certData.manual_verified = true;
      certData.verification_type = "instant_paid";

      // Mint immediately
      console.log("[Instant Verification] Minting certificate immediately...");
      
      const mintResult = await mintCertificateNFT(certData);

      return res.status(200).json({
        success: true,
        type: "instant",
        ...mintResult,
        message: "Certificate minted instantly! 🚀"
      });

    } else {
      // Add to manual verification queue
      certData.manual_verified = false;
      certData.verification_type = "pending_manual";
      certData.queue_position = verificationQueue.length + 1;

      verificationQueue.push(certData);

      console.log(`[Queue] Added certificate ${cert_id} to verification queue (position ${certData.queue_position})`);

      return res.status(202).json({
        success: true,
        type: "queued",
        cert_id,
        queue_position: certData.queue_position,
        estimated_time: "1-2 business days",
        message: "Certificate added to verification queue. You will be notified when it's ready."
      });
    }

  } catch (error) {
    console.error("[Verification Request] Error:", error);
    return res.status(500).json({
      success: false,
      error: error.message || "Failed to process verification request"
    });
  }
};

/**
 * Get Verification Queue Status
 */
export const getQueueStatus = async (req, res) => {
  try {
    const { cert_id } = req.params;

    if (cert_id) {
      // Get specific certificate status
      const cert = verificationQueue.find(c => c.cert_id === cert_id);
      
      if (!cert) {
        // Check if already verified
        if (verifiedCertificates.has(cert_id)) {
          return res.status(200).json({
            success: true,
            status: "completed",
            ...verifiedCertificates.get(cert_id)
          });
        }

        return res.status(404).json({
          success: false,
          error: "Certificate not found in queue"
        });
      }

      return res.status(200).json({
        success: true,
        status: "pending",
        ...cert
      });
    }

    // Return entire queue (admin only)
    return res.status(200).json({
      success: true,
      queue_length: verificationQueue.length,
      queue: verificationQueue
    });

  } catch (error) {
    console.error("[Queue Status] Error:", error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
};

/**
 * Manually Verify Certificate (Admin)
 * Called by admin/verifier to approve queued certificate
 */
export const manuallyVerifyCertificate = async (req, res) => {
  try {
    const { cert_id, approved } = req.body;

    if (!cert_id) {
      return res.status(400).json({
        success: false,
        error: "Certificate ID required"
      });
    }

    // Find certificate in queue
    const certIndex = verificationQueue.findIndex(c => c.cert_id === cert_id);

    if (certIndex === -1) {
      return res.status(404).json({
        success: false,
        error: "Certificate not found in queue"
      });
    }

    const cert = verificationQueue[certIndex];

    if (approved === false) {
      // Reject certificate
      verificationQueue.splice(certIndex, 1);
      
      console.log(`[Manual Verification] Certificate ${cert_id} rejected`);

      return res.status(200).json({
        success: true,
        action: "rejected",
        cert_id
      });
    }

    // Approve and mint
    cert.manual_verified = true;
    cert.verified_at = new Date().toISOString();

    console.log(`[Manual Verification] Certificate ${cert_id} approved. Minting...`);

    // Mint NFT
    const mintResult = await mintCertificateNFT(cert);

    // Remove from queue
    verificationQueue.splice(certIndex, 1);

    // Add to verified map
    verifiedCertificates.set(cert_id, {
      ...mintResult,
      verified_at: cert.verified_at
    });

    console.log(`[Manual Verification] Certificate ${cert_id} minted successfully`);

    return res.status(200).json({
      success: true,
      action: "approved_and_minted",
      ...mintResult
    });

  } catch (error) {
    console.error("[Manual Verification] Error:", error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
};

/**
 * Get Instant Verification Pricing
 */
export const getInstantVerificationPricing = async (req, res) => {
  try {
    return res.status(200).json({
      success: true,
      pricing: {
        instant_verification_fee: INSTANT_VERIFICATION_FEE,
        currency: "ALGO",
        revenue_split: {
          verifier: "60%",
          platform: "40%"
        },
        benefits: [
          "Immediate minting",
          "Skip verification queue",
          "Priority support"
        ]
      }
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
};

/**
 * Helper: Mint Certificate NFT
 */
async function mintCertificateNFT(certData) {
  const pythonScript = path.join(CONTRACTS_DIR, "mint_certificate_nft.py");
  const command = `python "${pythonScript}"`;

  const env = {
    ...process.env,
    CERT_DATA: JSON.stringify(certData)
  };

  const { stdout, stderr } = await execPromise(command, { env });

  if (stderr) {
    console.error("[Mint NFT] stderr:", stderr);
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
      nft: nftAssetIdMatch ? `https://testnet.algoexplorer.io/asset/${nftAssetIdMatch[1]}` : null
    }
  };
}

/**
 * Helper: Verify payment transaction on blockchain
 */
async function verifyPaymentTransaction(txId, senderAddress) {
  try {
    // TODO: Verify payment transaction on Algorand
    // Check:
    // - Transaction exists
    // - Amount >= INSTANT_VERIFICATION_FEE
    // - Receiver is payment contract address
    // - Sender matches user address

    console.log(`[Payment Verification] Verifying transaction ${txId} from ${senderAddress}`);
    
    // Placeholder - implement actual blockchain verification
    return true;

  } catch (error) {
    console.error("[Payment Verification] Error:", error);
    return false;
  }
}

/**
 * Helper: AI verification
 */
async function verifyWithAI(certData) {
  // Basic validation
  if (!certData.student_name || certData.student_name.length < 2) return false;
  if (!certData.course_name || certData.course_name.length < 3) return false;
  
  return true;
}

/**
 * Helper: IPFS verification
 */
async function verifyIPFSHash(ipfsHash) {
  if (!ipfsHash || ipfsHash.length < 10) return false;
  return true;
}
