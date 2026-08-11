'use client'

import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@clerk/nextjs'
import { fetchDocuments, Document } from '../lib/api'
import { FileText, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react'

function StatusBadge({ status }: { status: Document['status'] }) {
  switch (status) {
    case 'uploaded':
    case 'processing':
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-2.5 py-0.5 text-xs font-medium text-amber-500 border border-amber-500/20">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          {status === 'uploaded' ? 'Uploaded' : 'Processing'}
        </span>
      )
    case 'ready':
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-500 border border-emerald-500/20">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Ready
        </span>
      )
    case 'failed':
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-red-500/10 px-2.5 py-0.5 text-xs font-medium text-red-500 border border-red-500/20">
          <AlertCircle className="w-3.5 h-3.5" />
          Failed
        </span>
      )
  }
}

export function DocumentList() {
  const { getToken } = useAuth()
  
  const { data: documents, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const token = await getToken()
      if (!token) throw new Error('Not authenticated')
      return fetchDocuments(token)
    },
    refetchInterval: 5000 // poll every 5s for status updates
  })

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <Loader2 className="w-8 h-8 animate-spin text-slate-500" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-center font-medium">
        Failed to load documents
      </div>
    )
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-12 px-4 rounded-xl border border-slate-800 bg-slate-900/50">
        <div className="rounded-full bg-slate-800/80 p-4 w-16 h-16 mx-auto flex items-center justify-center mb-4">
          <FileText className="w-8 h-8 text-slate-400" />
        </div>
        <h3 className="text-lg font-medium text-slate-200">No documents yet</h3>
        <p className="text-slate-400 mt-1">
          Upload your first PDF above to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {documents.map(doc => (
        <div 
          key={doc.id} 
          className="flex items-center justify-between p-4 rounded-xl border border-slate-800 bg-slate-900/30 hover:bg-slate-900/60 transition-colors"
        >
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="p-2 rounded-lg bg-blue-500/10 shrink-0">
              <FileText className="w-5 h-5 text-blue-500" />
            </div>
            <div className="min-w-0">
              <p className="font-medium text-slate-200 truncate">{doc.filename}</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {new Date(doc.created_at).toLocaleDateString()}
                {doc.page_count && ` • ${doc.page_count} pages`}
              </p>
            </div>
          </div>
          <div className="shrink-0 ml-4">
            <StatusBadge status={doc.status} />
          </div>
        </div>
      ))}
    </div>
  )
}
