import { createFileRoute } from "@tanstack/react-router";
import { CryMonApp } from "@/components/crymon-app";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return <CryMonApp />;
}