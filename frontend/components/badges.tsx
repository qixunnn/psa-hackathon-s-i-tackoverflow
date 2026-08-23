import type { EventStatus, Severity } from "@/types/api";

export function StatusBadge({
  value,
  tone = "status",
}: {
  value: EventStatus | Severity;
  tone?: "status" | "severity";
}) {
  const className =
    tone === "severity"
      ? severityStyles[value as Severity]
      : "border-slate-200 bg-slate-100 text-slate-700";

  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold tracking-wide ${className}`}
    >
      {formatLabel(value)}
    </span>
  );
}

export function SyntheticBadge() {
  return (
    <span className="inline-flex rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold tracking-wide text-amber-800">
      Synthetic demo data
    </span>
  );
}

const severityStyles: Record<Severity, string> = {
  LOW: "border-emerald-200 bg-emerald-50 text-emerald-800",
  MEDIUM: "border-amber-200 bg-amber-50 text-amber-800",
  HIGH: "border-orange-200 bg-orange-50 text-orange-800",
  CRITICAL: "border-red-200 bg-red-50 text-red-800",
};

function formatLabel(value: string): string {
  return value.replaceAll("_", " ");
}
