export {};

declare global {
  interface Window {
    __controlsTest?: {
      getYaw: () => number;
      getSpeed: () => number;
      getX: () => number;
      getY: () => number;
      setKeys: (codes: string[]) => void;
      skipToWorld?: () => void;
    };
    __gemwar?: {
      getMode: () => string;
      skipToWorld: () => void;
      tapConfirm: () => void;
      [key: string]: unknown;
    };
  }
}
