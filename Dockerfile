# 1️⃣ Base image: a clean, minimal Python environment
FROM python:3.10-slim

# 2️⃣ Set working directory inside the container
WORKDIR /app

# 3️⃣ Copy only the requirements file first (for caching)
COPY requirements.txt .

# 4️⃣ Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy all remaining files (app.py)
COPY . .

# 6️⃣ Expose port 8501 for Streamlit
EXPOSE 8501

# 7️⃣ Set Streamlit server environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# 8️⃣ Start the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
