import * as React from "react";
import { ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type GetStartedButtonProps = React.ComponentProps<typeof Button>;

export function GetStartedButton({
  className,
  children = "Get Started",
  ...props
}: GetStartedButtonProps) {
  return (
    <Button
      className={cn(
        "group relative min-h-[48px] w-full overflow-hidden shadow-md transition-shadow duration-200 hover:shadow-lg",
        className
      )}
      size="lg"
      {...props}
    >
      <span className="mr-8 transition-opacity duration-200 group-hover:opacity-0">
        {children}
      </span>
      <span
        className="absolute bottom-1 right-1 top-1 z-10 grid w-1/4 place-items-center rounded-sm bg-primary-foreground/15 text-primary-foreground transition-all duration-200 group-hover:w-[calc(100%-0.5rem)] group-active:scale-95 group-hover:bg-primary-foreground/25"
        aria-hidden
      >
        <ChevronRight size={16} strokeWidth={2} />
      </span>
    </Button>
  );
}
