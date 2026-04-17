import { Metadata } from "next";

import BackLink from "@/components/BackLink";
import SubmitForm from "@/components/SubmitForm";
import { getBrands, getPage } from "@/lib/api";

export const metadata: Metadata = {
  title: "Добавить кондиционер в рейтинг",
  description:
    "Как добавить свой кондиционер в независимый рейтинг «Август-климат»: инструкция и форма заявки.",
  alternates: { canonical: "/submit" },
  robots: { index: false, follow: true },
};

export const revalidate = 60;

export default async function SubmitPage() {
  const [page, brands] = await Promise.all([
    getPage("submit"),
    getBrands().catch(() => []),
  ]);

  return (
    <>
      <BackLink href="/" />

      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
        {page.title_ru}
      </h1>

      <article
        className="prose prose-gray dark:prose-invert max-w-none"
        dangerouslySetInnerHTML={{ __html: page.content_ru }}
      />

      <SubmitForm brands={brands} />
    </>
  );
}
