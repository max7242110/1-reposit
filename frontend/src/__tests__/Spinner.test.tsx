import { render, screen } from "@testing-library/react";
import Spinner from "@/components/Spinner";

describe("Spinner", () => {
  it("renders default text", () => {
    render(<Spinner />);
    expect(screen.getByText("Загрузка рейтинга...")).toBeTruthy();
  });

  it("renders custom text", () => {
    render(<Spinner text="Пожалуйста, подождите..." />);
    expect(screen.getByText("Пожалуйста, подождите...")).toBeTruthy();
  });

  it("has role=status for screen readers", () => {
    render(<Spinner />);
    expect(screen.getByRole("status")).toBeTruthy();
  });
});
