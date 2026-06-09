/**
 * Shared motion constants for consistent animation easing across all sections.
 * Using `as const` satisfies Framer Motion's strict Easing tuple type.
 */

export const EASE_OUT_EXPO = [0.16, 1, 0.3, 1] as [number, number, number, number];

export const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: EASE_OUT_EXPO },
  },
};

export const staggerContainer = (stagger = 0.1, delay = 0.1) => ({
  hidden: {},
  show: {
    transition: {
      staggerChildren: stagger,
      delayChildren: delay,
    },
  },
});
