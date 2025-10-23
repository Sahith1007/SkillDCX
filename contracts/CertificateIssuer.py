from pyteal import *


def approval_program():
    cert_id_key = Bytes("cert_id")
    ipfs_hash_key = Bytes("ipfs_hash")  # type: ignore
    issuer_key = Bytes("issuer")
    recipient_key = Bytes("recipient")

    on_create = Seq([App.globalPut(issuer_key, Txn.sender()), Approve()])

    on_issue = Seq(
        [
            Assert(Txn.application_args.length() == Int(4)),
            Assert(Txn.sender() == App.globalGet(issuer_key)),
            App.globalPut(cert_id_key, Txn.application_args[1]),
            App.globalPut(ipfs_hash_key, Txn.application_args[2]),
            App.globalPut(recipient_key, Txn.application_args[3]),
            Approve(),
        ]
    )

    on_verify = Seq(
        [
            Assert(Txn.application_args.length() == Int(2)),
            Assert(Txn.application_args[1] == App.globalGet(cert_id_key)),
            Approve(),
        ]
    )

    on_call = Cond(
        [Txn.application_args[0] == Bytes("issue"), on_issue],
        [Txn.application_args[0] == Bytes("verify"), on_verify],
    )

    on_delete = Return(Txn.sender() == App.globalGet(issuer_key))
    on_update = Return(Txn.sender() == App.globalGet(issuer_key))

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.NoOp, on_call],
        [Txn.on_completion() == OnComplete.DeleteApplication, on_delete],
        [Txn.on_completion() == OnComplete.UpdateApplication, on_update],
    )

    return program


def clear_program():
    return Approve()
