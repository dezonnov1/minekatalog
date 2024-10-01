import {gtEestiProDisplayRegular} from "@/app/fonts/fonts";
import clsx from "clsx"
import Avatar from "@/app/ui/Avatar";
import User from "@/lib/user";
import Link from "next/link";

export default function Header({user, name}: {user: User, name: string}) {
    return (
        <div className="flex place-items-center place-content-between w-full h-16 px-4 py-2 select-none">
            <div id={"menu"} className={"absolute overflow-hidden flex gap-2 px-4 h-screen py-2 text-white select-text top-0 left-0 w-screen bg-[var(--accent)] z-50 hidden"}>
                <button className="absolute right-0 top-0 -translate-x-full translate-y-2/3 select-none" onClick={() => {
                    document.getElementById("menu").classList.toggle("animate-[menu_0.25s]")
                    document.getElementById("menu").classList.toggle("animate-[close_0.25s]")

                    setTimeout(() => {
                        if (!document.getElementById("menu").classList.contains("hidden")) {
                            document.getElementById("menu").classList.toggle("hidden")
                            window.Telegram.WebApp.setHeaderColor("#F2F5FA")
                        }
                    }, 240)

                }}>
                    <span className="material-symbols-outlined">close</span>
                </button>
                <div className="flex flex-col px-4 pt-8 text-xl gap-2">
                    <Link href={`/${window.localStorage.getItem("server")}/profile`}>Профиль</Link>
                    <p>{`Баланс: ${typeof user.balance[window.localStorage.getItem("server")] != "undefined" ? user.balance[window.localStorage.getItem("server")] : 0}`}</p>
                    <p>Корзина</p>
                    <Link href={`/support`}>Поддержка</Link>
                </div>
            </div>
            <button onClick={() => {}} className={"flex h-full aspect-square place-items-center place-content-center bg-[var(--secondary-bg)] rounded-full transition-all group"}><span style={{fontSize: "1.75em"}} className="material-symbols-outlined transition-colors duration-200 group-hover:text-[var(--accent)]">location_on</span></button>
            <p className={clsx(gtEestiProDisplayRegular.className, "text-[var(--accent)]")}>MineKatalog</p>
            <button onClick={() => {
                if (document.getElementById("menu").classList.contains("hidden")) {
                    document.getElementById("menu").classList.toggle("hidden")
                }
                document.getElementById("menu").classList.toggle("animate-[menu_0.25s]")
                if (document.getElementById("menu").classList.contains("animate-[close_0.25s]")) document.getElementById("menu").classList.toggle("animate-[close_0.25s]")
                window.Telegram.WebApp.setHeaderColor("#0066FF")
            }} className={"flex h-10 aspect-square place-items-center place-content-center rounded-full transition-all group"}>
                <Avatar avatar={user.avatar} defaultAvatar={user.default_avatar} name={name} />
            </button>
        </div>
    )
}