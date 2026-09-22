import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";

export function renderPlanApp(element: ReactElement, route = "/", width = 1440) {
  Object.defineProperty(window, "innerWidth", { configurable: true, value: width });
  window.dispatchEvent(new Event("resize"));
  return render(<MemoryRouter initialEntries={[route]}>{element}</MemoryRouter>);
}
