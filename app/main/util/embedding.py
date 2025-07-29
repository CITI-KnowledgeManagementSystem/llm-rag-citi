import httpx
from typing import List, Dict, Any
from langchain_core.embeddings import Embeddings

# Kelas ini sama, tapi kita akan lebih sering pake metode sync-nya
class CustomAPIEmbeddings(Embeddings):

    def __init__(self, api_url: str, model_name: str = "bge-m3", timeout: int = 30):
        self.api_url = f"{api_url}"
        self.model_name = model_name
        self.timeout = timeout

    def _call_api(self, content: str) -> Dict[str, Any]:
        """Helper pribadi buat manggil API."""
        try:
            request_data = {
                "content": content,
                "model": self.model_name,
                "return_dense": True,
                "return_sparse": True
            }
            with httpx.Client() as client:
                response = client.post(self.api_url, json=request_data, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                if "dense_embeddings" not in result or "sparse_embeddings" not in result:
                    raise ValueError("API response tidak lengkap, 'dense_embeddings' atau 'sparse_embeddings' tidak ditemukan.")
                return {
                    "dense": result["dense_embeddings"],
                    "sparse": result["sparse_embeddings"]
                }
        except httpx.RequestError as e:
            print(f"Request exception: {e}")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e

    # --- METODE UTAMA LO (INI YANG LO PAKE) ---
    
    def embed_query(self, text: str) -> List[float]:
        """
        [WAJIB LANGCHAIN]
        Hanya mengembalikan DENSE embedding untuk query.
        """
        # Panggil helper, tapi AMBIL dense-nya AJA
        return self._call_api(text)["dense"]

    # Metode ini juga harus HANYA return dense
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._call_api(text)["dense"] for text in texts]
    
    # Metode custom lo buat hybrid TETAP ADA
    def embed_with_hybrid_support(self, text: str) -> Dict[str, Any]:
        return self._call_api(text)

    
    # Metode async bisa dihapus atau diabaikan karena kita di lingkungan Flask sync
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        # Implementasi async tidak akan terpakai di Flask standar
        pass
    async def aembed_query(self, text: str) -> List[float]:
        # Implementasi async tidak akan terpakai di Flask standar
        pass