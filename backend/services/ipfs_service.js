import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';

const PINATA_API_KEY = process.env.PINATA_API_KEY;
const PINATA_SECRET_KEY = process.env.PINATA_SECRET_KEY;

/**
 * Upload certificate metadata to IPFS via Pinata
 */
export async function uploadToIPFS(certificateData) {
  try {
    const data = JSON.stringify({
      name: `Certificate-${certificateData.cert_id}`,
      description: `Certificate for ${certificateData.student_name}`,
      image: certificateData.image_url || "",
      attributes: [
        { trait_type: "Student", value: certificateData.student_name },
        { trait_type: "Course", value: certificateData.course_name },
        { trait_type: "Issuer", value: certificateData.issuer_name },
        { trait_type: "Date", value: certificateData.issue_date },
        { trait_type: "Verified", value: "true" },
        { trait_type: "AI Confidence", value: certificateData.ai_confidence?.toString() || "0" }
      ]
    });

    const response = await axios.post(
      'https://api.pinata.cloud/pinning/pinJSONToIPFS',
      data,
      {
        headers: {
          'Content-Type': 'application/json',
          'pinata_api_key': PINATA_API_KEY,
          'pinata_secret_api_key': PINATA_SECRET_KEY
        }
      }
    );

    return {
      success: true,
      ipfsHash: response.data.IpfsHash,
      ipfsUrl: `ipfs://${response.data.IpfsHash}`
    };
  } catch (error) {
    console.error('IPFS Upload Error:', error.response?.data || error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Upload certificate file (PDF/PNG) to IPFS via Pinata
 */
export async function uploadFileToIPFS(filePath) {
  try {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));

    const response = await axios.post(
      'https://api.pinata.cloud/pinning/pinFileToIPFS',
      formData,
      {
        maxBodyLength: Infinity,
        headers: {
          ...formData.getHeaders(),
          'pinata_api_key': PINATA_API_KEY,
          'pinata_secret_api_key': PINATA_SECRET_KEY
        }
      }
    );

    return {
      success: true,
      ipfsHash: response.data.IpfsHash,
      ipfsUrl: `https://gateway.pinata.cloud/ipfs/${response.data.IpfsHash}`
    };
  } catch (error) {
    console.error('File Upload Error:', error.response?.data || error.message);
    return {
      success: false,
      error: error.message
    };
  }
}
