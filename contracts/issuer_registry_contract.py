from pyteal import *

def issuer_registry_contract():
    """
    SkillDCX Issuer Registry Smart Contract
    
    Features:
    - Manage authorized certificate issuers
    - Only admin can add/remove issuers
    - Query issuer authorization status
    """
    
    # Global state keys
    admin_address = Bytes("admin")
    total_issuers = Bytes("total_issuers")
    
    # Issuer state keys (local state)
    is_authorized = Bytes("authorized")
    issuer_name = Bytes("name")
    issuer_metadata = Bytes("metadata")
    registration_timestamp = Bytes("reg_timestamp")
    
    # Contract creation - set admin
    on_creation = Seq([
        App.globalPut(admin_address, Txn.sender()),
        App.globalPut(total_issuers, Int(0)),
        Approve()
    ])
    
    # Add Issuer (admin only)
    add_issuer = Seq([
        # Verify caller is admin
        Assert(Txn.sender() == App.globalGet(admin_address)),
        
        # Verify arguments: issuer_address, name, metadata
        Assert(Txn.application_args.length() == Int(3)),
        
        # Parse issuer address from first argument
        # Store issuer data
        App.localPut(Btoi(Txn.application_args[0]), is_authorized, Int(1)),
        App.localPut(Btoi(Txn.application_args[0]), issuer_name, Txn.application_args[1]),
        App.localPut(Btoi(Txn.application_args[0]), issuer_metadata, Txn.application_args[2]),
        App.localPut(Btoi(Txn.application_args[0]), registration_timestamp, Global.latest_timestamp()),
        
        # Increment total issuers
        App.globalPut(total_issuers, App.globalGet(total_issuers) + Int(1)),
        
        Approve()
    ])
    
    # Remove Issuer (admin only)
    remove_issuer = Seq([
        # Verify caller is admin
        Assert(Txn.sender() == App.globalGet(admin_address)),
        
        # Verify arguments: issuer_address
        Assert(Txn.application_args.length() == Int(1)),
        
        # Verify issuer exists
        Assert(App.localGet(Btoi(Txn.application_args[0]), is_authorized) == Int(1)),
        
        # Remove authorization
        App.localPut(Btoi(Txn.application_args[0]), is_authorized, Int(0)),
        
        # Decrement total issuers
        App.globalPut(total_issuers, App.globalGet(total_issuers) - Int(1)),
        
        Approve()
    ])
    
    # Check if Issuer is Authorized (read-only)
    check_issuer = Seq([
        Assert(Txn.application_args.length() == Int(1)),  # issuer_address
        
        # Return authorization status (handled client-side)
        Approve()
    ])
    
    # Transfer Admin (current admin only)
    transfer_admin = Seq([
        # Verify caller is current admin
        Assert(Txn.sender() == App.globalGet(admin_address)),
        
        # Verify arguments: new_admin_address
        Assert(Txn.application_args.length() == Int(1)),
        
        # Update admin
        App.globalPut(admin_address, Txn.application_args[0]),
        
        Approve()
    ])
    
    # Main application logic
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnCall.NoOp,
         Cond(
             [Txn.application_args[0] == Bytes("add_issuer"), add_issuer],
             [Txn.application_args[0] == Bytes("remove_issuer"), remove_issuer],
             [Txn.application_args[0] == Bytes("check_issuer"), check_issuer],
             [Txn.application_args[0] == Bytes("transfer_admin"), transfer_admin],
             [Int(1), Reject()]
         )],
        [Txn.on_completion() == OnCall.OptIn, Approve()],  # Allow issuers to opt-in
        [Txn.on_completion() == OnCall.CloseOut, Approve()],
        [Txn.on_completion() == OnCall.UpdateApplication, Reject()],  # No updates allowed
        [Txn.on_completion() == OnCall.DeleteApplication, 
         # Only admin can delete
         If(Txn.sender() == App.globalGet(admin_address)).Then(Approve()).Else(Reject())
        ]
    )
    
    return program

def clear_state_program():
    """Clear state program - always approve"""
    return Approve()

if __name__ == "__main__":
    # Compile the contract
    approval_program = compileTeal(issuer_registry_contract(), Mode.Application, version=6)
    clear_program = compileTeal(clear_state_program(), Mode.Application, version=6)
    
    print("=== ISSUER REGISTRY APPROVAL PROGRAM ===")
    print(approval_program)
    print("\n=== CLEAR STATE PROGRAM ===")
    print(clear_program)