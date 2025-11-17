# 📄 Invoice & Document Data Extractor (Pixtral-12B + Streamlit)

A multimodal AI web app that uses **Pixtral-12B**, Mistral’s visual encoder–decoder model, to analyze and extract structured data from PDFs or images.

While it’s optimized for invoices, this app can extract any kind of information depending on the prompt — making it a flexible and powerful tool for document understanding, from receipts and purchase orders to reports or certificates.

## Features

- Uses **Pixtral-12B**, a large-scale vision–language model capable of understanding both text and layout from document images  
- Works with custom prompts — extract *any* fields, not just invoice data  
- Handles **PDFs (multi-page)**, **JPG**, and **PNG** formats  
- Converts PDFs to images automatically with `pdf2image`  
- Clean Streamlit interface with automatic light/dark mode
- Deployable locally, with Docker, or on Hugging Face Spaces

## How It Works

1. The uploaded document (PDF or image) is converted into base64-encoded images.  
2. These images, along with a user-defined text prompt, are sent to the Pixtral-12B multimodal model via Mistral’s API.  
3. Pixtral’s visual encoder interprets the layout, text, and visual structure of the document.  
4. The model returns structured data (typically JSON) that matches the prompt — such as:
   - Invoice metadata (dates, totals, references)
   - Delivery or shipping details
   - Business card fields (name, company, contact)
   - Table contents, forms, or handwritten text  

## Custom Prompt Examples

You can modify the extraction behavior in `app.py` by changing the `prompt` variable.

**Example 1 — Extract delivery information:**
```
Return a JSON with:
{
"expediteur": "",
"destinataire": "",
"adresse_livraison": "",
"date_expedition": ""
}
```
This flexibility allows the app to adapt to *any* document type or layout.

## Tech Stack

| Component               | Technology                                   |
| ----------------------- | -------------------------------------------- |
| 🧠 Model                | Pixtral-12B (Mistral visual encoder–decoder) |
| 🖥 Frontend             | Streamlit                                    |
| 📦 PDF/Image Processing | pdf2image, Pillow                            |
| ☁️ Deployment           | Hugging Face Spaces / Docker                 |
| 🔑 Secrets              | `MISTRAL_API_KEY` environment variable       |


## Installation (Local)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/asseromar/invoice-extractor.git
cd invoice-extractor
```

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Install system dependency (for PDFs)

#### macOS

```bash
brew install poppler
```

#### Windows

Download [Poppler for Windows](https://blog.alivate.com.au/poppler-windows/) and add its `/bin` folder to your PATH.

### 5️⃣ Add your Mistral API key

```bash
export MISTRAL_API_KEY=sk-your-api-key
```

### 6️⃣ Run the app

```bash
streamlit run app.py
```

## Author

**Asser Omar**

Paris, France

[LinkedIn](https://www.linkedin.com/in/asseromar/) 

---

## 🪪 License

This project is licensed under the **MIT License**.

---

⭐ If you like this project, consider giving it a **star** on GitHub — it helps others discover it!

