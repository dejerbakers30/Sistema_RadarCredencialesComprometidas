import { render, screen } from "@testing-library/react";
import { QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { vi, describe, it, expect } from "vitest";
import LeaksList from "@/pages/LeaksList";
import { queryClient } from "@/lib/queryClient";
import * as useLeaksHook from "@/hooks/useLeaks";

describe("LeaksList", () => {
  it("muestra filas cuando hay datos", () => {
    vi.spyOn(useLeaksHook, "useLeaks").mockReturnValue({
      data: [{
        id: "1", email_corporativo: "a@b.com", usuario_id: null,
        breach_origen: "Demo", breach_dominio: null, fecha_breach: null,
        fecha_deteccion: new Date().toISOString(), severidad: "alta",
        fuente_detalle: null, datos_expuestos: null, estado: "nuevo",
        fecha_contencion: null, hash_canonico: "x",
      }],
      isLoading: false, isError: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <LeaksList />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("a@b.com")).toBeInTheDocument();
    expect(screen.getByText("Demo")).toBeInTheDocument();
  });
});
