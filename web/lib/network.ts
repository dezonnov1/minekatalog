const Network = {
    get: async function (url: string, token?: string) {
        let initData = {}
        if (typeof token != "undefined") {
            initData = {headers: {Authorization: token}}
        }
        return await fetch(url, initData)
    },
    post: async function (url, body: unknown, token?: string) {
        const initData: RequestInit = {body: JSON.stringify(body), headers: {"Content-Type": "application/json"}, method: "POST"}
        if (typeof token != "undefined") {
            initData["headers"]["Authorization"] = token
        }
        return await fetch(url, initData)
    }
}

export default Network;