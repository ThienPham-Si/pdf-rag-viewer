'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, Loader2 } from 'lucide-react'
import { useAuth } from '@clerk/nextjs'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { uploadDocument } from '../lib/api'

export function UploadZone() {
  const { getToken } = useAuth()
  const queryClient = useQueryClient()
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: async (file: File) => {
      const token = await getToken()
      if (!token) throw new Error('Not authenticated')
      return uploadDocument(file, token)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      setErrorMsg(null)
    },
    onError: (err: Error) => {
      setErrorMsg(err.message || 'Failed to upload')
    }
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return
    const file = acceptedFiles[0]
    
    // Validate size (50MB) and type
    if (file.size > 50 * 1024 * 1024) {
      setErrorMsg('File size exceeds 50MB limit')
      return
    }
    if (file.type !== 'application/pdf') {
      setErrorMsg('Only PDF files are allowed')
      return
    }
    
    mutation.mutate(file)
  }, [mutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    multiple: false
  })

  return (
    <div className="w-full space-y-4">
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-500/10' : 'border-slate-700 hover:border-slate-600 hover:bg-slate-800/50'
        }`}
      >
        <input {...getInputProps()} />
        {mutation.isPending ? (
          <div className="flex flex-col items-center justify-center space-y-2">
            <Loader2 className="w-10 h-10 animate-spin text-blue-500" />
            <p className="text-slate-300 font-medium">Uploading document...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="rounded-full bg-slate-800 p-4">
              <UploadCloud className="w-8 h-8 text-slate-400" />
            </div>
            <p className="text-slate-300 font-medium">
              {isDragActive ? 'Drop the PDF here' : 'Drag & drop a PDF, or click to browse'}
            </p>
            <p className="text-sm text-slate-500">Max size 50MB. PDF files only.</p>
          </div>
        )}
      </div>
      
      {errorMsg && (
        <div className="p-3 rounded-lg bg-red-500/20 text-red-400 text-sm border border-red-500/30 text-center font-medium">
          {errorMsg}
        </div>
      )}
    </div>
  )
}
