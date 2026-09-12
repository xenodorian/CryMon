import { createFileRoute } from "@tanstack/react-router";
import { GemwarApp } from "@/components/gemwar-app";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return <GemwarApp />;
}
