import type { JSX } from "react";
import { getApiBase } from "../../lib/env";
import { useShellStore } from "../../stores/shellStore";

export type AppShellSlots = {
  explorerContent?: JSX.Element | null;
  centerPromptContent?: JSX.Element | null;
  centerViewportContent?: JSX.Element | null;
  bottomPanelContent?: JSX.Element | null;
};

/** Shell VS Code-inspired: explorer | centro tabs | inferior. */
export function AppShell({
  explorerContent,
  centerPromptContent,
  centerViewportContent,
  bottomPanelContent,
}: AppShellSlots) {
  const {
    sidebarOpen,
    bottomPanelOpen,
    activeCenterTab,
    toggleSidebar,
    toggleBottomPanel,
    setCenterTab,
  } = useShellStore();

  const sidebarWidth = sidebarOpen ? "min(288px, 32vw)" : "0";

  const bottomHeight = bottomPanelOpen ? "min(184px, 28vh)" : "0";

  return (
    <div className="app-root">
      <div className="top-row">
        <button type="button" data-testid="toggle-sidebar" onClick={toggleSidebar} aria-expanded={sidebarOpen}>
          Explorer
        </button>
        <button type="button" data-testid="toggle-bottom" onClick={toggleBottomPanel} aria-expanded={bottomPanelOpen}>
          Copilot / Job
        </button>
      </div>
      <div className="app-shell">
        <aside
          className="app-shell__sidebar"
          style={{ width: sidebarWidth, opacity: sidebarOpen ? 1 : 0 }}
          aria-hidden={!sidebarOpen}
        >
          <div className="panel-title">Explorer</div>
          {explorerContent ?? <div className="explorer-body muted">Topo (fase seguinte)</div>}
        </aside>
        <div className="app-shell__main">
          <div className="app-shell__center">
            <div className="app-shell__center-tabs" role="tablist">
              <button
                type="button"
                role="tab"
                className={activeCenterTab === "prompt" ? "is-active" : ""}
                onClick={() => setCenterTab("prompt")}
              >
                Prompt
              </button>
              <button
                type="button"
                role="tab"
                className={activeCenterTab === "viewport" ? "is-active" : ""}
                onClick={() => setCenterTab("viewport")}
              >
                Viewport 3D
              </button>
            </div>
            <div className="app-shell__center-body">
              {activeCenterTab === "prompt"
                ? (centerPromptContent ?? <PlaceholderPrompt />)
                : (centerViewportContent ?? (
                    <div className="viewport-placeholder">Viewport (pronto na fase seguinte)</div>
                  ))}
            </div>
          </div>
          <div
            className="app-shell__bottom"
            style={{ height: bottomHeight, overflow: bottomPanelOpen ? "auto" : "hidden" }}
            aria-hidden={!bottomPanelOpen}
          >
            <div className="panel-title">Copilot / Job</div>
            {bottomPanelContent ?? (
              <div className="explorer-body" style={{ color: "var(--text-muted)" }}>
                Estado de job será mostrado aqui após integração à API.
              </div>
            )}
          </div>
        </div>
      </div>
      <footer className="status-bar">API: {getApiBase()} (dev)</footer>
    </div>
  );
}

function PlaceholderPrompt() {
  return (
    <div className="explorer-body muted" style={{ color: "var(--text-muted)" }}>
      Prompt — integração Monaco nas ondas seguintes.
    </div>
  );
}
