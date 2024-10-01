export default function Search({disabled}: {disabled?: boolean}) {
    return <div className="w-full h-10 relative">
        <div className="absolute w-12 h-full top-0 left-0 z-10 flex place-items-center place-content-center">
            <span className="material-symbols-outlined select-none"
                  style={{color: "var(--hint-text)", fontSize: "1.25em", fontWeight: "600"}}>search</span>
        </div>
        <input placeholder={"Поиск в MineKatalog"} disabled={disabled}
               className="placeholder:text-[var(--hint-text)] bg-transparent peer focus-visible:outline-0 absolute z-10 top-1/2 -translate-y-[42%] left-11 w-5/6"/>
        <div
            className="w-full h-full bg-[var(--background)] peer-focus-visible:border-[2px] peer-focus-visible:border-[var(--hint-text)] rounded-full flex place-items-center pl-8 absolute top-0 left-0">
        </div>
    </div>
}