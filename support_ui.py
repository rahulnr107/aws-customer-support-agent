import json
import os
from uuid import uuid4

import boto3
import streamlit as st
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


st.set_page_config(page_title="AWS Customer Support", page_icon="💬")
st.title("Customer Support Assistant")
st.caption("Powered by Amazon Bedrock and AgentCore")
st.info(
    "Portfolio demo using fictional customer records. "
    "Refunds are simulations; no money moves or balances change."
)

runtime_arn = os.environ.get("AGENTCORE_RUNTIME_ARN")
if not runtime_arn:
    st.error("Set AGENTCORE_RUNTIME_ARN before starting this app.")
    st.stop()

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid4())
    st.session_state.messages = []

with st.sidebar:
    st.header("Try the demo")
    st.write("Customer: C-1001")
    st.write("• Show my recent orders.")
    st.write("• Simulate a USD 25 refund for ORD-5521.")
    st.caption("Each message uses billable AWS services.")

    if st.button("New conversation"):
        st.session_state.conversation_id = str(uuid4())
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("How can I help you?")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Contacting the support agent..."):
                client = boto3.client(
                    "bedrock-agentcore",
                    region_name="us-east-1",
                    config=Config(
                        connect_timeout=10,
                        read_timeout=120,
                        retries={"total_max_attempts": 1},
                    ),
                )

                response = client.invoke_agent_runtime(
                    agentRuntimeArn=runtime_arn,
                    runtimeSessionId=st.session_state.conversation_id,
                    contentType="application/json",
                    accept="application/json",
                    payload=json.dumps({"prompt": prompt}).encode("utf-8"),
                )

                body = response["response"]
                try:
                    result = json.loads(body.read())
                finally:
                    body.close()

                answer = result.get("reply")
                if not isinstance(answer, str) or not answer.strip():
                    raise ValueError("The agent returned no reply.")

            st.markdown(answer)

        except (BotoCoreError, ClientError, ValueError):
            answer = (
                "The request did not complete reliably. "
                "It was not automatically retried. "
                "If your AWS sign-in expired, refresh it in the terminal."
            )
            st.error(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )