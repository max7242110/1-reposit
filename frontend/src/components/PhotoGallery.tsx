"use client";

import { useState } from "react";
import { Photo } from "@/lib/types";

interface Props {
  photos: Photo[];
}

export default function PhotoGallery({ photos }: Props) {
  const [selectedIdx, setSelectedIdx] = useState(0);
  if (photos.length === 0) return null;

  const current = photos[selectedIdx];

  return (
    <section aria-label="Фотографии">
      <div className="space-y-3">
        <div className="relative w-full rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800 flex items-center justify-center" style={{ minHeight: "240px", maxHeight: "360px" }}>
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
    </section>
  );
}
