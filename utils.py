import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def validate_file(file_path: str) -> bool:
    if not os.path.exists(file_path):
        return False

    ext = Path(file_path).suffix.lower()
    if ext not in ['.pdf', '.docx', '.doc']:
        return False

    size = os.path.getsize(file_path)
    if size > 50 * 1024 * 1024:
        return False

    return True


def get_file_info(file_path: str) -> Dict:
    if not os.path.exists(file_path):
        return None

    stat = os.stat(file_path)
    return {
        "name": os.path.basename(file_path),
        "size_kb": round(stat.st_size / 1024, 2),
        "size_mb": round(stat.st_size / 1024 / 1024, 2),
        "extension": Path(file_path).suffix,
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    }


def format_sources(sources: List[Dict]) -> str:
    if not sources:
        return "No sources available"

    formatted = "Sources:\n\n"
    for i, source in enumerate(sources, 1):
        formatted += f"{i}. File: {source.get('source', 'Unknown')}\n"
        formatted += f"   Chunk: #{source.get('chunk_id', '?')}\n\n"

    return formatted


def format_chat_history(history: List[Dict]) -> str:
    if not history:
        return "No chat history"

    formatted = "Chat History:\n\n"
    for i, item in enumerate(history, 1):
        formatted += f"[{i}] Question: {item['question']}\n"
        formatted += f"Answer: {item['answer']}\n"
        formatted += "---\n\n"

    return formatted


def save_log(message: str, log_file: str = "logs/app.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")


def create_directories():
    for directory in ["data", "vectorstore", "logs"]:
        os.makedirs(directory, exist_ok=True)