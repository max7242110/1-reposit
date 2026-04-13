"use client";

import { useCallback, useEffect, useState } from "react";
import { Photo } from "@/lib/types";

interface Props {
  photos: Photo[];
}

export default function PhotoGallery({ photos }: Props) {
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  const goNext = useCallback(() => {
    setSelectedIdx((i) => Math.min(photos.length - 1, i + 1));
  }, [photos.length]);

  const goPrev = useCallback(() => {
    setSelectedIdx((i) => Math.max(0, i - 1));
  }, []);

  const closeLightbox = useCallback(() => setLightboxOpen(false), []);

  useEffect(() => {
    if (!lightboxOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") goNext();
      else if (e.key === "ArrowLeft") goPrev();
      else if (e.key === "Escape") closeLightbox();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [lightboxOpen, goNext, goPrev, closeLightbox]);

  useEffect(() => {
    document.body.style.overflow = lightboxOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [lightboxOpen]);

  if (photos.length === 0) return null;

  const current = photos[selectedIdx];

  return (
    <section aria-label="Фотографии">
      <div className="space-y-3">
        <div
          className="relative w-full rounded-xl overflow-hidden bg-white dark:bg-gray-900 flex items-center justify-center cursor-pointer"
          style={{ minHeight: "240px", maxHeight: "360px" }}
          onClick={() => setLightboxOpen(true)}
        >
          <img
            src={current.image_url}
            alt="Фото кондиционера"
            className="max-w-full max-h-[360px] object-contain"
          />
        </div>
        {photos.length > 1 && (
          <div className="flex gap-2 flex-wrap">
            {photos.map((p, idx) => (
              <button
                key={p.id}
                onClick={() => setSelectedIdx(idx)}
                className={`w-16 h-16 rounded-lg overflow-hidden border-2 transition-colors shrink-0 ${
                  idx === selectedIdx
                    ? "border-blue-500"
                    : "border-gray-200 dark:border-gray-700 hover:border-blue-300"
                }`}
              >
                <img src={p.image_url} alt="" className="w-full h-full object-cover" />
              </button>
            ))}
          </div>
        )}
      </div>

      {lightboxOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center"
          onClick={closeLightbox}
        >
          <button
            onClick={closeLightbox}
            className="absolute top-4 right-4 text-white/80 hover:text-white text-3xl leading-none z-10"
            aria-label="Закрыть"
          >
            &times;
          </button>

          {photos.length > 1 && selectedIdx > 0 && (
            <button
              onClick={(e) => { e.stopPropagation(); goPrev(); }}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-white/80 hover:text-white text-4xl leading-none z-10"
              aria-label="Предыдущее фото"
            >
              &#8249;
            </button>
          )}

          {photos.length > 1 && selectedIdx < photos.length - 1 && (
            <button
              onClick={(e) => { e.stopPropagation(); goNext(); }}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-white/80 hover:text-white text-4xl leading-none z-10"
              aria-label="Следующее фото"
            >
              &#8250;
            </button>
          )}

          <img
            src={current.image_url}
            alt="Фото кондиционера"
            className="max-w-[90vw] max-h-[90vh] object-contain"
            onClick={(e) => e.stopPropagation()}
          />

          {photos.length > 1 && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/70 text-sm">
              {selectedIdx + 1} / {photos.length}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
