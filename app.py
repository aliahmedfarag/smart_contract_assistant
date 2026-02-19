import gradio as gr
import requests
import os

API_URL = "http://127.0.0.1:8000"


def upload_file(file):
    if file is None:
        return "Please upload a file", ""

    try:
        print(f"[UPLOAD] Uploading file: {file.name}")
        
        with open(file.name, "rb") as f:
            files = {"file": (os.path.basename(file.name), f)}
            response = requests.post(f"{API_URL}/upload", files=files)

        if response.status_code == 200:
            data = response.json()
            print(f"[UPLOAD] Success: {data['filename']}")
            status = f"Document processed successfully!\n\nFilename: {data['filename']}"
            info = f"**Status:** {data['status']}\n**Message:** {data['message']}"
            return status, info
        else:
            error = response.json()['detail']
            print(f"[UPLOAD] Error: {error}")
            return f"Error: {error}", ""

    except Exception as e:
        print(f"[UPLOAD] Exception: {str(e)}")
        return f"Error: {str(e)}", ""


def ask_question(question, chat_history):
    if not question.strip():
        return chat_history, ""

    try:
        print(f"[ASK] Question: {question}")
        
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question, "k": 4}
        )

        if response.status_code == 200:
            data = response.json()
            answer = data['answer']
            print(f"[ASK] Answer received: {answer[:50]}...")
            
            sources_text = "**Sources:**\n\n"
            for i, src in enumerate(data['sources'], 1):
                sources_text += f"{i}. {src['source']} (Chunk #{src['chunk_id']})\n"
            
            chat_history.append((question, answer))
            return chat_history, sources_text

        else:
            error = response.json()['detail']
            print(f"[ASK] Error: {error}")
            chat_history.append((question, f"Error: {error}"))
            return chat_history, ""

    except Exception as e:
        print(f"[ASK] Exception: {str(e)}")
        chat_history.append((question, f"Error: {str(e)}"))
        return chat_history, ""


def clear_chat():
    try:
        print("[CLEAR] Clearing chat history")
        requests.delete(f"{API_URL}/history")
        print("[CLEAR] History cleared")
    except Exception as e:
        print(f"[CLEAR] Error: {str(e)}")
    return [], ""


def get_summary():
    try:
        print("[SUMMARY] Requesting document summary")
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": "Summarize this document in clear points", "k": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            summary = data['answer']
            print(f"[SUMMARY] Summary received")
            return f"**Document Summary:**\n\n{summary}"
        else:
            return "Cannot generate summary. Please upload a document first."
            
    except Exception as e:
        print(f"[SUMMARY] Error: {str(e)}")
        return f"Error: {str(e)}"


def show_history():
    try:
        print("[HISTORY] Fetching chat history")
        response = requests.get(f"{API_URL}/history")
        
        if response.status_code == 200:
            data = response.json()
            history = data['history']
            
            if not history:
                return "No chat history"
            
            formatted = "**Chat History:**\n\n"
            for i, item in enumerate(history, 1):
                formatted += f"**[{i}] Q:** {item['question']}\n"
                formatted += f"**A:** {item['answer']}\n\n"
            
            print(f"[HISTORY] Found {len(history)} items")
            return formatted
        else:
            return "Cannot retrieve history"
            
    except Exception as e:
        print(f"[HISTORY] Error: {str(e)}")
        return "Server not running"


def get_stats():
    try:
        print("[STATS] Fetching statistics")
        response = requests.get(f"{API_URL}/history")
        
        if response.status_code == 200:
            data = response.json()
            total = data['total']
            print(f"[STATS] Total questions: {total}")
            return f"**Total Questions:** {total}\n**Server:** Connected"
        else:
            return "Cannot retrieve stats"
            
    except Exception as e:
        print(f"[STATS] Error: {str(e)}")
        return "Server not running"


