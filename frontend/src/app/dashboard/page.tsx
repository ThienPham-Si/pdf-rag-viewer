import { UserButton } from '@clerk/nextjs'
import { UploadZone } from '@/components/UploadZone'
import { DocumentList } from '@/components/DocumentList'

export default function DashboardPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-900/50 px-6 backdrop-blur-sm sticky top-0 z-10">
        <h1 className="text-xl font-semibold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          Document Intelligence
        </h1>
        <UserButton />
      </header>
      
      <main className="flex-1 w-full max-w-4xl mx-auto p-6 md:p-8 space-y-8">
        <div>
          <h2 className="text-2xl font-bold text-slate-100 mb-6">Upload Document</h2>
          <UploadZone />
        </div>
        
        <div className="pt-6 border-t border-slate-800">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">Your Documents</h2>
          <DocumentList />
        </div>
      </main>
    </div>
  )
}
