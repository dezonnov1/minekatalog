'use client'

import {useEffect} from "react";

export default function Home() {
  useEffect(() => {
    window.Telegram.WebApp.setHeaderColor("#101014")
  }, []);
  return (
    <main>

    </main>
  );
}
