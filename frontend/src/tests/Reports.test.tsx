import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import Reports from "@/pages/Reports";

const mutate = vi.fn();

vi.mock("@/hooks/useReports", () => ({
  useGenerateReport: () => ({ mutate, isPending: false }),
  downloadReport: vi.fn(),
}));

vi.mock("@/components/ui/toast", () => ({
  useToast: () => ({ push: vi.fn() }),
}));

describe("Reports", () => {
  it("deriva el formato permitido del tipo seleccionado", () => {
    render(<MemoryRouter><Reports /></MemoryRouter>);
    fireEvent.click(screen.getByRole("button", { name: /gestión/i }));
    fireEvent.change(screen.getByLabelText("Fecha desde"), { target: { value: "2026-01-01" } });
    fireEvent.change(screen.getByLabelText("Fecha hasta"), { target: { value: "2026-01-31" } });
    fireEvent.click(screen.getByRole("button", { name: /generar y descargar/i }));
    expect(mutate).toHaveBeenCalledWith(expect.objectContaining({ tipo: "gestion", formato: "docx" }), expect.any(Object));
  });

  it("rechaza un período invertido", () => {
    render(<MemoryRouter><Reports /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText("Fecha desde"), { target: { value: "2026-02-01" } });
    fireEvent.change(screen.getByLabelText("Fecha hasta"), { target: { value: "2026-01-01" } });
    expect(screen.getByRole("alert")).toHaveTextContent(/anterior o igual/i);
    expect(screen.getByRole("button", { name: /generar y descargar/i })).toBeDisabled();
  });
});