def check_connection():
    try:
        print("[CONNECTION] Checking server connection")
        response = requests.get(f"{API_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            status = "Connected" if data['status'] == 'healthy' else "Not Ready"
            doc_loaded = "Yes" if data['document_loaded'] else "No"
            print(f"[CONNECTION] Server: {status}, Document: {doc_loaded}")
            return f"**Server Status:** {status}\n**Document Loaded:** {doc_loaded}"
        else:
            return "Cannot connect to server"
            
    except Exception as e:
        print(f"[CONNECTION] Error: {str(e)}")
        return "Server not running. Please start server.py first."


custom_css = """
.gradio-container {
    max-width: 1400px;
    margin: auto;
}
"""

with gr.Blocks(title="Smart Contract Assistant", theme=gr.themes.Soft(), css=custom_css) as demo:

    gr.Markdown("# Smart Contract Assistant\nAI-Powered Document Analysis System (Connected to FastAPI)")

    with gr.Tabs():

        with gr.Tab("Upload Document"):
            gr.Markdown("Upload your contract or document (PDF, DOCX)")

            with gr.Row():
                with gr.Column():
                    file_input = gr.File(label="Select File", file_types=[".pdf", ".docx", ".doc"])
                    upload_btn = gr.Button("Process Document", variant="primary", size="lg")

                with gr.Column():
                    upload_status = gr.Textbox(label="Status", lines=3, interactive=False)
                    file_info_output = gr.Textbox(label="File Details", lines=3, interactive=False)

            upload_btn.click(fn=upload_file, inputs=[file_input], outputs=[upload_status, file_info_output])

        with gr.Tab("Chat"):
            gr.Markdown("Ask questions about your document")

            with gr.Row():
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(label="Conversation", height=500, show_copy_button=True)
                    question_input = gr.Textbox(label="Your Question", placeholder="What are the main terms?", lines=2)

                    with gr.Row():
                        submit_btn = gr.Button("Send", variant="primary", scale=2)
                        clear_btn = gr.Button("Clear", scale=1)

                with gr.Column(scale=1):
                    sources_display = gr.Textbox(label="Sources", lines=10, interactive=False)

                    with gr.Row():
                        summary_btn = gr.Button("Summarize")
                        history_btn = gr.Button("History")
                        stats_btn = gr.Button("Stats")
                        connect_btn = gr.Button("Connection")

                    extra_output = gr.Textbox(label="Results", lines=8, interactive=False)

            submit_btn.click(fn=ask_question, inputs=[question_input, chatbot], outputs=[chatbot, sources_display]).then(fn=lambda: "", outputs=[question_input])
            question_input.submit(fn=ask_question, inputs=[question_input, chatbot], outputs=[chatbot, sources_display]).then(fn=lambda: "", outputs=[question_input])
            clear_btn.click(fn=clear_chat, outputs=[chatbot, sources_display])
            summary_btn.click(fn=get_summary, outputs=[extra_output])
            history_btn.click(fn=show_history, outputs=[extra_output])
            stats_btn.click(fn=get_stats, outputs=[extra_output])
            connect_btn.click(fn=check_connection, outputs=[extra_output])

        with gr.Tab("About"):
            gr.Markdown("""
            ## About This System
            
            This system is connected to a FastAPI backend server.
            
            ### Architecture
            - Frontend: Gradio UI (Port 7860)
            - Backend: FastAPI Server (Port 8000)
            - Communication: REST API
            
            ### Technology Stack
            - LLM: Groq API (LLaMA 3.3-70B)
            - Framework: LangChain
            - Vector Store: FAISS
            - Embeddings: HuggingFace
            - Interface: Gradio
            - API: FastAPI + LangServe
            
            ### How to Use
            1. Start FastAPI server: `python server.py`
            2. Start Gradio UI: `python app.py`
            3. Upload document and ask questions
            
            Version 1.0.0
            """)

    gr.Markdown("Smart Contract Assistant | Frontend connected to FastAPI Backend")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Starting Gradio UI - Connected to FastAPI")
    print("Make sure FastAPI server is running on port 8000")
    print("="*60 + "\n")
    demo.launch(server_name="0.0.0.0", server_port=7860)