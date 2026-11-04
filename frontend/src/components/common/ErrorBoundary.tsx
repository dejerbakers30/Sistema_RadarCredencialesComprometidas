import { Component, ReactNode } from "react";
import { Button } from "@/components/ui/button";

interface Props { children: ReactNode }
interface State { error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };
  static getDerivedStateFromError(error: Error): State { return { error }; }
  componentDidCatch(error: Error) { console.error("ErrorBoundary", error); }

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center gap-4">
          <h1 className="text-xl font-semibold">Algo ha ido mal</h1>
          <p className="text-muted-foreground text-sm">{this.state.error.message}</p>
          <Button onClick={() => window.location.reload()}>Recargar</Button>
        </div>
      );
    }
    return this.props.children;
  }
}
