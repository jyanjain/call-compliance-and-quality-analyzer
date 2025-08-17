import streamlit as st
import json
import os

from question1_regex import detect_profanity_regex
from question1_ml import detect_profanity_ml
from question2_regex import detect_privacy_violation_regex
from question2_llm import detect_privacy_violation_llm
from question3 import CallQualityAnalyzer


st.title("Call Compliance & Quality Analyzer")

folder = st.text_input("Enter folder path containing conversations:", "All_Conversations")

question = st.selectbox("Select Question:", ["", "Question 1 - Profanity Detection", "Question 2 - Privacy and Compliance Violation", "Question 3 - Call Quality Metrics Analysis"])

if question == "Question 1 - Profanity Detection":
    approach = st.radio("Select Approach:", ["Regex", "ML"])

    if st.button("Run Analysis"):
        if approach == "Regex":
            agent_calls, customer_calls = detect_profanity_regex(folder)
            output_file = "profane_regex_texts.json"

        elif approach == "ML":
            agent_calls, customer_calls = detect_profanity_ml(folder)
            output_file = "profane_ml_texts.json"

        st.success(f"Analysis complete! Results saved to {output_file}")

        st.subheader("🚨 Agent Profanity Call IDs")
        st.write(list(agent_calls) if agent_calls else "None found")

        st.subheader("🚨 Customer Profanity Call IDs")
        st.write(list(customer_calls) if customer_calls else "None found")

        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            st.download_button(
                label="Download Full JSON Results",
                data=json.dumps(data, indent=2),
                file_name=output_file,
                mime="application/json"
            )


elif question == "Question 2 - Privacy and Compliance Violation":
    approach = st.radio("Select Approach:", ["Regex", "LLM"])

    if st.button("Run Analysis"):
        if approach == "Regex":
            violating_calls = detect_privacy_violation_regex(folder, "privacy_violations_regex.json")
            output_file = "privacy_violations_regex.json"

        elif approach == "LLM":
            violating_calls = detect_privacy_violation_llm(folder, "privacy_violations_llm.json")
            output_file = "privacy_violations_llm.json"

        st.success(f"Analysis complete! Results saved to {output_file}")

        st.subheader("⚠️ Violating Call IDs")
        st.write(list(violating_calls) if violating_calls else "None found")

        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            st.download_button(
                label="Download Full JSON Results",
                data=json.dumps(data, indent=2),
                file_name=output_file,
                mime="application/json"
            )


elif question == "Question 3 - Call Quality Metrics Analysis":
    if st.button("Run Analysis"):
        analyzer = CallQualityAnalyzer()
        analyzer.load_all_calls(folder)
        metrics = analyzer.analyze_all_calls()
        output_file = "call_quality_metrics.json"
        analyzer.save_results_json(output_file)
        analyzer.create_visualizations()

        st.success(f"Analysis complete! Results saved to {output_file}")

        st.subheader("📊 Call IDs Analyzed")
        st.write(list(metrics["call_id"]) if not metrics.empty else "No calls analyzed")

        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            st.download_button(
                label="Download Full JSON Results",
                data=json.dumps(data, indent=2),
                file_name=output_file,
                mime="application/json"
            )
