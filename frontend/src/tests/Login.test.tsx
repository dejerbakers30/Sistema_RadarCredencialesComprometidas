import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import Login from "@/pages/Login";
import { queryClient } from "@/lib/queryClient";
import { describe, it, expect } from "vitest";

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Login", () => {
  it("renderiza formulario y valida email", async () => {
    renderWithProviders(<Login />);
    const email = screen.getByLabelText(/correo corporativo/i);
    await userEvent.type(email, "no-valido");
    await userEvent.click(screen.getByRole("button", { name: /acceder/i }));
    expect(await screen.findByText(/email inválido/i)).toBeInTheDocument();
  });
});
