import { useEffect } from "react";

export function usePageTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} | TrendScout` : "TrendScout";
    return () => {
      document.title = "TrendScout";
    };
  }, [title]);
}
