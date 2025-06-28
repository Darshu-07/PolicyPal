import streamlit as st
import fitz  
import requests
from langchain_community.llms import Ollama
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import matplotlib.pyplot as plt

def ask_mistral(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )
    return response.json().get('response', 'Error: No response from model.')

def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def clean_text(text):
    return " ".join(text.split())

def summarize_text_with_local_llm(text):
    try:
        llm = Ollama(model="mistral")
        prompt = f"""Summarize the following insurance policy in detail. 
Focus on coverages, exclusions, risk factors, and important information:\n\n{text[:1000]}"""
        return llm(prompt)
    except Exception as e:
        st.error(f"Error during summarization: {e}")
        return None

def answer_question_with_local_llm(document_text, user_question):
    try:
        llm = Ollama(model="llama2:7b")
        prompt = f"Based on this insurance policy document:\n\n{document_text[:500]}\n\nAnswer this question:\n{user_question}"
        return llm(prompt)
    except Exception as e:
        st.error(f"Error during Q&A: {e}")
        return None

def highlight_risky_terms(text):
    risky_terms = [
        "exclusion", "exclusions", "limitation", "limitations",
        "pre-existing condition", "contestable", "suicide",
        "waiting period", "not covered", "void", "termination"
    ]
    pattern = re.compile(r"(" + "|".join(re.escape(term) for term in risky_terms) + r")", re.IGNORECASE)
    highlighted_text = pattern.sub(r'<span class="highlight-text">\1</span>', text)
    return highlighted_text

