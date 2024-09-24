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
    reactStrictMode: false
};

export default nextConfig;
