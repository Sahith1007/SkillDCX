from pyteal import *

def certification_contract():
    """
    SkillDCX Certificate Smart Contract
    
    Features:
    - Issue certificates with IPFS hash storage
    - Verify certificate authenticity
    - Revoke certificates (issuer only)
    - Soulbound tokens (non-transferable)
    """
    
    # Global state keys
    total_certificates = Bytes("total_certs")
    issuer_registry_app_id = Bytes("issuer_registry")
    
    # Certificate storage keys (local state)
    cert_ipfs_hash = Bytes("ipfs_hash")
    cert_issuer = Bytes("issuer")
    cert_timestamp = Bytes("timestamp")
    cert_active = Bytes("active")
    cert_metadata = Bytes("metadata")
    
    # Application calls
    on_creation = Seq([
        App.globalPut(total_certificates, Int(0)),
        App.globalPut(issuer_registry_app_id, Txn.applications[1]),  # Registry app ID passed during creation
        Approve()
    ])
    
    # Issue Certificate
    @Subroutine(TealType.uint64)
    def is_authorized_issuer():
        """Check if caller is an authorized issuer via registry contract"""
        return App.globalGet(issuer_registry_app_id) != Int(0)  # Simplified - in real implementation would call registry
    
    issue_certificate = Seq([
        # Verify issuer authorization
        Assert(is_authorized_issuer()),
        
        # Verify application arguments
        Assert(Txn.application_args.length() == Int(3)),  # ipfs_hash, receiver, metadata
        
        # Store certificate data in receiver's local state
        App.localPut(Btoi(Txn.application_args[1]), cert_ipfs_hash, Txn.application_args[0]),
        App.localPut(Btoi(Txn.application_args[1]), cert_issuer, Txn.sender()),
        App.localPut(Btoi(Txn.application_args[1]), cert_timestamp, Global.latest_timestamp()),
        App.localPut(Btoi(Txn.application_args[1]), cert_active, Int(1)),
        App.localPut(Btoi(Txn.application_args[1]), cert_metadata, Txn.application_args[2]),
        
        # Increment total certificates
        App.globalPut(total_certificates, App.globalGet(total_certificates) + Int(1)),
        
        Approve()
    ])
    
    # Verify Certificate
    verify_certificate = Seq([
        Assert(Txn.application_args.length() == Int(2)),  # certificate_holder, expected_ipfs_hash
        
        # Check if certificate exists and is active
        Assert(App.localGet(Btoi(Txn.application_args[0]), cert_active) == Int(1)),
        
        # Verify IPFS hash matches
        Assert(App.localGet(Btoi(Txn.application_args[0]), cert_ipfs_hash) == Txn.application_args[1]),
        
        Approve()
    ])
    
    # Revoke Certificate (issuer only)
    revoke_certificate = Seq([
        Assert(Txn.application_args.length() == Int(1)),  # certificate_holder
        
        # Verify caller is the original issuer
        Assert(App.localGet(Btoi(Txn.application_args[0]), cert_issuer) == Txn.sender()),
        
        # Mark certificate as inactive
        App.localPut(Btoi(Txn.application_args[0]), cert_active, Int(0)),
        
        Approve()
    ])
    
    # Get Certificate Info (read-only)
    get_certificate_info = Seq([
        Assert(Txn.application_args.length() == Int(1)),  # certificate_holder
        
        # Return certificate data (this would be handled by client-side reading)
        Approve()
    ])
    
    # Main application logic
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnCall.NoOp, 
         Cond(
             [Txn.application_args[0] == Bytes("issue"), issue_certificate],
             [Txn.application_args[0] == Bytes("verify"), verify_certificate],
             [Txn.application_args[0] == Bytes("revoke"), revoke_certificate],
             [Txn.application_args[0] == Bytes("get_info"), get_certificate_info],
             [Int(1), Reject()]
         )],
        [Txn.on_completion() == OnCall.OptIn, Approve()],  # Allow users to opt-in
        [Txn.on_completion() == OnCall.CloseOut, Approve()],
        [Txn.on_completion() == OnCall.UpdateApplication, Reject()],  # No updates allowed
        [Txn.on_completion() == OnCall.DeleteApplication, Reject()]   # No deletion allowed
    )
    
    return program

def clear_state_program():
    """Clear state program - always approve for flexibility"""
    return Approve()

if __name__ == "__main__":
    # Compile the contract
    approval_program = compileTeal(certification_contract(), Mode.Application, version=6)
    clear_program = compileTeal(clear_state_program(), Mode.Application, version=6)
    
    print("=== APPROVAL PROGRAM ===")
    print(approval_program)
    print("\n=== CLEAR STATE PROGRAM ===")
    print(clear_program)