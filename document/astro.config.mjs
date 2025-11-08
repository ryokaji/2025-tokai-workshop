// @ts-check
import starlight from "@astrojs/starlight";
import { defineConfig } from "astro/config";

import plantuml from "astro-plantuml";

// https://astro.build/config
export default defineConfig({
  integrations: [
    starlight({
      title: "パスワードレス認証の仕組み",
      social: [],
      sidebar: [
        {
          label: "環境構築",
          autogenerate: { directory: "setup" },
        },
        {
          label: "はじめに",
          autogenerate: { directory: "introduction" },
        },
        {
          label: "仕組みを知る",
          autogenerate: { directory: "poc" },
        },
        {
          label: "ユーザ機能との協調",
          autogenerate: { directory: "practice" },
        },
        {
          label: "用語集",
          link: "/glossary",
        },
      ],
    }),
    plantuml(),
  ],
});
