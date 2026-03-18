interface Props {
  youtube_url: string;
  rutube_url: string;
  vk_url: string;
}

function extractYoutubeId(url: string): string | null {
  const match = url.match(
    /(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([a-zA-Z0-9_-]{11})/
  );
  return match ? match[1] : null;
}

export default function VideoLinks({
  youtube_url,
  rutube_url,
  vk_url,
}: Props) {
  const hasAny = youtube_url || rutube_url || vk_url;
  if (!hasAny) return null;

  const youtubeId = youtube_url ? extractYoutubeId(youtube_url) : null;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Видеообзор
      </h2>

      {youtubeId && (
        <div className="aspect-video rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
          <iframe
            src={`https://www.youtube.com/embed/${youtubeId}`}
            title="YouTube видеообзор"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="w-full h-full"
          />
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        {youtube_url && (
          <a
            href={youtube_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm font-medium hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
            </svg>
            YouTube
          </a>
        )}
        {rutube_url && (
          <a
            href={rutube_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 text-sm font-medium hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
          >
            RuTube
          </a>
        )}
        {vk_url && (
          <a
            href={vk_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-400 text-sm font-medium hover:bg-sky-100 dark:hover:bg-sky-900/40 transition-colors"
          >
            VK Видео
          </a>
        )}
      </div>
    </div>
  );
}
