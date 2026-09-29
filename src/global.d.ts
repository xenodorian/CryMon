export {};

declare global {
  /** Build-time hash of public/sprites (vite.config.ts define). */
  const __ART_VERSION__: string | undefined;
  interface Window {
    __controlsTest?: {
      getYaw: () => number;
      getSpeed: () => number;
      getX: () => number;
      getY: () => number;
      setKeys: (codes: string[]) => void;
      skipToWorld?: () => void;
    };
    __crymon?: {
      getMode: () => string;
      skipToWorld: () => void;
      tapConfirm: () => void;
      [key: string]: unknown;
    };
  }
}
