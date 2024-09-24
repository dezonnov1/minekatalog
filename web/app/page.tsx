'use client'

import {useEffect, useState} from "react";
import Network from "@/lib/network";
import User from "@/lib/user";

export default function Home() {
  const [user, setUser] = useState<User|null>(null)
  useEffect(() => {
    window.Telegram.WebApp.setHeaderColor("#101014")
    async function getUser() {
      const data = await Network.post("/api/auth", {"raw_init_data": window.Telegram.WebApp.initData, "init_data": window.Telegram.WebApp.initDataUnsafe})
      if (data.status == 200) {
        setUser(await data.json() as User)
      }
    }
    getUser()
  }, []);
  if (user != null)
  return (
    <main>
      <p>АУФ</p>
    </main>
  );
}
