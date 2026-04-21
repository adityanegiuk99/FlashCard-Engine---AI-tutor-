import "./globals.css";

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Flashcard Engine",
  description: "Convert PDFs into active recall decks with spaced repetition."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

