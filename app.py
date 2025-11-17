import streamlit as st
import base64
from mistralai import Mistral
from pdf2image import convert_from_bytes
from io import BytesIO
import os
from PIL import Image

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

if uploaded_file:
    st.success("✅ File uploaded successfully")

    images = []  

    # Handle PDFs (multi-page)
    if uploaded_file.type == "application/pdf":
        try:
            pdf_bytes = uploaded_file.read()
            pages = convert_from_bytes(pdf_bytes)

            st.info(f"📄 PDF detected with {len(pages)} page(s). Converting to images...")

            for i, page in enumerate(pages, start=1):
                buf = BytesIO()
                page.save(buf, format="JPEG")
                image_bytes = buf.getvalue()
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
                images.append(base64_image)

                st.image(page, caption=f"Page {i} Preview", use_container_width=True)

        except Exception as e:
            st.error(f"Error processing PDF: {e}")
            st.stop()

    # Handle normal images (JPG, JPEG, PNG)
    else:
        try:
            image = Image.open(uploaded_file)
            buf = BytesIO()
            image.save(buf, format="JPEG")
            image_bytes = buf.getvalue()
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            images.append(base64_image)

            st.image(image, caption="Uploaded Image Preview", use_container_width=True)

        except Exception as e:
            st.error(f"This file is not a valid image: {e}")
            st.stop()

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