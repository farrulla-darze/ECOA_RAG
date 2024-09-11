# model/test_url_database.py

import unittest
from unittest.mock import patch, MagicMock
from url_database import WebDatabase

class TestWebDatabase(unittest.TestCase):

    @patch('os.path.exists')
    @patch('langchain_community.vectorstores.Chroma')
    def test_init_chroma_db_exists(self, mock_chroma, mock_exists):
        # Mock os.path.exists to return True
        mock_exists.return_value = True

        # Initialize WebDatabase
        db = WebDatabase()

        # Check if Chroma was initialized with the correct parameters
        mock_chroma.assert_called_once_with(
            persist_directory="./chroma_db",
            embedding_function=MagicMock()
        )

    @patch('os.path.exists')
    @patch('langchain_community.vectorstores.Chroma')
    @patch('langchain_community.document_loaders.SeleniumURLLoader')
    @patch('langchain.text_splitter.RecursiveCharacterTextSplitter')
    def test_init_chroma_db_not_exists(self, mock_text_splitter, mock_loader, mock_chroma, mock_exists):
        # Mock os.path.exists to return False
        mock_exists.return_value = False

        # Mock SeleniumURLLoader to return documents
        mock_loader_instance = mock_loader.return_value
        mock_loader_instance.load.return_value = [MagicMock()]

        # Mock RecursiveCharacterTextSplitter to return splits
        mock_text_splitter_instance = mock_text_splitter.return_value
        mock_text_splitter_instance.split_documents.return_value = [MagicMock()]

        # Initialize WebDatabase
        db = WebDatabase.GetInstance()

        # Check if SeleniumURLLoader was called with the correct URLs
        mock_loader.assert_called_once_with(urls=db.mock_urls)
        mock_loader_instance.load.assert_called_once()

        # Check if RecursiveCharacterTextSplitter was called with the correct parameters
        mock_text_splitter.assert_called_once_with(chunk_size=1000, chunk_overlap=100)
        mock_text_splitter_instance.split_documents.assert_called_once_with(mock_loader_instance.load.return_value)

        # Check if Chroma was initialized with the correct parameters
        mock_chroma.from_documents.assert_called_once_with(
            documents=mock_text_splitter_instance.split_documents.return_value,
            embedding=MagicMock(),
            persist_directory="./chroma_db"
        )

if __name__ == '__main__':
    unittest.main()