
import hashlib
from datetime import datetime, timezone

import requests
import streamlit as st

# API provided by the instructor
API_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbyNZNOE1DYNbd4GbGTISJsGrnJ4PYCuip0yjSw3Lr8KkD6-kadKI9mfpKNfiAHEWb0Osw/exec"
)

COMMIT_DEADLINE = datetime(2026, 11, 15, 22, 59, 59, tzinfo=timezone.utc)
REVEAL_OPEN = datetime(2026, 11, 15, 23, 0, 0, tzinfo=timezone.utc)

st.set_page_config(page_title="Beauty Contest App", page_icon="🎯")

st.title("Beauty Contest App")
st.caption("NEOMA Business School · FinTech & DeFi · Commit–Reveal")
st.write("Developed by Moyer YOBO")

with st.form("beauty_contest_form"):
    uni_id = st.text_input("NEOMA ID")
    guess = st.number_input("Guess (0–100)", min_value=0, max_value=100, step=1)
    nonce = st.text_input("Secret nonce", type="password")

    col1, col2 = st.columns(2)

    with col1:
        commit = st.form_submit_button("Commit", width="stretch")
    with col2:
        reveal = st.form_submit_button("Reveal", width="stretch")

if commit or reveal:
    uni_id = uni_id.strip()
    nonce = nonce.strip()
    number = int(guess)

    if not uni_id or not nonce:
        st.error("Please enter your NEOMA ID and secret nonce.")
    else:
        preimage = f"{uni_id}|{number}|{nonce}"
        commit_hash = hashlib.sha256(preimage.encode("utf-8")).hexdigest()

        st.write("**SHA-256 hash:**")
        st.code(commit_hash)

        now = datetime.now(timezone.utc)

        if commit and now > COMMIT_DEADLINE:
            st.error("Commit phase is closed.")
        elif reveal and now < REVEAL_OPEN:
            st.error("Reveal phase is not open yet.")
        else:
            if commit:
                payload = {
                    "kind": "commit",
                    "uni_id": uni_id,
                    "commit": commit_hash
                }
            else:
                payload = {
                    "kind": "reveal",
                    "uni_id": uni_id,
                    "number": number,
                    "nonce": nonce
                }

            try:
                response = requests.post(
                    API_URL, json=payload, timeout=15
                )
                response.raise_for_status()

                st.success("Request sent to the ledger.")
                st.text(response.text)

                if commit:
                    st.info(
                        "Keep your NEOMA ID, guess, and nonce "
                        "for the Reveal phase."
                    )

            except requests.RequestException as exc:
                st.error(f"Could not contact the ledger: {exc}")
