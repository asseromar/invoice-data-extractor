import streamlit as st
import base64
from mistralai import Mistral
from pdf2image import convert_from_bytes
from io import BytesIO
import os

# Initialize client
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

st.title("📄 Invoice Data Extractor with Pixtral-12B")

uploaded_file = st.file_uploader("Upload your invoice (PDF or image)", type=["pdf", "jpg", "jpeg", "png"])

prompt = """
You are an assistant specialized in document analysis.

Carefully read the provided document image (invoice, quote, receipt, purchase order, etc.)
and extract the following key fields. Return ONLY a valid JSON object with the detected values.

Identify equivalent labels even if wording differs:

- "numero_de_dossier" → may appear as "Référence", "N° Dossier", "Réf", "N/REF", etc.
  Example values: "2025.01", "1234546.01-PLAN"
- "numero_de_facture" → may appear as "Facture N°", "Invoice No", "N", etc.
- "date_de_facture" → may appear as "Date", "Invoice Date", "Date d’émission", etc.
  ⚠️ Ignore date ranges such as “du 01/07/2023 au 30/08/2023” (leave this field empty).
- "montant_ht" → may appear as "Montant HT", "Net Amount", "Subtotal", "Total (excl. tax)", etc.
- "montant_tva" → may appear as "TVA", "VAT", "Tax", "Tax Amount", etc.
- "montant_ttc" → may appear as "Montant TTC", "Total TTC", "Amount Due", "Total (incl. tax)", etc.

If a value is missing, leave it as an empty string ("").

Return EXACTLY this JSON structure — no explanations, no extra text:

{
  "numero_de_dossier": "",
  "numero_de_facture": "",
  "date_de_facture": "",
  "montant_ht": "",
  "montant_tva": "",
  "montant_ttc": ""
}

"""

# Handle upload
if uploaded_file:
    st.write("✅ File uploaded successfully")

    # Convert PDF to images if needed
    images = []
    if uploaded_file.type == "application/pdf":
        pages = convert_from_bytes(uploaded_file.read())
        for page in pages:
            buf = BytesIO()
            page.save(buf, format="JPEG")
            image_bytes = buf.getvalue()
            images.append(base64.b64encode(image_bytes).decode("utf-8"))
    else:
        # Single image
        images.append(base64.b64encode(uploaded_file.read()).decode("utf-8"))

    # Display preview
    st.image(uploaded_file, caption="Uploaded document preview")

    if st.button("🔍 Extract data"):
        st.write("⏳ Processing with Pixtral-12B...")

        image_inputs = [
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img}"}
            for img in images
        ]

        # Call the model
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

        st.subheader("🧾 Extracted JSON:")
        st.json(response.choices[0].message.content)



# test 