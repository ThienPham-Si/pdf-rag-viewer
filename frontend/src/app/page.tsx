export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm flex flex-col gap-8">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl text-center">
          Document Intelligence
        </h1>
        <p className="text-xl text-slate-300 text-center max-w-2xl">
          Upload financial and legal PDFs. Ask questions. Get cited answers.
        </p>
        
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <div className="flex items-center gap-3 px-4 py-2 rounded-full bg-slate-900 border border-slate-800">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
            </span>
            <span className="text-sm font-medium text-slate-300">System initializing...</span>
          </div>
        </div>
      </div>
    </main>
  );
}
