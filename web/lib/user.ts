interface Order {
    id: number,
    order_id: string,
    status: string,
    items: unknown
}

interface Shop {
    id: number,
    shop_id: string,
    name: string,
    mc_nickname: string,
    position: {x: number, y: number, z: number},
    rating: number,
    working: boolean,
    work_time: {open_time: number, close_time: number},
    subscribe_paid?: boolean,
    promos?: {promo: string, give: number, uses: number, max_uses: number}[],
}

export default interface User {
    id: number,
    tg_id: number,
    language: string,
    balance: unknown,
    cart: unknown,
    linked_cards: unknown,
    shops: Shop[],
    orders: Order[],
    type?: string,
    avatar: string,
    default_avatar: boolean
}