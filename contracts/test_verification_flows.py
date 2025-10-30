"""
Comprehensive Test Suite for Instant Verification System

Tests:
1. Smoke test - Request verification (pending)
2. Manual approval flow
3. Paid instant verification
4. Negative tests (invalid data, unauthorized access)
5. On-chain state verification
"""

import requests
import json
import time
from algosdk import account, mnemonic
from algosdk.v2client import algod
import os

# Configuration
BACKEND_URL = "http://localhost:8000/api"
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
CONTRACT_APP_ID = 748842503

# Test data
TEST_CERT_FREE = {
    "cert_id": "TEST-FREE-001",
    "ipfs_hash": "QmTestFree123456789",
    "student_name": "Alice Johnson",
    "course_name": "Blockchain Development",
    "recipient_address": "HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q",
    "timestamp": "2025-01-30T00:00:00Z"
}

TEST_CERT_INSTANT = {
    "cert_id": "TEST-INSTANT-001",
    "ipfs_hash": "QmTestInstant123456789",
    "student_name": "Bob Smith",
    "course_name": "Web3 Development",
    "recipient_address": "HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q",
    "timestamp": "2025-01-30T00:00:00Z"
}

TEST_CERT_INVALID = {
    "cert_id": "TEST-INVALID-001",
    "ipfs_hash": "FAKE",  # Invalid IPFS hash
    "student_name": "X",  # Too short
    "course_name": "AB",  # Too short
    "recipient_address": "HNTEOSL5NPTVES7GWQ3TXE3FFCTNT337H7ZNEIBO2EAYMZWKN2ZGUL742Q",
}


def print_test_header(test_name):
    """Print formatted test header"""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)


def print_result(success, message):
    """Print test result"""
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status}: {message}")


