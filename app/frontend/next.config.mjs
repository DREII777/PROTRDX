import { config } from "dotenv";
config({ path: "../.env" });

const nextConfig = {
  output: "standalone",
  experimental: {
    appDir: true
  }
};

export default nextConfig;
