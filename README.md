# 🧠 AXIOM — Intelligent File Discovery

An interactive AI system that allows you to **search and understand your local files using semantic intelligence**.

---

## 🌐 Live Demo

👉 https://axiomseekr.streamlit.app

---

## 🧠 What this project does

* Scans local folders and reads supported files (.txt, .pdf, .docx)
* Splits content into semantic chunks
* Generates embeddings for each chunk
* Uses similarity search to retrieve relevant information
* Highlights matching content and ranks results by relevance

---

## 🎯 Why this matters

Traditional search relies on keywords.
AXIOM uses **semantic understanding**, meaning it can find information based on *context and meaning*, not just exact matches.

This is a step toward more **intelligent, explainable AI systems** that interact with real user data.

---

## 🚀 Features

* 🔍 Semantic file search
* 🧠 Embedding-based retrieval (FAISS)
* 📊 Relevance scoring
* ✨ Highlighted matching text
* 📂 Local file system exploration
* ⚡ Interactive interface (Streamlit)

---

## 🛠 Tech Stack

* Python
* Streamlit
* NumPy
* FAISS
* Sentence Transformers
* PyPDF / python-docx

---

## ▶️ Run locally

```bash
git clone https://github.com/dealmeidaferreiraAlexandra/axiom.git
cd axiom

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

---

## ⚠️ Notes

* The app accesses local files — permissions depend on your system
* Live demo has limited file access (sandbox environment)
* Performance depends on number and size of files

---

## 🚀 Future Work

* 🤖 AI explanations (“why this file was retrieved”)
* 📄 Automatic summarization of results
* 🔎 Multi-modal search (images + text)
* 💻 Desktop app version (Tauri)

---

👩‍💻 Author

Developed by Alexandra de Almeida Ferreira
GitHub: [https://github.com/dealmeidaferreiraAlexandra](https://github.com/dealmeidaferreiraAlexandra)
LinkedIn: [https://www.linkedin.com/in/dealmeidaferreira](https://www.linkedin.com/in/dealmeidaferreira)

---

📄 License

This project is licensed under the MIT License.
