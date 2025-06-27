# PolicyPal

- 📤 Upload and summarize complex insurance documents
- 🛡️ Analyze coverage strength and highlight risky terms
- 🧾 Auto-generate claim letters
- 💬 Ask contextual policy-related questions
- 🧑‍⚕️ Get insurance plan recommendations based on age, income, and goals

## 🔧 Tech Stack
- Frontend: Streamlit
- Backend: Python (LangChain, PyMuPDF, ReportLab)
- LLMs: LLaMA2, Mistral via Ollama (local inference)
- Deployment: Streamlit Cloud + Ollama (local API)

## 🚀 How to Run Locally
1. Clone the repository
2. Activate venv in your terminal
python -m venv venv
.\venv\Scripts\Activate 
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
4. Start Ollama model:
   ollama run mistral
   ollama run llama (local machine)
5. Run the app:
streamlit run main.py


“Due to Streamlit Cloud limitations, LLM-based features are available only when running the app locally via Ollama. The hosted UI demonstrates the interface only.”
