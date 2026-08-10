import { UserButton } from '@clerk/nextjs'

export default function DashboardPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex h-16 items-center justify-between border-b border-slate-800 px-6">
        <h1 className="text-xl font-semibold">Document Intelligence</h1>
        <UserButton afterSignOutUrl="/sign-in" />
      </header>
      
      <main className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-md space-y-6">
          <div className="rounded-full bg-slate-800 p-4 w-16 h-16 mx-auto flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8 text-slate-400">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold">No documents yet</h2>
          <p className="text-slate-400">
            Upload your first PDF to get started with document intelligence.
          </p>
          <button className="rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-500 transition-colors">
            Upload PDF
          </button>
        </div>
      </main>
    </div>
  )
}
