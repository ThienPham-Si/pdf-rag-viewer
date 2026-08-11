import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_upload_document_success(client: AsyncClient):
    with patch("app.auth.verify_token") as mock_verify, \
         patch("app.main.upload_file_to_s3") as mock_s3:
        mock_verify.return_value = {"sub": "user_test_docs"}
        mock_s3.return_value = True

        files = {"file": ("test.pdf", b"dummy pdf content", "application/pdf")}
        response = await client.post(
            "/documents/upload",
            headers={"Authorization": "Bearer test_token"},
            files=files
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert data["status"] == "uploaded"
        assert "id" in data

@pytest.mark.asyncio
async def test_upload_document_invalid_type(client: AsyncClient):
    with patch("app.auth.verify_token") as mock_verify:
        mock_verify.return_value = {"sub": "user_test_docs"}

        files = {"file": ("test.txt", b"dummy txt content", "text/plain")}
        response = await client.post(
            "/documents/upload",
            headers={"Authorization": "Bearer test_token"},
            files=files
        )
        assert response.status_code == 400
        assert "Only PDF files are allowed" in response.json()["detail"]

@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient):
    with patch("app.auth.verify_token") as mock_verify, \
         patch("app.main.upload_file_to_s3") as mock_s3:
        mock_verify.return_value = {"sub": "user_test_docs"}
        mock_s3.return_value = True

        # upload first
        files = {"file": ("test.pdf", b"dummy pdf content", "application/pdf")}
        await client.post(
            "/documents/upload",
            headers={"Authorization": "Bearer test_token"},
            files=files
        )
        
        # list documents
        response = await client.get(
            "/documents",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["filename"] == "test.pdf"
        assert data[0]["status"] == "uploaded"
