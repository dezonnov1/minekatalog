import clsx from "clsx";
import {gtEestiProDisplayRegular} from "@/app/fonts/fonts";
import Search from "@/app/ui/Search";

const shimmer =
    'before:absolute relative overflow-hidden before:inset-0 before:w-[150%] before:h-[150%] before:-translate-x-full before:animate-[shimmer_2s_infinite] before:bg-gradient-to-r before:from-transparent before:via-gray-200/60 before:to-transparent';

export function MainSkeleton() {
    return (
        <main
            className={clsx("flex flex-col gap-2 w-screen h-screen overflow-hidden", gtEestiProDisplayRegular.className)}>
            <div className="flex place-items-center place-content-between w-full h-16 p-2 select-none">
                <div
                    className={`${shimmer} relative overflow-hidden flex h-full aspect-square place-items-center place-content-center bg-[var(--secondary-bg)] rounded-full transition-all group before:`}/>
                <p className={clsx(gtEestiProDisplayRegular.className, "text-[var(--accent)]")}>MineKatalog</p>
                <div
                    className={`${shimmer} relative overflow-hidden bg-[var(--secondary-bg)] flex h-10 aspect-square place-items-center place-content-center rounded-full transition-all group`}>
                </div>
            </div>
            <div className={`w-full h-auto bg-[var(--secondary-bg)] rounded-xl flex flex-col gap-4 p-4 pb-0 dynamic`}>
                <Search disabled/>
                <div className="flex overflow-x-scroll rounded-xl w-auto h-24 gap-2 select-none text-sm">
                    <div
                        className={`${shimmer} min-w-[4.75rem] w-[4.75rem] bg-[var(--background)] rounded-xl text-[var(--hint-text)] h-full p-2 relative overflow-hidden cursor-pointer`}>
                        <div className={`w-3/4 h-4 bg-[var(--secondary-bg)] rounded-lg`}/>
                        <div className={`absolute right-0 bottom-0 w-12 h-12`}/>
                    </div>
                    <div
                        className={`${shimmer} min-w-[4.75rem] w-[4.75rem] bg-[var(--background)] rounded-xl text-[var(--hint-text)] h-full p-2 relative overflow-hidden cursor-pointer`}>
                        <div className={`w-3/4 h-4 bg-[var(--secondary-bg)] rounded-lg`}/>
                        <div className={`absolute right-0 bottom-0 w-12 h-12`}/>
                    </div>
                    <div
                        className={`${shimmer} min-w-[4.75rem] w-[4.75rem] bg-[var(--background)] rounded-xl text-[var(--hint-text)] h-full p-2 relative overflow-hidden cursor-pointer`}>
                        <div className={`w-3/4 h-4 bg-[var(--secondary-bg)] rounded-lg`}/>
                        <div className={`absolute right-0 bottom-0 w-12 h-12`}/>
                    </div>
                    <div
                        className={`${shimmer} min-w-[4.75rem] w-[4.75rem] bg-[var(--background)] rounded-xl text-[var(--hint-text)] h-full p-2 relative overflow-hidden cursor-pointer`}>
                        <div className={`w-3/4 h-4 bg-[var(--secondary-bg)] rounded-lg`}/>
                        <div className={`absolute right-0 bottom-0 w-12 h-12`}/>
                    </div>
                </div>
            </div>
            <div className={`${shimmer} w-full h-full rounded-xl bg-[var(--secondary-bg)]`} />
        </main>
    )
}