def calculate_risk_score(text):
    risky_terms = [
        "exclusion", "exclusions", "limitation", "limitations",
        "pre-existing condition", "contestable", "suicide",
        "waiting period", "not covered", "void", "termination"
    ]
    text = text.lower()
    total_terms = len(risky_terms)
    risky_hits = sum(1 for term in risky_terms if term in text)
    return max(0, 100 - (risky_hits * (100 // total_terms)))

def generate_pdf_summary(summary_text, risk_score, strength_label):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("<b>PolicyPal - Insurance Summary Report</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Coverage Strength:</b> {strength_label}", styles['Normal']))
    elements.append(Paragraph(f"<b>Risk Score:</b> {risk_score}/100", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>Simplified Policy Summary:</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(summary_text.replace('\n', '<br/>'), styles['Normal']))
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_claim_pdf(claim_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("<b>PolicyPal - Claim Form Draft</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(claim_text.replace('\n', '<br/>'), styles['Normal']))
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_claim_letter(user_input):
    try:
        llm = Ollama(model="llama2:7b")
        prompt = f"""
You are an AI assistant helping users write simple insurance claim letters.

Write a concise claim letter based on this incident:
\"\"\"{user_input}\"\"\"

Include:
- Greeting
- Summary of incident
- Damages/losses
- Request for reimbursement
- Polite closing

Use a polite, clear, and professional tone.
Keep it short.
"""
        return llm(prompt)
    except Exception as e:
        st.error(f"Error during claim generation: {e}")
        return None

# Streamlit UI
st.set_page_config(page_title="PolicyPal - Insurance Simplifier", layout="centered")

import os

IS_CLOUD = os.environ.get("STREAMLIT_SERVER_HEADLESS", "") == "1"

if IS_CLOUD:
    st.warning("⚠️ LLM features are disabled in the hosted version (Streamlit Cloud).\nPlease run locally to use summarization and recommendations.")


st.sidebar.title("📋 Navigation")
page = st.sidebar.radio("Go to", [
    "Upload Policy", "Coverage Strength", "Summarize", "Ask Questions", 
    "Claim Letter", "InsureWise Advisor", "Compare Policies"
])


if "summary" not in st.session_state:
    st.session_state.summary = None

st.markdown("""
<style>
.stApp {
    background-color: #000000;
    font-family: 'Segoe UI', sans-serif;
    padding: 1rem;
}
.highlight-text {
    background-color: #000000;
    color: #cc0000;
    padding: 2px 5px;
    border-radius: 4px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

if page == "Upload Policy":
    st.title("📤 Upload Insurance Policies for Comparison")
    uploaded_files = st.file_uploader(
        "Upload one or two policies (PDF only)", 
        type=["pdf"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) > 2:
            st.error("Please upload no more than 2 files.")
        else:
            for idx, file in enumerate(uploaded_files):
                extracted_text = extract_text_from_pdf(file)
                st.session_state[f"policy_{idx+1}_text"] = extracted_text
                highlighted_text = highlight_risky_terms(extracted_text)
                with st.expander(f"🔍 View Policy {idx+1} (Highlighted Terms)"):
                    st.markdown(highlighted_text, unsafe_allow_html=True)

            st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")


elif page == "Coverage Strength":
    st.title("🛡 Coverage Strength Analysis")

    texts = []
    if "policy_1_text" in st.session_state:
        texts.append(("Policy 1", st.session_state["policy_1_text"]))
    if "policy_2_text" in st.session_state:
        texts.append(("Policy 2", st.session_state["policy_2_text"]))

    if not texts:
        st.warning("Please upload a policy first in the 'Upload Policy' section.")
    else:
        for label, text in texts:
            risk_score = calculate_risk_score(text)
            labels = ['Risky Terms Impact', 'Remaining Score']
            sizes = [100 - risk_score, risk_score]
            colors = ['#ff9999', '#66b3ff']

            st.subheader(f"{label}")
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')
            st.pyplot(fig)

            if risk_score >= 80:
                strength = "Strong Coverage ✅"
            elif risk_score >= 50:
                strength = "Moderate Coverage ⚠"
            else:
                strength = "Weak Coverage ❌"
            st.markdown(f"Coverage Strength: **{strength}**")
            st.divider()


elif page == "Summarize":
    st.title("📝 Simplified Summary")

    available_policies = []
    if "policy_1_text" in st.session_state:
        available_policies.append("Policy 1")
    if "policy_2_text" in st.session_state:
        available_policies.append("Policy 2")

    if not available_policies:
        st.warning("Please upload a policy first.")
    else:
        selected = st.selectbox("Choose a policy to summarize:", available_policies)
        text = st.session_state["policy_1_text"] if selected == "Policy 1" else st.session_state["policy_2_text"]

        if st.button("Summarize Policy"):
            with st.spinner("Summarizing..."):
                summary = summarize_text_with_local_llm(text)
                st.session_state[f"{selected.lower()}_summary"] = summary

        summary_key = f"{selected.lower()}_summary"
        if summary_key in st.session_state:
            st.write(st.session_state[summary_key])
            pdf_buffer = generate_pdf_summary(
                st.session_state[summary_key],
                calculate_risk_score(text),
                ""
            )
            st.download_button("Download Summary PDF", data=pdf_buffer, file_name=f"{selected}_Summary.pdf", mime="application/pdf")


elif page == "Ask Questions":
    st.title("💬 Ask Questions")

    available_policies = []
    if "policy_1_text" in st.session_state:
        available_policies.append("Policy 1")
    if "policy_2_text" in st.session_state:
        available_policies.append("Policy 2")

    if not available_policies:
        st.warning("Please upload a policy first.")
    else:
        selected = st.selectbox("Choose a policy for Q&A:", available_policies)
        text = st.session_state["policy_1_text"] if selected == "Policy 1" else st.session_state["policy_2_text"]

        example_questions = [
            "What is the total coverage amount provided by this policy?",
            "What exclusions apply to this policy?",
            "What is the deductible amount?",
            "What is the policy period?",
            "Is accidental damage covered?"
        ]
        cols = st.columns(2)
        for idx, q in enumerate(example_questions):
            if cols[idx % 2].button(q):
                with st.spinner("Generating answer..."):
                    answer = answer_question_with_local_llm(text, q)
                    st.success(f"Answer to: {q}")
                    st.write(answer)

        user_question = st.text_input("Or type your own question:")
        if st.button("Get Answer") and user_question:
            with st.spinner("Generating answer..."):
                answer = answer_question_with_local_llm(text, user_question)
                st.success("Answer:")
                st.write(answer)

elif page == "Claim Letter":
    st.title("📝 Claim Letter Drafting")
    description = st.text_area("Describe the incident")
    if st.button("Generate Claim Letter") and description.strip():
        with st.spinner("Generating claim draft..."):
            claim_draft = generate_claim_letter(description)
            if claim_draft:
                st.success("Claim Letter Generated")
                st.write(claim_draft)
                claim_pdf = generate_claim_pdf(claim_draft)
                st.download_button("Download Claim PDF", data=claim_pdf, file_name="Claim_Letter.pdf", mime="application/pdf")

elif page == "InsureWise Advisor":
    st.title("🛡️ PolicyPal's InsureWise – GenAI Insurance Advisor")

    st.subheader("🧑‍⚕️ Recommend an Insurance Plan")

    age = st.slider("Your Age", 18, 70, 30)
    income = st.text_input("Monthly Income (in ₹)")
    members = st.number_input("Family Members to Cover", min_value=1, step=1)
    goals = st.text_area("Your Goals (e.g., cover for illness, travel, accident...)")

    def ask_mistral(prompt):
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        return response.json().get('response', 'Error: No response from model.')

    def generate_advice_pdf(content):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("<b>InsureWise - Insurance Recommendation Report</b>", styles['Title']),
            Spacer(1, 12),
            Paragraph(f"<b>Age:</b> {age}", styles['Normal']),
            Paragraph(f"<b>Income:</b> ₹{income}", styles['Normal']),
            Paragraph(f"<b>Family Members:</b> {members}", styles['Normal']),
            Spacer(1, 12),
            Paragraph("<b>Goals:</b>", styles['Heading3']),
            Paragraph(goals.replace('\n', '<br/>'), styles['Normal']),
            Spacer(1, 12),
            Paragraph("<b>Recommendation:</b>", styles['Heading3']),
            Paragraph(content.replace('\n', '<br/>'), styles['Normal']),
        ]
        doc.build(elements)
        buffer.seek(0)
        return buffer

    if st.button("Get Recommendation"):
        prompt = f"""
        I am {age} years old, earning ₹{income}/month with {members} family members.
        I want insurance for: {goals}
        Recommend the best type of insurance policy (Health / Life / Vehicle / Term etc.) with reasons.
        """
        recommendation = ask_mistral(prompt)
        st.success("✅ Recommendation Generated:")
        st.write(recommendation)

        pdf = generate_advice_pdf(recommendation)
        st.download_button("📥 Download Recommendation PDF", data=pdf, file_name="Insurance_Recommendation.pdf", mime="application/pdf")


elif page == "Compare Policies":
    st.title("📊 Compare Two Policies")

    text1 = st.session_state.get("policy_1_text")
    text2 = st.session_state.get("policy_2_text")

    if text1 and text2:
        risk1 = calculate_risk_score(text1)
        risk2 = calculate_risk_score(text2)

        def get_strength_label(score):
            if score >= 80:
                return "Strong ✅"
            elif score >= 50:
                return "Moderate ⚠"
            else:
                return "Weak ❌"

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 Policy 1")
            st.markdown(f"**Risk Score:** {risk1}/100")
            st.markdown(f"**Coverage Strength:** {get_strength_label(risk1)}")
        with col2:
            st.subheader("📄 Policy 2")
            st.markdown(f"**Risk Score:** {risk2}/100")
            st.markdown(f"**Coverage Strength:** {get_strength_label(risk2)}")

        if st.button("Compare Policies with AI"):
            with st.spinner("Analyzing policies..."):
                try:
                    llm = Ollama(model="mistral")
                    prompt = f"""
You are an insurance policy comparison assistant.

Here are two policies:

Policy 1:
{text1[:1200]}

Policy 2:
{text2[:1200]}

Compare both policies in detail, considering:
- Coverage breadth and limits
- Exclusions and risky terms
- Policyholder benefits
- Risk exposure
- Any fine print red flags

Provide a side-by-side comparison, then clearly state which one is better and why.
Be fair, factual, and detailed in your reasoning.
"""
                    comparison = llm(prompt)
                    st.subheader("🧠 AI-Powered Comparison")
                    st.write(comparison)

                    st.download_button(
                        "📥 Download Comparison Report",
                        data=BytesIO(comparison.encode("utf-8")),
                        file_name="Policy_Comparison_Report.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Error during comparison: {e}")

    else:
        st.warning("Please upload two policies first in the 'Upload Policy' section.")
