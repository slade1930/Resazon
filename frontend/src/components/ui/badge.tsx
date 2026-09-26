import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors [&_svg]:pointer-events-none [&_svg]:size-3",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground",
        aji: "border-transparent bg-aji text-primary-foreground",
        maize: "border-transparent bg-maize text-marino-dark",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        outline: "border-border bg-card/60 text-foreground",
        success: "border-transparent bg-culantro/15 text-culantro-dark",
        warn: "border-transparent bg-maize-soft text-[oklch(0.4_0.1_70)]",
        destructive: "border-transparent bg-destructive/10 text-destructive",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

function Badge({
  className,
  variant,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return (
    <span
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  );
}

export { Badge, badgeVariants };