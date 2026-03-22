import { render, screen } from "@testing-library/react";
import RatingTableV2 from "@/components/RatingTableV2";
import { ACModelSummary } from "@/lib/types";

jest.mock("next/link", () => {
  return function MockLink({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) {
    return <a href={href}>{children}</a>;
  };
});

const mockModels: ACModelSummary[] = [
  {
    id: 1,
    brand: "Daikin",
    inner_unit: "FTXB25C",
    series: "Comfora",
    nominal_capacity: 2.5,
    total_index: 85.5,
    index_max: 100,
    publish_status: "published",
    region_availability: [
      { region_code: "ru", region_display: "Россия" },
    ],
  },
  {
    id: 2,
    brand: "Mitsubishi",
    inner_unit: "MSZ-LN25VGW",
    series: "Premium",
    nominal_capacity: 2.5,
    total_index: 92.1,
    index_max: 100,
    publish_status: "published",
    region_availability: [
      { region_code: "ru", region_display: "Россия" },
      { region_code: "eu", region_display: "Европа" },
    ],
  },
];

describe("RatingTableV2", () => {
  it("renders all models", () => {
    render(<RatingTableV2 models={mockModels} />);
    expect(screen.getByText("Daikin")).toBeTruthy();
    expect(screen.getByText("Mitsubishi")).toBeTruthy();
  });

  it("displays total_index and scale max", () => {
    render(<RatingTableV2 models={mockModels} />);
    expect(screen.getByText("85.5")).toBeTruthy();
    expect(screen.getByText("92.1")).toBeTruthy();
    expect(screen.getAllByText("100").length).toBeGreaterThanOrEqual(2);
  });

  it("renders accessible table with caption", () => {
    render(<RatingTableV2 models={mockModels} />);
    expect(screen.getByRole("table")).toBeTruthy();
  });

  it("renders column headers with scope", () => {
    const { container } = render(<RatingTableV2 models={mockModels} />);
    const ths = container.querySelectorAll("th[scope='col']");
    expect(ths.length).toBe(5);
  });

  it("renders links to v2 model detail pages", () => {
    render(<RatingTableV2 models={mockModels} />);
    const links = screen.getAllByRole("link");
    expect(links[0].getAttribute("href")).toBe("/v2/model/1");
    expect(links[1].getAttribute("href")).toBe("/v2/model/2");
  });

  it("renders model unit names", () => {
    render(<RatingTableV2 models={mockModels} />);
    expect(screen.getAllByText("FTXB25C").length).toBeGreaterThan(0);
    expect(screen.getAllByText("MSZ-LN25VGW").length).toBeGreaterThan(0);
  });

  it("renders empty table body for empty data", () => {
    render(<RatingTableV2 models={[]} />);
    const rows = screen.queryAllByRole("row");
    expect(rows.length).toBe(1); // header row only
  });
});
