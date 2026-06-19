export default function PipelinePage() {
  return (
    <div className="space-y-8">
      <h1 className="font-serif text-4xl text-stone tracking-tight">Lead Pipeline Kanban</h1>
      <p className="text-stone-muted font-sans">Drag-and-drop pipeline management for AI-verified leads.</p>
      <div className="grid grid-cols-3 gap-6">
        {["New Leads", "Site Visit Scheduled", "Token Paid"].map((stage) => (
          <div key={stage} className="luxury-panel p-4 rounded-sm min-h-[400px]">
            <h3 className="font-sans text-sm text-brass uppercase tracking-wider mb-4">{stage}</h3>
            <div className="space-y-3">
              <div className="p-3 bg-sapphire border border-white/5 rounded-sm text-sm text-stone">Rajesh K. (Kharghar)</div>
              <div className="p-3 bg-sapphire border border-white/5 rounded-sm text-sm text-stone">Priya S. (Powai)</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
