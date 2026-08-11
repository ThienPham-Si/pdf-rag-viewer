const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type DocumentStatus = 'uploaded' | 'processing' | 'ready' | 'failed';

export interface Document {
  id: string;
  filename: string;
  status: DocumentStatus;
  page_count: number | null;
  created_at: string;
}

export async function fetchDocuments(token: string): Promise<Document[]> {
  const res = await fetch(`${API_URL}/documents`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function uploadDocument(file: File, token: string): Promise<Document> {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_URL}/documents/upload`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: formData
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Failed to upload document');
  }
  return res.json();
}

export async function deleteDocument(id: string, token: string): Promise<void> {
  const res = await fetch(`${API_URL}/documents/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Failed to delete document');
  }
}

