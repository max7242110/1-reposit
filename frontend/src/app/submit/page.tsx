import { Metadata } from "next";

import BackLink from "@/components/BackLink";
import { getPage } from "@/lib/api";

export const metadata: Metadata = {
  title: "Добавить кондиционер в рейтинг",
  description:
    "Как добавить свой кондиционер в независимый рейтинг «Август-климат»: инструкция и форма заявки.",
};

export const revalidate = 60;

export default async function SubmitPage() {
  const page = await getPage("submit");

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
    </>
  );
}
