import streamlit as st
from mistralai import Mistral
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
import base64
import os

# -------------------------
# Page configuration
# -------------------------
st.set_page_config(
    page_title="Invoice Data Extractor",
    page_icon="📄",
    layout="centered"
)

# -------------------------
# Custom CSS styling
# -------------------------
st.markdown(
    """
    <style>
        /* Light mode */
        @media (prefers-color-scheme: light) {
            [data-testid="stAppViewContainer"] {
                background-color: #f9f9f9;
                color: black;
            }
            [data-testid="stSidebar"] {
                background-color: #ffffff;
                color: black;
            }
            .main-title {
                color: gray !important;
            }
            .sub-title {
                color: gray !important;
            }
            .footer {
                color: gray !important;
            }
        }

        /* Dark mode */
        @media (prefers-color-scheme: dark) {
            [data-testid="stAppViewContainer"] {
                background-color: #0e1117;
                color: white;
            }
            [data-testid="stSidebar"] {
                background-color: #1b1e23;
                color: white;
            }
            .main-title {
                color: #b0b0b0 !important;
            }
            .sub-title {
                color: #b0b0b0 !important;
            }
            .footer {
                color: #aaaaaa !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------
# Header
# -------------------------
st.markdown("<p class='main-title'>Invoice Data Extractor</p>", unsafe_allow_html=True)
# -------------------------
# Initialize Mistral client
# -------------------------
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    st.warning("API key not found. Please set MISTRAL_API_KEY in your environment variables.")
else:
    client = Mistral(api_key=api_key)

# -------------------------
# File uploader
# -------------------------
st.markdown("### 📤 Upload your invoice")
uploaded_file = st.file_uploader(
    "Select a PDF or image file",
    type=["pdf", "jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

prompt = """
You are an assistant specialized in document analysis.

Carefully read the provided document image (invoice, quote, receipt, purchase order, etc.)
and extract the following key fields. Return ONLY a valid JSON object with the detected values.

Identify equivalent labels even if wording differs:

- "numero_de_dossier" → may appear as "Référence", "N° Dossier", "Réf", "N/REF", etc.
- "numero_de_facture" → may appear as "Facture N°", "Invoice No", "N", etc.
- "date_de_facture" → may appear as "Date", "Invoice Date", "Date d’émission", etc.
  ⚠️ Ignore date ranges such as “du 01/07/2023 au 30/08/2023”.
- "montant_ht" → may appear as "Montant HT", "Net Amount", "Subtotal", "Total (excl. tax)", etc.
- "montant_tva" → may appear as "TVA", "VAT", "Tax", "Tax Amount", etc.
- "montant_ttc" → may appear as "Montant TTC", "Total TTC", "Amount Due", "Total (incl. tax)", etc.

If a value is missing, leave it empty ("").
Return EXACTLY this JSON structure:

{
  "numero_de_dossier": "",
  "numero_de_facture": "",
  "date_de_facture": "",
  "montant_ht": "",
  "montant_tva": "",
  "montant_ttc": ""
}
"""

# -------------------------
# File preview & processing
# -------------------------
if uploaded_file:
    st.success("File uploaded successfully!")

    images = []

    if uploaded_file.type == "application/pdf":
        try:
            pdf_bytes = uploaded_file.read()
            pages = convert_from_bytes(pdf_bytes)
            st.info(f"📄 PDF detected with {len(pages)} page(s).")

            for i, page in enumerate(pages, start=1):
                buf = BytesIO()
                page.save(buf, format="JPEG")
                image_bytes = buf.getvalue()
                base64_img = base64.b64encode(image_bytes).decode("utf-8")
                images.append(base64_img)

                st.image(page, caption=f"Page {i} Preview", use_container_width=True)

        except Exception as e:
            st.error(f"Error processing PDF: {e}")
            st.stop()

    else:
        try:
            image = Image.open(uploaded_file)
            buf = BytesIO()
            image.save(buf, format="JPEG")
            image_bytes = buf.getvalue()
            base64_img = base64.b64encode(image_bytes).decode("utf-8")
            images.append(base64_img)
            st.image(image, caption="Uploaded Image Preview", use_container_width=True)

        except Exception as e:
            st.error(f"Invalid image file: {e}")
            st.stop()

    # -------------------------
    # Extract button
    # -------------------------
    if st.button("🔍 Extract data"):
        if not api_key:
            st.error("API key missing. Please set MISTRAL_API_KEY.")
            st.stop()

        st.info("⏳ Sending document to Pixtral-12B for analysis...")

        image_inputs = [
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img}"}
            for img in images
        ]

        with st.spinner("Processing with Pixtral-12B..."):
            response = client.chat.complete(
                model="pixtral-12b",
                messages=[
                    {
                        "role": "user",
                        "content": image_inputs + [{"type": "text", "text": prompt}],
                    }
                ],
                temperature=0.2,
                max_tokens=800,
                response_format={"type": "json_object"},
            )

        st.success("Extraction complete!")

        st.subheader("🧾 Extracted Data")
        with st.expander("View JSON result", expanded=True):
            st.json(response.choices[0].message.content)

# -------------------------
# Footer
# -------------------------
st.markdown(
    """
    <hr>
    <p class='footer'>
    Built by <b>Asser Omar</b> • Powered by <b>Pixtral-12B (Mistral AI)</b>
    </p>
    """,
    unsafe_allow_html=True
)
