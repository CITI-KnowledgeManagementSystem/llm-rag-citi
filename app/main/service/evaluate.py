import asyncio
import torch
from datasets import Dataset
from ragas import evaluate
from ragas.llms import LlamaIndexLLMWrapper
from ...main import langchain_embedding_model as ragas_embed_model
from ragas.metrics import LLMContextPrecisionWithoutReference
from ragas.metrics import ContextRelevance
from ...main import generation_llm

from ragas.metrics import (
    faithfulness,
    answer_relevancy,
)
# ==========================================================
# ===== SETUP RAGAS - DILAKUKAN SEKALI SAAT APLIKASI START =====
# ==========================================================
print("[RAGAS Evaluator] Mulai inisialisasi model untuk evaluasi...")

# 1. Setup LLM untuk RAGAS
ragas_llm_llamaindex = generation_llm
ragas_llm = LlamaIndexLLMWrapper(llm=ragas_llm_llamaindex)

ragas_embed_model = ragas_embed_model

context_precision_metric = LLMContextPrecisionWithoutReference(llm=ragas_llm)
context_relevancy_metric = ContextRelevance(llm=ragas_llm)

# 4. Kumpulin semua juri dalam satu list
EVALUATION_METRICS = [
    faithfulness,
    answer_relevancy,
    context_precision_metric,
    context_relevancy_metric
]

print("✅ [RAGAS Evaluator] Semua model dan metrik siap.")

# ==========================================================
# ===== FUNGSI EVALUASI UTAMA =====
# ==========================================================
def evaluate_single_turn_rag(question: str, answer: str, contexts: list):
    """
    Fungsi ini menjalankan evaluasi RAGAS untuk satu interaksi tanya-jawab.
    """
    try:
        print(f"[RAGAS Evaluator] Menerima request evaluasi untuk pertanyaan: {question[:50]}...")

        eval_data = [{
            "question": question,
            "answer": answer,
            "contexts": contexts
        }]
        eval_dataset = Dataset.from_list(eval_data)

        # Menjalankan evaluasi sync di thread terpisah agar tidak memblokir aplikasi
        eval_result = evaluate(
            eval_dataset,
            metrics=EVALUATION_METRICS,
            llm=ragas_llm,
            embeddings=ragas_embed_model
        )

        # Di produksi, ini harusnya di-log ke file, database, atau platform monitoring
        print(f"\n[RAGAS Evaluator] Hasil Evaluasi Selesai:\n{eval_result}\n")

    except Exception as e:
        print(f"\n[RAGAS Evaluator] ❌ ERROR DI TUGAS BACKGROUND: {e}\n")
        import traceback
        traceback.print_exc() # Print traceback lengkapnya biar makin jelas
    
    return