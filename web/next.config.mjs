/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://api:5000/:path*',
            },
        ]
    },
    images: {domains: ["minekatalog.saddeststoryevertold.ru"]},
    reactStrictMode: false
};

export default nextConfig;
