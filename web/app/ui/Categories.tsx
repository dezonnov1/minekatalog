import Image from "next/image";
import Search from "@/app/ui/Search";
import {StaticImport} from "next/dist/shared/lib/get-img-props";
import clsx from "clsx";
import Link from "next/link";

export function Category({name, icon, href, translate, reverse}: {name: string, icon: StaticImport|string, href: string, translate?: boolean, reverse?: boolean}) {
    return <Link href={href} className="min-w-[4.75rem] w-[4.75rem] bg-[var(--background)] rounded-xl text-[var(--hint-text)] h-full p-2 relative overflow-hidden cursor-pointer">
        <p>{name}</p>
        <Image src={icon} alt={name} className={clsx("absolute right-0 bottom-0", {"translate-x-1 translate-y-1": translate}, {"-scale-x-100": reverse})} width={48} height={48} quality={100} />
    </Link>
}

export default function Categories({children}: {children: unknown}) {
    return <div className={`w-full h-auto bg-[var(--secondary-bg)] rounded-xl flex flex-col gap-4 p-4 pb-0 dynamic`}>
        <Search />
        <div className="flex overflow-x-scroll rounded-xl w-auto h-24 gap-2 select-none text-sm">
            {children}
        </div>
    </div>
}