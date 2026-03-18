import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export const metadata: Metadata = {
  title: {
    default: "Рейтинг кондиционеров 2026",
    template: "%s | Рейтинг кондиционеров",
  },
  description:
    "Независимый рейтинг бытовых кондиционеров на основе реальных измерений: шум, вибрация, качество комплектующих и функциональность.",
  openGraph: {
    title: "Рейтинг кондиционеров 2026",
    description:
      "Независимый рейтинг бытовых кондиционеров на основе реальных измерений.",
    type: "website",
    locale: "ru_RU",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body className={`${inter.className} bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 antialiased`}>
        <header className="border-b border-gray-200 dark:border-gray-800">
          <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
            <a href="/" className="text-xl font-bold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              Рейтинг кондиционеров
            </a>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              2026
            </span>
          </div>
        </header>
        <main className="max-w-5xl mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-200 dark:border-gray-800 mt-16">
          <div className="max-w-5xl mx-auto px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
            Данные основаны на независимых измерениях и тестированиях
          </div>
        </footer>
      </body>
    </html>
  );
}
