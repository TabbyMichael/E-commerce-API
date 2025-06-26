import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

class MockFirestore:
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}

    async def get_document(self, path: str, doc_id: str) -> Optional[Dict[str, Any]]:
        collection = self._data.get(path)
        if collection:
            return collection.get(doc_id)
        return None

    async def add_document(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if path not in self._data:
            self._data[path] = {}
        doc_id = str(uuid.uuid4())
        data["id"] = doc_id
        data["created_at"] = datetime.now().isoformat()
        data["updated_at"] = datetime.now().isoformat()
        self._data[path][doc_id] = data
        return data

    async def update_document(self, path: str, doc_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        collection = self._data.get(path)
        if collection and doc_id in collection:
            collection[doc_id].update(data)
            collection[doc_id]["updated_at"] = datetime.now().isoformat()
            return collection[doc_id]
        return None

    async def delete_document(self, path: str, doc_id: str) -> bool:
        collection = self._data.get(path)
        if collection and doc_id in collection:
            del collection[doc_id]
            return True
        return False

    async def query_collection(self, path: str, filters: Optional[Dict[str, Any]] = None, 
                               limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        collection = self._data.get(path, {})
        results = list(collection.values())

        if filters:
            for key, value in filters.items():
                results = [doc for doc in results if doc.get(key) == value]
        
        # Simple sorting by created_at for consistency, can be extended
        results.sort(key=lambda x: x.get("created_at", ""))

        if offset is not None:
            results = results[offset:]
        if limit is not None:
            results = results[:limit]
            
        return results

db = MockFirestore()