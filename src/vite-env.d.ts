/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Override the hero HLS manifest without touching source. */
  readonly VITE_HERO_HLS_SRC?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
