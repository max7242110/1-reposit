import { render, screen } from "@testing-library/react";
import VideoLinks from "@/components/VideoLinks";

describe("VideoLinks", () => {
  it("renders all video links", () => {
    render(
      <VideoLinks
        youtube_url="https://youtu.be/test123"
        rutube_url="https://rutube.ru/video/test/"
        vk_url="https://vk.com/video-123"
      />
    );
    expect(screen.getByText("YouTube")).toBeTruthy();
    expect(screen.getByText("RuTube")).toBeTruthy();
    expect(screen.getByText("VK Видео")).toBeTruthy();
  });

  it("renders YouTube embed when URL provided", () => {
    const { container } = render(
      <VideoLinks
        youtube_url="https://youtu.be/tgN0W83hQh4"
        rutube_url=""
        vk_url=""
      />
    );
    const iframe = container.querySelector("iframe");
    expect(iframe).not.toBeNull();
    expect(iframe?.src).toContain("youtube.com/embed/tgN0W83hQh4");
  });

  it("renders YouTube embed iframe with title", () => {
    const { container } = render(
      <VideoLinks youtube_url="https://youtu.be/tgN0W83hQh4" rutube_url="" vk_url="" />
    );
    const iframe = container.querySelector("iframe");
    expect(iframe).not.toBeNull();
    expect(iframe?.getAttribute("title")).toBe("YouTube видеообзор");
  });

  it("returns null when no URLs provided", () => {
    const { container } = render(
      <VideoLinks youtube_url="" rutube_url="" vk_url="" />
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders only available links", () => {
    render(
      <VideoLinks
        youtube_url="https://youtu.be/test123"
        rutube_url=""
        vk_url=""
      />
    );
    expect(screen.getByText("YouTube")).toBeTruthy();
    expect(screen.queryByText("RuTube")).toBeNull();
    expect(screen.queryByText("VK Видео")).toBeNull();
  });

  it("opens links in new tab with security attributes", () => {
    render(
      <VideoLinks
        youtube_url="https://youtu.be/test123"
        rutube_url=""
        vk_url=""
      />
    );
    const link = screen.getByText("YouTube").closest("a");
    expect(link?.getAttribute("target")).toBe("_blank");
    expect(link?.getAttribute("rel")).toBe("noopener noreferrer");
  });

  it("has aria-labels on links", () => {
    render(
      <VideoLinks
        youtube_url="https://youtu.be/test123"
        rutube_url="https://rutube.ru/test/"
        vk_url="https://vk.com/test"
      />
    );
    const youtubeLink = screen.getByText("YouTube").closest("a");
    expect(youtubeLink?.getAttribute("aria-label")).toContain("YouTube");
  });

  it("renders section with aria-label", () => {
    const { container } = render(
      <VideoLinks youtube_url="https://youtu.be/test" rutube_url="" vk_url="" />
    );
    const section = container.querySelector("section[aria-label]");
    expect(section).not.toBeNull();
  });

  it("renders heading", () => {
    render(
      <VideoLinks youtube_url="https://youtu.be/test" rutube_url="" vk_url="" />
    );
    expect(screen.getByText("Видеообзор")).toBeTruthy();
  });
});
