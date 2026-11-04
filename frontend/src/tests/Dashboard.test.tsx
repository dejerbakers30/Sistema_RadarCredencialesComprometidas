import { render, screen } from "@testing-library/react";
import { QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { vi, describe, it, expect } from "vitest";
import Dashboard from "@/pages/Dashboard";
import { queryClient } from "@/lib/queryClient";
import * as useLeaksHook from "@/hooks/useLeaks";

describe("Dashboard", () => {
  it("renderiza KPIs", () => {
    vi.spyOn(useLeaksHook, "useKpis").mockReturnValue({
      data: { total: 10, nuevos: 3, contenidos: 7, mttc_min: 42.5 },
      isLoading: false, isError: false,
    } as any);
    vi.spyOn(useLeaksHook, "useDashboardSummary").mockReturnValue({
      data: { tendencia_diaria: [], por_severidad: [], top_breaches: [], resets_estado: [], reincidentes: [] },
      isLoading: false, isError: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <Dashboard />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("Total filtraciones")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
  });
});
