import asyncio
import torch
from datasets import Dataset
from ragas import evaluate
from ragas.llms import LlamaIndexLLMWrapper
from ...main import langchain_embedding_model as ragas_embed_model
from ragas.metrics import LLMContextPrecisionWithoutReference
from ragas.metrics import ContextRelevance
from ...main import generation_llm
import os
from opik.integrations.langchain import OpikTracer
from opik import track

from ragas.metrics import (
    FaithfulnesswithHHEM,
    answer_relevancy,
)

import requests
from ..constant.llm import FRONTEND_SERVER_EVALUATE_URL
import math

os.environ["OPIK_API_KEY"] = os.getenv('OPIK_API_KEY')
os.environ["OPIK_WORKSPACE"] = os.getenv('OPIK_WORKSPACE')
os.environ["OPIK_PROJECT_NAME"] = os.getenv('OPIK_PROJECT_NAME')


# ==========================================================
# ===== SETUP RAGAS - DILAKUKAN SEKALI SAAT APLIKASI START =====
# ==========================================================
print("[RAGAS Evaluator] Initialize model for evaluating...")

# 1. Setup LLM untuk RAGAS
ragas_llm_llamaindex = generation_llm
ragas_llm = LlamaIndexLLMWrapper(llm=ragas_llm_llamaindex)

ragas_embed_model = ragas_embed_model

context_precision_metric = LLMContextPrecisionWithoutReference(llm=ragas_llm)
context_relevancy_metric = ContextRelevance(llm=ragas_llm)

faithfulness = FaithfulnesswithHHEM()
# 4. Kumpulin semua juri dalam satu list
EVALUATION_METRICS = [
    faithfulness,
    answer_relevancy,
    context_precision_metric,
    context_relevancy_metric
]

print("✅ [RAGAS Evaluator] Model is ready to use.")

def sanitize_score(score):
    try:
        score = float(score)
        if not math.isfinite(score):
            return None
        return score
    except:
        return None

# ==========================================================
# ===== FUNGSI EVALUASI UTAMA =====
# ==========================================================
def evaluate_single_turn_rag(message_id: str, question: str, answer: str, contexts: list):
    """
    Fungsi ini menjalankan evaluasi RAGAS untuk satu interaksi tanya-jawab.
    """
    try:
        print(f"[RAGAS Evaluator] Receiving evaluation request for: {question[:50]}...")

        eval_data = [{
            "question": question,
            "answer": answer,
            "contexts": contexts
        }]
        eval_dataset = Dataset.from_list(eval_data)

        opik_tracer_eval = OpikTracer(tags=["ragas_eval"], metadata={"evaluation_run": True})

        # Menjalankan evaluasi sync di thread terpisah agar tidak memblokir aplikasi
        eval_result = evaluate(
            eval_dataset,
            metrics=EVALUATION_METRICS,
            llm=ragas_llm,
            embeddings=ragas_embed_model,
            callbacks=[opik_tracer_eval],
        )
       
        print(f"\n[RAGAS Evaluator] Evaluation Complete:\n{eval_result}\n")

        # scores_payload = {
        #     "faithfulness": sanitize_score(eval_result['faithfulness']),
        #     "answer_relevancy": sanitize_score(eval_result['answer_relevancy']),
        #     "context_precision": sanitize_score(eval_result['llm_context_precision_without_reference']),
        #     "context_relevance": sanitize_score(eval_result['nv_context_relevance'])
        # }

        # headers = {
        #     "Content-Type": "application/json",
        #     "x-internal-secret": os.getenv("INTERNAL_SECRET_KEY") 
        # }

        # update_url = f"{FRONTEND_SERVER_EVALUATE_URL}{message_id}"

        # print("Skor mentah dari RAGAS:", eval_result)
        # print("Payload ke frontend:", scores_payload)
        # print("Target URL:", update_url)

        # response = requests.patch(update_url, json=scores_payload, headers=headers, timeout=10)
        # response.raise_for_status()


    except Exception as e:
        print(f"\n[RAGAS Evaluator] ❌ ERROR IN BACKGROUND: {e}\n")
        import traceback
        traceback.print_exc() # Print traceback lengkapnya biar makin jelas
    
    return