from typing import Type, List


from pydantic import BaseModel, Field, Extra

from gentopia.memory.embeddings import Embeddings, OpenAIEmbeddings
from gentopia.memory.vectorstores.chroma import Chroma
from gentopia.memory.vectorstores.vectorstore import VectorStore
from gentopia.tools.utils import Document
from gentopia.tools.utils.document_loaders.base_loader import BaseLoader
from gentopia.tools.utils.document_loaders.text_splitter import TextSplitter, _get_default_text_splitter


class VectorstoreIndexCreator(BaseModel):
    """Logic for creating indexes."""

    vectorstore_cls: Type[VectorStore] = Chroma
    embedding: Embeddings = Field(default_factory=OpenAIEmbeddings)
    text_splitter: TextSplitter = Field(default_factory=_get_default_text_splitter)
    vectorstore_kwargs: dict = Field(default_factory=dict)

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def from_loaders(self, loaders: List[BaseLoader]) -> VectorStore:
        """Create a vectorstore index from loaders."""
        docs = []
        for loader in loaders:
            docs.extend(loader.load())
        return self.from_documents(docs)

    def from_documents(self, documents: List[Document]) -> VectorStore:
        """Create a vectorstore index from documents."""
        sub_docs = self.text_splitter.split_documents(documents)
        vectorstore = self.vectorstore_cls.from_documents(
            sub_docs, self.embedding, **self.vectorstore_kwargs
        )
        return vectorstore