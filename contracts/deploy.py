import base64
from algosdk.v2client import algod  # type: ignore
from algosdk import account, mnemonic, transaction
from pyteal import compileTeal, Mode
from CertificateIssuer import approval_program, clear_program

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # Algonode needs no token
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# 👉 Replace this with the issuer's wallet mnemonic
ISSUER_MNEMONIC = "your 25-word mnemonic here"
private_key = mnemonic.to_private_key(ISSUER_MNEMONIC)
issuer_address = account.address_from_private_key(private_key)


def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


def deploy_contract():
    approval_teal = compileTeal(approval_program(), mode=Mode.Application, version=7)
    clear_teal = compileTeal(clear_program(), mode=Mode.Application, version=7)

    approval_binary = compile_program(client, approval_teal)
    clear_binary = compile_program(client, clear_teal)

    params = client.suggested_params()

    txn = transaction.ApplicationCreateTxn(
        sender=issuer_address,
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC.real,
        approval_program=approval_binary,
        clear_program=clear_binary,
        global_schema=transaction.StateSchema(num_uints=0, num_byte_slices=4),
        local_schema=transaction.StateSchema(num_uints=0, num_byte_slices=0),
    )

    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    result = transaction.wait_for_confirmation(client, txid, 4)

    app_id = result["application-index"]
    print(f"✅ Deployed Certificate Issuer App ID: {app_id}")
    return app_id


if __name__ == "__main__":
    deploy_contract()
