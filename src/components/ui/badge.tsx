import { cn } from "@/lib/utils";

export function Badge({
  className,
  tone = "muted",
  children,
}: {
  className?: string;
  tone?: "muted" | "accent" | "warn" | "live";
  children: React.ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-medium tracking-wide uppercase",
        tone === "muted" && "bg-raised text-muted",
        tone === "accent" && "bg-accent/15 text-accent",
        tone === "warn" && "bg-warn/15 text-warn",
        tone === "live" && "bg-accent/15 text-accent",
        className,
      )}
    >
      {tone === "live" ? (
        <span className="size-1.5 rounded-full bg-accent" aria-hidden />
      ) : null}
      {children}
    </span>
  );
}
