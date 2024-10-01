import Image from "next/image";

export default function Avatar({avatar, defaultAvatar, name}: {avatar: string, defaultAvatar: boolean, name: string}) {
    return <div className="rounded-full h-full aspect-square flex place-content-center place-items-center text-white" style={{background: avatar}}>
        {defaultAvatar ? name.substring(1,1).toUpperCase() : <Image src={avatar} alt={name} width={48} height={48} className="rounded-full" quality={100} /> }
    </div>
}