import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

type SectionHeaderProps = {
  title: string;
  description?: string;
  badge?: string;
  badgeVariant?: "default" | "accent" | "success" | "warning" | "danger" | "outline";
  action?: React.ReactNode;
  className?: string;
};

export function SectionHeader({
  title,
  description,
  badge,
  badgeVariant = "outline",
  action,
  className,
}: SectionHeaderProps) {
  return (
    <div className={cn("flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between", className)}>
      <div className="space-y-1.5">
        <div className="flex flex-wrap items-center gap-2.5">
          <h2 className="text-lg font-semibold tracking-tight text-foreground sm:text-xl">
            {title}
          </h2>
          {badge ? <Badge variant={badgeVariant}>{badge}</Badge> : null}
        </div>
        {description ? (
          <p className="max-w-2xl text-sm leading-relaxed text-muted-foreground">
            {description}
          </p>
        ) : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