def test_backend_connectivity():
    """Test 1: Check if backend is running"""
    print_test_header("Backend Connectivity Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/verification/pricing", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Backend is running")
            print(f"  Instant verification fee: {data['pricing']['instant_verification_fee']} ALGO")
            print(f"  Revenue split: {data['pricing']['revenue_split']}")
            return True
        else:
            print_result(False, f"Backend returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_result(False, "Backend is not running")
        print("  → Start backend: cd backend && npm start")
        return False
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_free_verification_request():
    """Test 2: Request free verification (should go to queue)"""
    print_test_header("Free Verification Request (Pending Queue)")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/verification/request",
            json={
                **TEST_CERT_FREE,
                "instant_verification": False
            },
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 202 and data.get("success"):
            print_result(True, "Certificate added to queue")
            print(f"  Certificate ID: {data.get('cert_id')}")
            print(f"  Queue position: #{data.get('queue_position')}")
            print(f"  Estimated time: {data.get('estimated_time')}")
            return data.get('cert_id')
        else:
            print_result(False, f"Unexpected response: {data}")
            return None
            
    except Exception as e:
        print_result(False, f"Error: {e}")
        return None


def test_queue_status(cert_id):
    """Test 3: Check queue status"""
    print_test_header("Queue Status Check")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/verification/queue/{cert_id}",
            timeout=5
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print_result(True, "Queue status retrieved")
            print(f"  Status: {data.get('status')}")
            print(f"  Certificate ID: {data.get('cert_id')}")
            print(f"  Queue position: #{data.get('queue_position', 'N/A')}")
            return True
        else:
            print_result(False, f"Failed to get status: {data}")
            return False
            
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_manual_approval(cert_id):
    """Test 4: Manual approval by admin"""
    print_test_header("Manual Approval Flow")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/verification/manual",
            json={
                "cert_id": cert_id,
                "approved": True
            },
            timeout=30
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print_result(True, "Certificate approved and minted")
            print(f"  NFT Asset ID: {data.get('nft_asset_id')}")
            print(f"  Transaction ID: {data.get('transaction_id')}")
            
            if data.get('explorer_urls', {}).get('nft'):
                print(f"  Explorer: {data['explorer_urls']['nft']}")
            
            return data.get('nft_asset_id')
        else:
            print_result(False, f"Approval failed: {data}")
            return None
            
    except Exception as e:
        print_result(False, f"Error: {e}")
        return None


def test_instant_verification():
    """Test 5: Instant verification with payment"""
    print_test_header("Instant Verification (Paid)")
    
    try:
        # Simulate payment transaction
        mock_payment_tx = f"MOCK_PAYMENT_{int(time.time())}"
        
        response = requests.post(
            f"{BACKEND_URL}/verification/request",
            json={
                **TEST_CERT_INSTANT,
                "instant_verification": True,
                "payment_tx_id": mock_payment_tx
            },
            timeout=30
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            print_result(True, "Instant verification successful")
            print(f"  Type: {data.get('type')}")
            print(f"  NFT Asset ID: {data.get('nft_asset_id')}")
            print(f"  Transaction ID: {data.get('transaction_id')}")
            print(f"  Message: {data.get('message')}")
            return data.get('nft_asset_id')
        else:
            print_result(False, f"Instant verification failed: {data}")
            return None
            
    except Exception as e:
        print_result(False, f"Error: {e}")
        return None


def test_invalid_certificate():
    """Test 6: Submit invalid certificate (should fail AI verification)"""
    print_test_header("Negative Test - Invalid Certificate")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/verification/request",
            json={
                **TEST_CERT_INVALID,
                "instant_verification": False
            },
            timeout=10
        )
        
        data = response.json()
        
        # Should fail validation
        if response.status_code != 200 or not data.get("success"):
            print_result(True, "Invalid certificate rejected as expected")
            print(f"  Error: {data.get('error', 'Validation failed')}")
            return True
        else:
            print_result(False, "Invalid certificate was accepted (should have been rejected)")
            return False
            
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_unauthorized_approval():
    """Test 7: Try to approve from non-admin (should fail)"""
    print_test_header("Negative Test - Unauthorized Approval")
    
    # Note: This test requires authentication middleware in production
    print("  ⚠️  TODO: Implement admin authentication middleware")
    print("  ℹ️  Currently all approval requests are allowed")
    print_result(True, "Test skipped - requires auth implementation")
    return True


def verify_on_chain_state(app_id):
    """Test 8: Check on-chain state"""
    print_test_header("On-Chain State Verification")
    
    try:
        client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        app_info = client.application_info(app_id)
        
        if 'params' in app_info:
            print_result(True, "Contract exists on-chain")
            print(f"  App ID: {app_id}")
            
            global_state = app_info.get('params', {}).get('global-state', [])
            print(f"  Global state entries: {len(global_state)}")
            
            # Look for key metrics
            for state in global_state:
                key_b64 = state.get('key', '')
                value = state.get('value', {})
                
                # Try to decode key
                try:
                    import base64
                    key = base64.b64decode(key_b64).decode('utf-8')
                    
                    if key in ['total_issuers', 'total_certs', 'total_certificates']:
                        val_type = value.get('type')
                        val_data = value.get('uint', value.get('bytes', 0))
                        print(f"  {key}: {val_data}")
                except:
                    pass
            
            return True
        else:
            print_result(False, "Contract not found on-chain")
            return False
            
    except Exception as e:
        print_result(False, f"Error querying blockchain: {e}")
        return False


def verify_nft_exists(asset_id):
    """Test 9: Verify NFT exists on blockchain"""
    print_test_header("NFT Asset Verification")
    
    if not asset_id:
        print_result(False, "No asset ID provided")
        return False
    
    try:
        client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        asset_info = client.asset_info(asset_id)
        
        if 'params' in asset_info:
            params = asset_info['params']
            print_result(True, "NFT exists on blockchain")
            print(f"  Asset ID: {asset_id}")
            print(f"  Name: {params.get('name', 'N/A')}")
            print(f"  Unit: {params.get('unit-name', 'N/A')}")
            print(f"  Total: {params.get('total', 0)}")
            print(f"  URL: {params.get('url', 'N/A')}")
            print(f"  Explorer: https://testnet.algoexplorer.io/asset/{asset_id}")
            return True
        else:
            print_result(False, "NFT not found")
            return False
            
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def run_all_tests():
    """Run complete test suite"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "INSTANT VERIFICATION TEST SUITE" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
    
    # Test 1: Backend connectivity
    results["total"] += 1
    if test_backend_connectivity():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Backend not running. Start it first:")
        print("   cd backend && npm start\n")
        return results
    
    # Test 2: Free verification request
    results["total"] += 1
    cert_id = test_free_verification_request()
    if cert_id:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 3: Queue status
    if cert_id:
        results["total"] += 1
        if test_queue_status(cert_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Test 4: Manual approval
    if cert_id:
        results["total"] += 1
        nft_id = test_manual_approval(cert_id)
        if nft_id:
            results["passed"] += 1
            
            # Test 9: Verify NFT exists
            results["total"] += 1
            if verify_nft_exists(nft_id):
                results["passed"] += 1
            else:
                results["failed"] += 1
        else:
            results["failed"] += 1
    
    # Test 5: Instant verification
    results["total"] += 1
    instant_nft_id = test_instant_verification()
    if instant_nft_id:
        results["passed"] += 1
        
        # Verify instant NFT
        results["total"] += 1
        if verify_nft_exists(instant_nft_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
    else:
        results["failed"] += 1
    
    # Test 6: Invalid certificate
    results["total"] += 1
    if test_invalid_certificate():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 7: Unauthorized approval
    results["total"] += 1
    results["skipped"] += 1  # Skipped until auth is implemented
    test_unauthorized_approval()
    
    # Test 8: On-chain state
    results["total"] += 1
    if verify_on_chain_state(CONTRACT_APP_ID):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests:   {results['total']}")
    print(f"✓ Passed:      {results['passed']}")
    print(f"✗ Failed:      {results['failed']}")
    print(f"⚠ Skipped:     {results['skipped']}")
    print(f"Success Rate:  {(results['passed']/results['total']*100):.1f}%")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    try:
        results = run_all_tests()
        
        # Exit with appropriate code
        if results['failed'] > 0:
            exit(1)
        else:
            exit(0)
            
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
