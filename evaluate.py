import json
from datetime import datetime
from src.ingestion import DocumentIngestion
from src.qa_chain import QASystem


class Evaluator:

    def __init__(self, file_path: str):
        ingestion = DocumentIngestion()
        vectorstore = ingestion.ingest_document(file_path, "eval_doc")
        self.qa = QASystem(vectorstore)
        self.results = []

    def run(self):
        test_cases = [
            {
                "question": "Who are the parties in this contract?",
                "expected_keywords": ["ABC", "XYZ"]
            },
            {
                "question": "What is the contract duration?",
                "expected_keywords": ["12", "months"]
            },
            {
                "question": "What is the total value?",
                "expected_keywords": ["50,000", "$"]
            },
            {
                "question": "What are the termination conditions?",
                "expected_keywords": ["30", "notice"]
            },
            {
                "question": "Who is responsible for damages?",
                "expected_keywords": ["ABC"]
            }
        ]

        for i, test in enumerate(test_cases, 1):
            question = test["question"]
            keywords = test["expected_keywords"]

            result = self.qa.ask(question)
            answer = result["answer"]

            metrics = self.calculate_metrics(answer, keywords, result)

            self.results.append({
                "question": question,
                "answer": answer,
                "metrics": metrics
            })

        self.print_summary()
        self.save_report()

    def calculate_metrics(self, answer: str, keywords: list, result: dict) -> dict:
        found = sum(1 for kw in keywords if kw.lower() in answer.lower())
        keyword_score = found / len(keywords) if keywords else 0

        if len(answer) < 10 or "cannot find" in answer.lower():
            quality = "poor"
        elif keyword_score >= 0.5:
            quality = "good"
        else:
            quality = "fair"

        return {
            "keyword_score": keyword_score,
            "answer_length": len(answer),
            "num_sources": result.get("num_sources", 0),
            "guardrail": result.get("guardrail_triggered", False),
            "quality": quality
        }

    def print_summary(self):
        total = len(self.results)
        good = sum(1 for r in self.results if r["metrics"]["quality"] == "good")
        avg_score = sum(r["metrics"]["keyword_score"] for r in self.results) / total
        avg_sources = sum(r["metrics"]["num_sources"] for r in self.results) / total

        print("\nEvaluation Summary")
        print("=" * 60)
        print(f"Total Questions: {total}")
        print(f"Good Answers: {good}/{total} ({good/total:.0%})")
        print(f"Average Accuracy: {avg_score:.0%}")
        print(f"Average Sources: {avg_sources:.1f}")
        print("=" * 60)

    def save_report(self):
        total = len(self.results)
        good = sum(1 for r in self.results if r["metrics"]["quality"] == "good")
        avg_score = sum(r["metrics"]["keyword_score"] for r in self.results) / total

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_questions": total,
                "good_answers": good,
                "success_rate": round(good/total, 2),
                "avg_keyword_score": round(avg_score, 2)
            },
            "detailed_results": self.results
        }

        with open("evaluation_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print("\nReport saved: evaluation_report.json")


if __name__ == "__main__":
    evaluator = Evaluator("data/test_contract.pdf")
    evaluator.run()