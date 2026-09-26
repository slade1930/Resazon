import { cn } from "@/lib/utils";

export function LogoMark({ className }: { className?: string }) {
  return (
    <img
      src="/resazon.png"
      alt="ReSazón Loop"
      className={cn("size-9 shrink-0 rounded-lg object-contain", className)}
    />
  );
}

export function Logo({
  className,
  onLight: _onLight = true,
}: {
  className?: string;
  onLight?: boolean;
}) {
  return (
    <img
      src="/resazon.png"
      alt="ReSazón Loop — Sabor panameño"
      className={cn(
        "h-11 w-auto rounded-lg object-contain",
        _onLight ? "" : "drop-shadow-[0_1px_2px_rgba(0,0,0,0.35)]",
        className,
      )}
    />
  );
}