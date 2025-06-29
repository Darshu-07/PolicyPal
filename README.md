# 🛡️ PolicyPal

**PolicyPal** simplifies insurance. It leverages local AI models to help you:  
- Summarize your policy in plain English  
- Highlight risky terms like exclusions and conditions  
- Answer your questions  
- Recommend personalized insurance plans  
- Write claim letters effortlessly
- Also now you can get to upload upto two policys , can extract text from it, can also summarize for those two policies , can also get the coverage strength analysis as well as Q&A for both policies and the main feature that you can now comapare both the policies.

---

## ✨ Features

- 📤 **Upload & Summarize**: Easily upload your insurance PDFs and get a plain-English summary.  
- 🛡️ **Risk Analysis**: Automatically highlight risky terms, such as exclusions and critical conditions.  
- 💬 **Conversational Q&A**: Ask contextual questions about your policy and get accurate responses.  
- 🧾 **Claim Letter Generation**: Generate claim letters tailored to your insurance needs.  
- 🤖 **InsureWise Engine**: Receive smart, personalized plan recommendations based on age, income, and financial goals.  
- **Compare Policies**: Compare both policies now with main real world points covered.
---

## 🔧 Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Python (LangChain, PyMuPDF, ReportLab)  
- **LLMs**: LLaMA2, Mistral via **[Ollama](https://ollama.com/)** for local inference  
- **Deployment**: Streamlit Cloud (UI only) + Local Ollama API  

---

## 🚀 How It Works

1. **Upload your insurance PDF**: Quickly upload your document for analysis.  
2. **Highlight risky terms**: Exclusions, conditions, and weak areas are automatically flagged.  
3. **Interactive Q&A**: Ask questions or request summaries of specific sections.  
4. **Generate documents**: Create claim letters with a single click.  
5. **Personalized recommendations**: Use the **InsureWise Engine** to get tailored insurance suggestions.
6. **Compare Policies**: Compare both policies now with main real world points covered.

---

## 🚀 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/PolicyPal.git
   cd PolicyPal
2. Create and activate a virtual environment

python -m venv venv
.\venv\Scripts\activate       # On Windows
source venv/bin/activate     # On macOS/Linux

3. Install dependencies
pip install -r requirements.txt

4. Start Ollama models
ollama run mistral
ollama run llama

Do this locally

5. Run the app

streamlit run main.py
 
