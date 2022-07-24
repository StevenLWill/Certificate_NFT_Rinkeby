import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

json_headers = {
    "Content-Type": "application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

file_headers = {
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

def convert_data_to_json(content):
    data = {"pinataOptions": {"cidVersion": 1}, "pinataContent": content}
    return json.dumps(data)

def pin_file_to_ipfs(data):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        files={'file': data},
        headers=file_headers
    )
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

def pin_json_to_ipfs(json):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        data=json,
        headers=json_headers
    )
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash
    
def pin_cert(cert_name, cert_file, **kwargs):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(cert_file.getvalue())

    # Build a token metadata file for the artwork
    token_json = {
        "name": cert_name,
        "image": f"ipfs.io/ipfs/{ipfs_file_hash}",
        
    }
    # If there are any extra attributes to be added
    token_json.update(kwargs.items())
    
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash, token_json



################################################################################
# Contract Helper function:
# 1. Loads the contract once using cache
# 2. Connects to the contract using the contract address and ABI
################################################################################

# Cache the contract on load
@st.cache(allow_output_mutation=True)
# Define the load_contract function
def load_contract():

    # Load Art Gallery ABI
    with open(Path('./contracts/compiled/certificate_abi.json')) as f:
        certificate_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=certificate_abi
    )
    # Return the contract from the function
    return contract


# Load the contract
contract = load_contract()



student_account = st.text_input("Enter Account Address", value = "0x9182b74A7ED5A9b92f7113bE0415927411256426")


################################################################################
# Award Certificate
################################################################################
st.markdown("## Create the certificate")

cert_name = st.text_input("Enter the name of the student")
university_name = st.text_input("Enter the name of the university", value="University of Toronto")
class_name = st.text_input("Enter the name of the class", value="FinTech Bootcamp")
cert_date = st.text_input("Enter the date of completion", value="07-25-2022")
cert_details = st.text_input("Certificate Details", value="Certificate of Completion")

# Use the Streamlit `file_uploader` function create the type of digital image files (jpg, jpeg, or png) that will be uploaded to Pinata.
file = st.file_uploader('Upload a Certificate', type=['png','jpeg'])

if st.button("Award Certificate"):

    # Use the `pin_artwork` helper function to pin the file to IPFS
    cert_ipfs_hash, token_json =  pin_cert(cert_name, file, university = university_name, class_name=class_name, date=cert_date, details=cert_details)

    cert_uri = f"ipfs.io/ipfs/{cert_ipfs_hash}"

    tx_hash = contract.functions.mint(
        student_account,
        cert_uri
      ).transact({'from': student_account, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))
    st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
    st.markdown(f"[Cert IPFS Gateway Link](https://{cert_uri})")
    st.markdown(f"[Cert IPFS Image Link](https://{token_json['image']})")

st.markdown("---")


################################################################################
# Display Certificate
################################################################################
certificate_id = st.number_input("Enter a Certificate Token ID to display", value=0, step=1)
if st.button("Display Certificate"):
    # Get the certificate owner
    certificate_owner = contract.functions.ownerOf(certificate_id).call()
    st.write(f"The certificate was awarded to {certificate_owner}")

    # Get the certificate's metadata
    certificate_uri = contract.functions.tokenURI(certificate_id).call()
    st.write(f"The certificate's tokenURI metadata is {certificate_uri}")
