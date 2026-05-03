import { create } from "zustand";

/** Separador centro: prompt (Monaco) vs viewport Three.js */
export type CenterTab = "prompt" | "viewport";

type ShellState = {
  sidebarOpen: boolean;
  bottomPanelOpen: boolean;
  activeCenterTab: CenterTab;
  selectedTopologyPath: string[] | null;

  toggleSidebar: () => void;
  toggleBottomPanel: () => void;
  setCenterTab: (tab: CenterTab) => void;
  selectTopologyPath: (path: string[] | null) => void;
};

export const useShellStore = create<ShellState>((set) => ({
  sidebarOpen: true,
  bottomPanelOpen: true,
  activeCenterTab: "prompt",
  selectedTopologyPath: null,

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  toggleBottomPanel: () => set((s) => ({ bottomPanelOpen: !s.bottomPanelOpen })),
  setCenterTab: (tab) => set({ activeCenterTab: tab }),
  selectTopologyPath: (path) => set({ selectedTopologyPath: path }),
}));
