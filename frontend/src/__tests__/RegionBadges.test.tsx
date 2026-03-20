import { render, screen } from "@testing-library/react";
import RegionBadges from "@/components/RegionBadges";

describe("RegionBadges", () => {
  it("renders region badges", () => {
    render(
      <RegionBadges
        regions={[
          { region_code: "ru", region_display: "Россия" },
          { region_code: "eu", region_display: "Европа" },
        ]}
      />,
    );
    expect(screen.getByText("RU")).toBeTruthy();
    expect(screen.getByText("EU")).toBeTruthy();
  });

  it("returns null for empty regions", () => {
    const { container } = render(<RegionBadges regions={[]} />);
    expect(container.innerHTML).toBe("");
  });

  it("falls back to region_display for unknown codes", () => {
    render(
      <RegionBadges regions={[{ region_code: "us", region_display: "USA" }]} />,
    );
    expect(screen.getByText("USA")).toBeTruthy();
  });
});
