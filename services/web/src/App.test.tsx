import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import App from "./App";
import { useShellStore } from "./stores/shellStore";

vi.mock("@monaco-editor/react", () => ({
  __esModule: true,
  default: () => <div data-testid="monaco-mock" />,
}));

describe("App", () => {
  it("shows Explorer and toggles sidebar", async () => {
    const user = userEvent.setup();
    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <App />
      </QueryClientProvider>,
    );

    expect(screen.getByTestId("toggle-sidebar")).toBeVisible();

    const toggle = screen.getByTestId("toggle-sidebar");
    expect(toggle).toHaveAttribute("aria-expanded", "true");

    await user.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(useShellStore.getState().sidebarOpen).toBe(false);

    await user.click(toggle);
    expect(useShellStore.getState().sidebarOpen).toBe(true);
  });
});
