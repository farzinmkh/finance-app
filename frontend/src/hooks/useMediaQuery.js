import { useEffect, useState } from "react";

/**
 * Tracks whether a CSS media query currently matches.
 * Example: const isMobile = useMediaQuery("(max-width: 640px)");
 */
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(
    () => typeof window !== "undefined" && window.matchMedia(query).matches
  );

  useEffect(() => {
    const media = window.matchMedia(query);
    const handleChange = () => setMatches(media.matches);
    handleChange();
    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, [query]);

  return matches;
}

export const breakpoints = {
  mobile: "(max-width: 640px)",
  tablet: "(min-width: 641px) and (max-width: 1024px)",
  laptop: "(min-width: 1025px) and (max-width: 1439px)",
  desktop: "(min-width: 1440px)",
};
