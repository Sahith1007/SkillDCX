from pyteal import *

def instant_verification_payment_contract():
    """
    Instant Verification Payment Contract
    
    Handles payments for instant certificate verification.
    Revenue split: 60% to verifier, 40% to platform treasury.
    
    Payment: 1 ALGO = 1,000,000 microALGOs
    """
    
    # Global state keys
    admin_address = Bytes("admin")
    treasury_address = Bytes("treasury")
    verifier_pool_address = Bytes("verifier_pool")
    instant_verification_fee = Bytes("instant_fee")  # In microALGOs
    total_payments = Bytes("total_payments")
    total_verifications = Bytes("total_verifications")
    
    # Local state keys (per user)
    user_paid = Bytes("paid")
    user_verified = Bytes("verified")
    payment_timestamp = Bytes("pay_time")
    
    # Constants
    INSTANT_FEE = Int(1000000)  # 1 ALGO
    VERIFIER_PERCENTAGE = Int(60)  # 60%
    PLATFORM_PERCENTAGE = Int(40)  # 40%
    
    @Subroutine(TealType.uint64)
    def is_admin():
        """Check if caller is admin"""
        return Txn.sender() == App.globalGet(admin_address)
    
    @Subroutine(TealType.none)
    def split_payment(amount: TealType.uint64):
        """Split payment between verifier and platform"""
        verifier_amount = amount * VERIFIER_PERCENTAGE / Int(100)
        platform_amount = amount * PLATFORM_PERCENTAGE / Int(100)
        
        return Seq([
            # Send to verifier pool
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: App.globalGet(verifier_pool_address),
                TxnField.amount: verifier_amount,
                TxnField.fee: Int(0)
            }),
            InnerTxnBuilder.Submit(),
            
            # Send to treasury
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: App.globalGet(treasury_address),
                TxnField.amount: platform_amount,
                TxnField.fee: Int(0)
            }),
            InnerTxnBuilder.Submit()
        ])
    
    # Contract creation
    on_creation = Seq([
        App.globalPut(admin_address, Txn.sender()),
        App.globalPut(treasury_address, Txn.sender()),  # Default to sender
        App.globalPut(verifier_pool_address, Txn.sender()),  # Default to sender
        App.globalPut(instant_verification_fee, INSTANT_FEE),
        App.globalPut(total_payments, Int(0)),
        App.globalPut(total_verifications, Int(0)),
        Approve()
    ])
    
    # Set treasury address
    set_treasury = Seq([
        Assert(is_admin()),
        Assert(Txn.application_args.length() == Int(2)),
        
        App.globalPut(treasury_address, Txn.application_args[1]),
        Approve()
    ])
    
    # Set verifier pool address
    set_verifier_pool = Seq([
        Assert(is_admin()),
        Assert(Txn.application_args.length() == Int(2)),
        
        App.globalPut(verifier_pool_address, Txn.application_args[1]),
        Approve()
    ])
    
    # Pay for instant verification
    pay_instant_verification = Seq([
        # Args: [method]
        # Must be accompanied by payment transaction
        Assert(Global.group_size() == Int(2)),
        
        # Verify payment transaction
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[0].receiver() == Global.current_application_address()),
        Assert(Gtxn[0].amount() >= App.globalGet(instant_verification_fee)),
        Assert(Gtxn[0].sender() == Txn.sender()),
        
        # Verify app call transaction
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        
        # Mark as paid in user's local state
        App.localPut(Txn.sender(), user_paid, Int(1)),
        App.localPut(Txn.sender(), payment_timestamp, Global.latest_timestamp()),
        App.localPut(Txn.sender(), user_verified, Int(0)),  # Not yet verified
        
        # Split payment
        split_payment(Gtxn[0].amount()),
        
        # Update global stats
        App.globalPut(total_payments, App.globalGet(total_payments) + Int(1)),
        
        Approve()
    ])
    
    # Mark as verified (called by backend after manual verification)
    mark_verified = Seq([
        # Args: [method, user_address]
        Assert(is_admin()),
        Assert(Txn.application_args.length() == Int(2)),
        
        # Verify user paid
        Assert(App.localGet(Btoi(Txn.application_args[1]), user_paid) == Int(1)),
        
        # Mark as verified
        App.localPut(Btoi(Txn.application_args[1]), user_verified, Int(1)),
        
        # Update global stats
        App.globalPut(total_verifications, App.globalGet(total_verifications) + Int(1)),
        
        Approve()
    ])
    
    # Check if user has paid and is verified
    check_verification_status = Seq([
        # Args: [method, user_address]
        Assert(Txn.application_args.length() == Int(2)),
        
        # Return values accessible via local state read
        Approve()
    ])
    
    # Update instant verification fee
    update_fee = Seq([
        Assert(is_admin()),
        Assert(Txn.application_args.length() == Int(2)),
        
        App.globalPut(instant_verification_fee, Btoi(Txn.application_args[1])),
        Approve()
    ])
    
    # Main program logic
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp,
         Cond(
             [Txn.application_args[0] == Bytes("set_treasury"), set_treasury],
             [Txn.application_args[0] == Bytes("set_verifier_pool"), set_verifier_pool],
             [Txn.application_args[0] == Bytes("pay_instant"), pay_instant_verification],
             [Txn.application_args[0] == Bytes("mark_verified"), mark_verified],
             [Txn.application_args[0] == Bytes("check_status"), check_verification_status],
             [Txn.application_args[0] == Bytes("update_fee"), update_fee],
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
    """Clear state program"""
    return Approve()


if __name__ == "__main__":
    from pyteal import compileTeal, Mode
    
    approval_program = compileTeal(
        instant_verification_payment_contract(),
        Mode.Application,
        version=6
    )
    
    clear_program = compileTeal(
        clear_state_program(),
        Mode.Application,
        version=6
    )
    
    print("=== INSTANT VERIFICATION PAYMENT APPROVAL PROGRAM ===")
    print(approval_program)
    print("\n=== CLEAR STATE PROGRAM ===")
    print(clear_program)
