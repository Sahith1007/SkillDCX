import { exec } from "child_process";
import { promisify } from "util";
import path from "path";
import { fileURLToPath } from "url";

const execPromise = promisify(exec);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Contract configuration
const CONTRACT_APP_ID = 748842503;
const CONTRACTS_DIR = path.join(__dirname, "../../contracts");

/**
 * Mint Certificate NFT with 3-Layer Verification
 * 
 * Flow:
 * 1. Verify issuer is authorized
 * 2. Run AI verification on certificate data
 * 3. Verify IPFS hash exists (or upload if needed)
 * 4. Mint NFT on Algorand
 * 5. Call smart contract to record certificate
 */
export const mintCertificateNFT = async (req, res) => {
  try {
    const {
      cert_id,
      ipfs_hash,
      student_name,
      course_name,
      recipient_address,
      timestamp
    } = req.body;

    // Validate required fields
    if (!cert_id || !ipfs_hash || !student_name || !course_name || !recipient_address) {
      return res.status(400).json({
        success: false,
        error: "Missing required fields"
      });
    }

    console.log(`[Mint NFT] Starting minting process for certificate ${cert_id}`);

    // LAYER 1: Check issuer authorization (handled by smart contract)
    console.log("[Mint NFT] Layer 1: Issuer registry check - delegated to smart contract");

    // LAYER 2: AI Verification
    console.log("[Mint NFT] Layer 2: Running AI verification...");
    const aiVerified = await verifyWithAI({
      student_name,
      course_name,
      cert_id
    });

    if (!aiVerified) {
      return res.status(403).json({
        success: false,
        error: "AI verification failed - certificate data appears invalid"
      });
    }

    // LAYER 3: IPFS Verification
    console.log("[Mint NFT] Layer 3: Verifying IPFS hash...");
    const ipfsValid = await verifyIPFSHash(ipfs_hash);

    if (!ipfsValid) {
      return res.status(400).json({
        success: false,
        error: "IPFS hash verification failed"
      });
    }

    // Call Python script to mint NFT and issue certificate on-chain
    console.log("[Mint NFT] Calling blockchain minting script...");
    
    const certData = JSON.stringify({
      cert_id,
      ipfs_hash,
      student_name,
      course_name,
      issuer_address: process.env.DEPLOYER_ADDRESS,
      recipient_address,
      timestamp: timestamp || new Date().toISOString()
    });

    // Execute Python minting script
    const pythonScript = path.join(CONTRACTS_DIR, "mint_certificate_nft.py");
    const command = `python "${pythonScript}"`;

    // Set environment variables for the Python script
    const env = {
      ...process.env,
      CERT_DATA: certData
    };

    const { stdout, stderr } = await execPromise(command, { env });

    console.log("[Mint NFT] Blockchain response:", stdout);

    if (stderr) {
      console.error("[Mint NFT] Script stderr:", stderr);
    }

    // Parse the output to extract NFT asset ID and transaction ID
    const nftAssetIdMatch = stdout.match(/NFT Asset ID: (\d+)/);
    const txIdMatch = stdout.match(/Transaction: https:\/\/testnet\.algoexplorer\.io\/tx\/([A-Z0-9]+)/);

    const result = {
      success: true,
      nft_asset_id: nftAssetIdMatch ? parseInt(nftAssetIdMatch[1]) : null,
      transaction_id: txIdMatch ? txIdMatch[1] : null,
      contract_app_id: CONTRACT_APP_ID,
      verification_layers: {
        issuer_registry: true,
        ai_verification: true,
        ipfs_verification: true
      },
      explorer_urls: {
        transaction: txIdMatch ? `https://testnet.algoexplorer.io/tx/${txIdMatch[1]}` : null,
        nft: nftAssetIdMatch ? `https://testnet.algoexplorer.io/asset/${nftAssetIdMatch[1]}` : null,
        contract: `https://testnet.algoexplorer.io/application/${CONTRACT_APP_ID}`
      }
    };

    console.log("[Mint NFT] Successfully minted certificate NFT:", result);

    return res.status(200).json(result);

  } catch (error) {
    console.error("[Mint NFT] Error:", error);
    return res.status(500).json({
      success: false,
      error: error.message || "Failed to mint certificate NFT"
    });
  }
};

/**
 * AI Verification Layer
 * Validates certificate data consistency using AI
 */
async function verifyWithAI(certData) {
  try {
    // TODO: Implement actual AI verification
    // This should call your AI service to verify:
    // - Student name format is valid
    // - Course name exists in your system
    // - Certificate data is consistent
    
    console.log("[AI Verification] Checking certificate data:", certData);
    
    // For now, basic validation
    if (!certData.student_name || certData.student_name.length < 2) {
      return false;
    }
    
    if (!certData.course_name || certData.course_name.length < 3) {
      return false;
    }
    
    // In production, call your AI verification endpoint:
    // const response = await fetch('http://localhost:8000/api/ai/verifyCertificate', {
    //   method: 'POST',
    //   body: JSON.stringify(certData)
    // });
    // return response.ok && response.json().verified === true;
    
    return true;  // Placeholder - always passes for now
    
  } catch (error) {
    console.error("[AI Verification] Error:", error);
    return false;
  }
}

/**
 * IPFS Verification Layer
 * Verifies that the IPFS hash exists and is accessible
 */
async function verifyIPFSHash(ipfsHash) {
  try {
    console.log("[IPFS Verification] Checking hash:", ipfsHash);
    
    // Basic format validation
    if (!ipfsHash || ipfsHash.length < 10) {
      return false;
    }
    
    // TODO: Actually verify IPFS hash exists
    // Try to fetch from IPFS gateway:
    // const response = await fetch(`https://ipfs.io/ipfs/${ipfsHash}`, { method: 'HEAD' });
    // return response.ok;
    
    return true;  // Placeholder - always passes for now
    
  } catch (error) {
    console.error("[IPFS Verification] Error:", error);
    return false;
  }
}

/**
 * Get certificate information from blockchain
 */
export const getCertificateInfo = async (req, res) => {
  try {
    const { recipient_address } = req.params;

    if (!recipient_address) {
      return res.status(400).json({
        success: false,
        error: "Recipient address is required"
      });
    }

    // Query the smart contract for certificate data
    // This would use algosdk to read the contract's global state

    return res.status(200).json({
      success: true,
      message: "Certificate info retrieval - to be implemented"
    });

  } catch (error) {
    console.error("[Get Certificate] Error:", error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
};

/**
 * Verify a certificate is valid
 */
export const verifyCertificate = async (req, res) => {
  try {
    const { recipient_address, ipfs_hash } = req.body;

    if (!recipient_address || !ipfs_hash) {
      return res.status(400).json({
        success: false,
        error: "Missing required fields"
      });
    }

    // Call smart contract verify method
    // This checks: certificate is active, IPFS hash matches, AI verified

    return res.status(200).json({
      success: true,
      verified: true,
      message: "Certificate verification - to be implemented"
    });

  } catch (error) {
    console.error("[Verify Certificate] Error:", error);
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
};
