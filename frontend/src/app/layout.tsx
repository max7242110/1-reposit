import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { getRatingYear } from "@/lib/year";

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export function generateMetadata(): Metadata {
  const year = getRatingYear();
  return {
    metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
    title: {
      default: `Рейтинг кондиционеров ${year}`,
      template: "%s | Рейтинг кондиционеров и отзывы",
    },
    description:
      "Независимый рейтинг бытовых кондиционеров на основе реальных измерений: шум, вибрация, качество комплектующих и функциональность.",
    alternates: {
      canonical: "/",
    },
    openGraph: {
      title: `Рейтинг кондиционеров ${year}`,
      description:
        "Независимый рейтинг бытовых кондиционеров на основе реальных измерений.",
      type: "website",
      locale: "ru_RU",
    },
    twitter: {
      card: "summary_large_image",
      title: `Рейтинг кондиционеров ${year}`,
      description:
        "Независимый рейтинг бытовых кондиционеров на основе реальных измерений.",
    },
    robots: {
      index: true,
      follow: true,
    },
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const year = getRatingYear();
  return (
    <html lang="ru">
      <body className={`${inter.className} bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 antialiased`}>
        <header className="border-b border-gray-200 dark:border-gray-800">
          <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
            <Link
              href="/"
              className="text-xl font-bold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            >
              Рейтинг кондиционеров
            </Link>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {year}
            </span>
          </div>
        </header>
        <main className="max-w-5xl mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-200 dark:border-gray-800 mt-16">
          <div className="max-w-5xl mx-auto px-4 py-6 flex flex-col items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex flex-wrap justify-center gap-x-4 gap-y-2">
              <Link
                href="/methodology"
                className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
              >
                Методика рейтинга
              </Link>
              <Link
                href="/submit"
                className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
              >
                Добавить в рейтинг
              </Link>
              <Link
                href="/archive"
                className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
              >
                Архивные модели
              </Link>
            </div>
            <span>Данные основаны на независимых измерениях и тестированиях</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
