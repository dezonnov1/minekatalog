'use client'

import {useEffect, useState} from "react";
import Network from "@/lib/network";
import User from "@/lib/user";
import Header from "@/app/ui/Header";
import Categories, {Category} from "@/app/ui/Categories";
import clsx from "clsx";
import {gtEestiProDisplayRegular} from "@/app/fonts/fonts";
import GrassBlock from "@/public/Grass_Block.png";
import IronIngot from "@/public/Iron_Ingot.png";
import NetheriteChestplate from "@/public/Netherite_Chestplate.png";
import {StaticImport} from "next/dist/shared/lib/get-img-props";
import {MainSkeleton} from "@/app/ui/Skeletons";

export default function Home() {
    const [user, setUser] = useState<User | null>(null)
    const [firstLoad, setFirstLoad] = useState<boolean>(false)
    const [token, setToken] = useState<string | null>(null)
    useEffect(() => {
        window.Telegram.WebApp.setHeaderColor("#F2F5FA")
        const server = window.localStorage.getItem("server")
        if (server == null) {
            window.localStorage.setItem("server", "1")
        }

        async function updateUser(token) {
            const res = await Network.get("/api/me", token)
            if (res.status == 200) setUser(await res.json() as User)
            setTimeout(() => {
                updateUser(token)
            }, 10000)
        }

        async function getUser(token?: string) {
            if (token == null) {
                const data = await Network.post("/api/auth", {
                    "raw_init_data": window.Telegram.WebApp.initData,
                    "init_data": window.Telegram.WebApp.initDataUnsafe
                })
                if (data.status == 200) {
                    const user = await data.json() as User
                    setUser(user)
                    const t = data.headers.get("Authorization")
                    setToken(t)
                    window.onbeforeunload = function () {
                        window.sessionStorage.setItem("user", JSON.stringify(user))
                        window.sessionStorage.setItem("token", t)
                    }
                    return t
                }
            } else {
                const user = JSON.parse(window.sessionStorage.getItem("user"))
                setUser(user)
                setToken(token)
                window.onbeforeunload = function () {
                    window.sessionStorage.setItem("user", JSON.stringify(user))
                    window.sessionStorage.setItem("token", token)
                }
                window.sessionStorage.removeItem("user")
                window.sessionStorage.removeItem("token")
                return token
            }
        }

        const token = window.sessionStorage.getItem("token")
        if (token == null) setFirstLoad(true)
        getUser(token).then((t) => {
            updateUser(t)
        })
    }, []);
    if (user != null && token != null)
        return (
            <main
                className={clsx("flex flex-col gap-2 w-screen h-screen overflow-hidden", gtEestiProDisplayRegular.className)}>
                <Header user={user} name={window.Telegram.WebApp.initDataUnsafe.user.first_name}/>
                <Categories>
                    <Category name={"Блоки"} icon={GrassBlock as StaticImport} href={"/category/block"}
                              translate={true}/>
                    <Category name={"Ресурсы"} icon={IronIngot as StaticImport} href={"/category/item"}/>
                    <Category name={"Инстру\nменты"}
                              icon={"https://minekatalog.saddeststoryevertold.ru/icons/netherite_pickaxe.png"}
                              href={"/category/tool"} reverse={true} translate={true}/>
                    <Category name={"Броня"} icon={NetheriteChestplate as StaticImport} href={"/category/armor"}/>
                    <Category name={"Еда"} icon={"https://minekatalog.saddeststoryevertold.ru/icons/cake.png"}
                              href={"/category/food"}/>
                    {/*<Category name={"Оружие"}*/}
                    {/*          icon={"https://minekatalog.saddeststoryevertold.ru/icons/netherite_sword.png"}*/}
                    {/*          translate={true} href={"/category/weapon"} reverse={true}/>*/}
                </Categories>
            </main>
        );
    if (firstLoad)
    return (
        <MainSkeleton/>
    )
}
