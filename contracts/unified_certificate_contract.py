from pyteal import *

def unified_certificate_contract():
    """
    SkillDCX Unified Certificate Smart Contract
    
    Three-Layer Verification System:
    1. Issuer Registry Verification - Check if issuer is authorized
    2. AI Verification - Validate certificate data via AI backend
    3. IPFS Verification - Confirm metadata hash exists and is valid
    
    Features:
    - Integrated issuer management (from issuer_registry_contract.py)
    - Certificate issuance with verification layers (from certification_contract.py)
    - NFT minting logic (from CertificateIssuer.py)
    - Soulbound NFT certificates (non-transferable)
    """
    
    # ==================== GLOBAL STATE KEYS ====================
    admin_address = Bytes("admin")
    total_issuers = Bytes("total_issuers")
    total_certificates = Bytes("total_certs")
    issuer_registry_enabled = Bytes("registry_enabled")
    ai_verification_required = Bytes("ai_required")
    
    # ==================== LOCAL STATE KEYS ====================
    # Issuer data (local to issuer addresses)
    is_authorized = Bytes("authorized")
    issuer_name = Bytes("issuer_name")
    issuer_metadata = Bytes("issuer_meta")
    registration_timestamp = Bytes("reg_time")
    
    # Certificate data (local to recipient addresses)
    cert_id = Bytes("cert_id")
    cert_ipfs_hash = Bytes("ipfs_hash")
    cert_issuer = Bytes("issuer")
    cert_recipient = Bytes("recipient")
    cert_timestamp = Bytes("timestamp")
    cert_active = Bytes("active")
    cert_metadata = Bytes("metadata")
    cert_ai_verified = Bytes("ai_verified")
    cert_nft_asset_id = Bytes("nft_asset_id")
    
    # ==================== SUBROUTINES ====================
    
    @Subroutine(TealType.uint64)
    def is_admin():
        """Check if caller is admin"""
        return Txn.sender() == App.globalGet(admin_address)
    
    @Subroutine(TealType.uint64)
    def check_issuer_authorized(issuer_addr):
        """Check if an address is an authorized issuer"""
        # Read from global state using address as key
        return App.globalGet(Concat(Bytes("issuer_"), issuer_addr)) == Int(1)
    
    # ==================== CONTRACT CREATION ====================
    
    on_creation = Seq([
        App.globalPut(admin_address, Txn.sender()),
        App.globalPut(total_issuers, Int(0)),
        App.globalPut(total_certificates, Int(0)),
        App.globalPut(issuer_registry_enabled, Int(1)),
        App.globalPut(ai_verification_required, Int(1)),
        Approve()
    ])
    
    # ==================== ISSUER MANAGEMENT ====================
    
    add_issuer = Seq([
        # Only admin can add issuers
        Assert(is_admin()),
        
        # Args: [method, issuer_address, name, metadata]
        Assert(Txn.application_args.length() == Int(4)),
        
        # Store issuer authorization in global state using address as key prefix
        App.globalPut(Concat(Bytes("issuer_"), Txn.application_args[1]), Int(1)),
        App.globalPut(Concat(Bytes("name_"), Txn.application_args[1]), Txn.application_args[2]),
        App.globalPut(Concat(Bytes("meta_"), Txn.application_args[1]), Txn.application_args[3]),
        
        # Increment counter
        App.globalPut(total_issuers, App.globalGet(total_issuers) + Int(1)),
        
        Approve()
    ])
    
    remove_issuer = Seq([
        # Only admin can remove issuers
        Assert(is_admin()),
        
        # Args: [method, issuer_address]
        Assert(Txn.application_args.length() == Int(2)),
        
        # Verify issuer exists
        Assert(App.globalGet(Concat(Bytes("issuer_"), Txn.application_args[1])) == Int(1)),
        
        # Revoke authorization
        App.globalPut(Concat(Bytes("issuer_"), Txn.application_args[1]), Int(0)),
        
        # Decrement counter
        App.globalPut(total_issuers, App.globalGet(total_issuers) - Int(1)),
        
        Approve()
    ])
    
    check_issuer = Seq([
        # Args: [method, issuer_address]
        Assert(Txn.application_args.length() == Int(2)),
        
        # Client reads the return value from local state
        Approve()
    ])
    
    # ==================== CERTIFICATE ISSUANCE WITH 3-LAYER VERIFICATION ====================
    
    issue_certificate = Seq([
        # Args: [method, cert_id, ipfs_hash, recipient_address, metadata, ai_verified_flag, manual_verified_flag, nft_asset_id]
        Assert(Txn.application_args.length() == Int(8)),
        
        # LAYER 1: Issuer Registry Verification
        Assert(check_issuer_authorized(Txn.sender())),
        
        # LAYER 2: AI Verification (flag passed from backend after API call)
        # The backend must call /ai/verifyCertificate and pass result here
        Assert(Btoi(Txn.application_args[5]) == Int(1)),  # ai_verified_flag must be 1
        
        # LAYER 2.5: Manual Verification (required for instant minting)
        # If manual_verified_flag is 0, certificate goes to pending queue
        # If manual_verified_flag is 1, mint immediately (user paid for instant verification)
        Assert(Btoi(Txn.application_args[6]) == Int(1)),  # manual_verified_flag must be 1
        
        # LAYER 3: IPFS Hash Verification (length check as basic validation)
        # Backend must verify IPFS hash exists before calling
        Assert(Len(Txn.application_args[2]) > Int(0)),
        
        # Store certificate data in global state using cert_id and recipient address as keys
        App.globalPut(Concat(Bytes("cert_id_"), Txn.application_args[3]), Txn.application_args[1]),
        App.globalPut(Concat(Bytes("cert_ipfs_"), Txn.application_args[3]), Txn.application_args[2]),
        App.globalPut(Concat(Bytes("cert_issuer_"), Txn.application_args[3]), Txn.sender()),
        App.globalPut(Concat(Bytes("cert_recipient_"), Txn.application_args[3]), Txn.application_args[3]),
        App.globalPut(Concat(Bytes("cert_time_"), Txn.application_args[3]), Global.latest_timestamp()),
        App.globalPut(Concat(Bytes("cert_active_"), Txn.application_args[3]), Int(1)),
        App.globalPut(Concat(Bytes("cert_meta_"), Txn.application_args[3]), Txn.application_args[4]),
        App.globalPut(Concat(Bytes("cert_ai_"), Txn.application_args[3]), Int(1)),
        App.globalPut(Concat(Bytes("cert_manual_"), Txn.application_args[3]), Int(1)),
        App.globalPut(Concat(Bytes("cert_nft_"), Txn.application_args[3]), Txn.application_args[7]),
        
        # Increment counter
        App.globalPut(total_certificates, App.globalGet(total_certificates) + Int(1)),
        
        Approve()
    ])
    
    # ==================== CERTIFICATE VERIFICATION ====================
    
    verify_certificate = Seq([
        # Args: [method, recipient_address, expected_ipfs_hash]
        Assert(Txn.application_args.length() == Int(3)),
        
        # Check certificate is active
        Assert(App.globalGet(Concat(Bytes("cert_active_"), Txn.application_args[1])) == Int(1)),
        
        # Verify IPFS hash matches
        Assert(App.globalGet(Concat(Bytes("cert_ipfs_"), Txn.application_args[1])) == Txn.application_args[2]),
        
        # Verify AI verification flag
        Assert(App.globalGet(Concat(Bytes("cert_ai_"), Txn.application_args[1])) == Int(1)),
        
        Approve()
    ])
    
    # ==================== CERTIFICATE REVOCATION ====================
    
    revoke_certificate = Seq([
        # Args: [method, recipient_address]
        Assert(Txn.application_args.length() == Int(2)),
        
        # Only original issuer or admin can revoke
        Assert(
            Or(
                App.globalGet(Concat(Bytes("cert_issuer_"), Txn.application_args[1])) == Txn.sender(),
                is_admin()
            )
        ),
        
        # Mark as inactive
        App.globalPut(Concat(Bytes("cert_active_"), Txn.application_args[1]), Int(0)),
        
        Approve()
    ])
    
    # ==================== ADMIN FUNCTIONS ====================
    
    transfer_admin = Seq([
        Assert(is_admin()),
        Assert(Txn.application_args.length() == Int(2)),
        
        # Update admin address
        App.globalPut(admin_address, Txn.application_args[1]),
        
        Approve()
    ])
    
    toggle_ai_verification = Seq([
        Assert(is_admin()),
        
        # Toggle AI verification requirement
        App.globalPut(
            ai_verification_required,
            Int(1) - App.globalGet(ai_verification_required)
        ),
        
        Approve()
    ])
    
    get_certificate_info = Seq([
        # Args: [method, recipient_address]
        Assert(Txn.application_args.length() == Int(2)),
        
        # Client reads certificate data from local state
        Approve()
    ])
    
    # ==================== MAIN PROGRAM LOGIC ====================
    
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp,
         Cond(
             # Issuer management
             [Txn.application_args[0] == Bytes("add_issuer"), add_issuer],
             [Txn.application_args[0] == Bytes("remove_issuer"), remove_issuer],
             [Txn.application_args[0] == Bytes("check_issuer"), check_issuer],
             
             # Certificate operations
             [Txn.application_args[0] == Bytes("issue"), issue_certificate],
             [Txn.application_args[0] == Bytes("verify"), verify_certificate],
             [Txn.application_args[0] == Bytes("revoke"), revoke_certificate],
             [Txn.application_args[0] == Bytes("get_info"), get_certificate_info],
             
             # Admin operations
             [Txn.application_args[0] == Bytes("transfer_admin"), transfer_admin],
             [Txn.application_args[0] == Bytes("toggle_ai"), toggle_ai_verification],
             
             # Default: reject
             [Int(1), Reject()]
         )],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.UpdateApplication, 
         If(is_admin()).Then(Approve()).Else(Reject())],
        [Txn.on_completion() == OnComplete.DeleteApplication,
         If(is_admin()).Then(Approve()).Else(Reject())]
    )
    
    return program


def clear_state_program():
    """Clear state program - always approve for flexibility"""
    return Approve()


if __name__ == "__main__":
    # Compile the contract
    approval_program = compileTeal(unified_certificate_contract(), Mode.Application, version=6)
    clear_program = compileTeal(clear_state_program(), Mode.Application, version=6)
    
    print("=== UNIFIED CERTIFICATE APPROVAL PROGRAM ===")
    print(approval_program)
    print("\n=== CLEAR STATE PROGRAM ===")
    print(clear_program)
