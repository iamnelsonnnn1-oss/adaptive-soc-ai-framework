"use client";

import { useState } from "react";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { respondAsKai } from "@/lib/services/ai-charlie-service";
import type { Threat } from "@/lib/types";

interface AiCharlieChatProps {
  selectedThreat?: Threat;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function AiCharlieChat({ selectedThreat }: AiCharlieChatProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: "AI Security Analyst Kai online. Ask me to walk your triage shift." },
  ]);

  const send = () => {
    const question = input.trim();
    if (!question) return;
    const answer = respondAsKai(question, selectedThreat);
    setMessages((m) => [...m, { role: "user", content: question }, { role: "assistant", content: answer }]);
    setInput("");
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>AI Charlie Analyst</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="max-h-[360px] space-y-2 overflow-auto pr-1">
          {messages.map((message, idx) => (
            <motion.div
              key={`${message.role}-${idx}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={message.role === "assistant" ? "rounded-xl border border-cyan-400/20 bg-cyan-500/10 p-3 text-sm text-slate-100" : "rounded-xl border border-slate-600 bg-slate-800/60 p-3 text-sm text-slate-200"}
            >
              <p className="mb-1 text-xs uppercase text-slate-400">{message.role === "assistant" ? "Kai" : "Analyst"}</p>
              <pre className="whitespace-pre-wrap font-sans">{message.content}</pre>
            </motion.div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400/70"
            placeholder="Ask for triage guidance..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <Button onClick={send}>Send</Button>
        </div>
      </CardContent>
    </Card>
  );
}

