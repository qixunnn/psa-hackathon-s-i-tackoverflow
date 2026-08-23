export default function Loading() {
  return (
    <div aria-live="polite" aria-busy="true" className="animate-pulse space-y-8">
      <div className="space-y-3">
        <div className="h-4 w-40 rounded bg-slate-200" />
        <div className="h-10 w-full max-w-md rounded bg-slate-200" />
        <div className="h-5 w-full max-w-xl rounded bg-slate-200" />
      </div>
      <div className="h-72 rounded-xl border border-slate-200 bg-white" />
      <span className="sr-only">Loading risk intelligence</span>
    </div>
  );
}
