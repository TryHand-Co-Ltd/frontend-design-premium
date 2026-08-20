# LLM Streaming and AI Chat Patterns

Read this when implementing streaming chat, real-time AI responses, server-sent events, or progressive content rendering. This reference covers the UI contract for streaming — backend streaming implementation is outside the skill's scope.

## Streaming chat architecture

### Client-side pattern: fetch + ReadableStream

Use the Web Streams API to consume progressive responses. This is framework-agnostic and works with any LLM backend that returns SSE (Server-Sent Events):

```tsx
const [messages, setMessages] = useState<ChatMessage[]>([]);
const [isStreaming, setIsStreaming] = useState(false);
const [streamingContent, setStreamingContent] = useState("");
const [error, setError] = useState<string | null>(null);
const abortRef = useRef<AbortController | null>(null);

const sendMessage = useCallback(async (content: string) => {
  if (isStreaming) return;

  const userMsg: ChatMessage = { role: "user", content };
  setMessages((prev) => [...prev, userMsg]);
  setIsStreaming(true);
  setStreamingContent("");
  setError(null);

  abortRef.current = new AbortController();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: content, history: messages }),
      signal: abortRef.current.signal,
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);

    const reader = res.body?.getReader();
    if (!reader) throw new Error("No response stream");

    const decoder = new TextDecoder();
    let fullContent = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: true });
      const lines = text.split("\n");

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const data = line.slice(6).trim();

        if (data === "[DONE]") break;

        try {
          const parsed = JSON.parse(data);
          if (parsed.content) {
            fullContent += parsed.content;
            setStreamingContent(fullContent);
          }
        } catch {
          // partial JSON chunk — skip
        }
      }
    }

    setMessages((prev) => [...prev, { role: "assistant", content: fullContent }]);
    setStreamingContent("");
  } catch (err: any) {
    if (err.name === "AbortError") {
      setError("Response cancelled");
    } else {
      setError(err.message || "Failed to get response");
    }
  } finally {
    setIsStreaming(false);
    abortRef.current = null;
  }
}, [messages, isStreaming]);
```

### SSE format expected from the server

```
data: {"content":"The"}

data: {"content":" candidate"}

data: {"content":" scored"}

data: [DONE]
```

## Message display

### Rendered messages + streaming placeholder

```tsx
<div className="flex flex-col gap-4">
  {messages.map((msg, i) => (
    <ChatMessage key={i} message={msg} />
  ))}

  {isStreaming && (
    <div className="chat-message assistant">
      <p>{streamingContent}</p>
      {streamingContent === "" && <TypingIndicator />}
    </div>
  )}

  {error && (
    <div className="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">
      {error}
      <button onClick={() => retryLastMessage()} className="ml-2 underline">
        Retry
      </button>
    </div>
  )}

  <div ref={messagesEndRef} />
</div>
```

### Typing indicator

```tsx
function TypingIndicator() {
  return (
    <span className="inline-flex items-center gap-1" aria-label="Generating response">
      <span className="size-1.5 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: "0ms" }} />
      <span className="size-1.5 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: "150ms" }} />
      <span className="size-1.5 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: "300ms" }} />
    </span>
  );
}
```

## Input area with send + abort

```tsx
<div className="flex items-end gap-2 border-t p-4">
  <textarea
    value={input}
    onChange={(e) => setInput(e.target.value)}
    onKeyDown={(e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(input);
        setInput("");
      }
    }}
    placeholder="Ask about this analysis…"
    rows={1}
    className="flex-1 resize-none rounded-lg border p-3 text-sm"
    disabled={isStreaming}
  />
  {isStreaming ? (
    <button onClick={abortRef.current?.abort} className="rounded-lg bg-destructive px-4 py-2 text-sm text-white">
      Stop
    </button>
  ) : (
    <button
      onClick={() => { sendMessage(input); setInput(""); }}
      disabled={!input.trim()}
      className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground disabled:opacity-50"
    >
      Send
    </button>
  )}
</div>
```

## Suggested questions

After receiving a response, offer contextual follow-up questions:

```tsx
const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);

useEffect(() => {
  if (report) {
    setSuggestedQuestions(generateSuggestedQs(report));
  }
}, [report]);

// In JSX
{suggestedQuestions.length > 0 && !isStreaming && (
  <div className="flex flex-wrap gap-2">
    {suggestedQuestions.map((q) => (
      <button
        key={q}
        onClick={() => sendMessage(q)}
        className="rounded-full border px-3 py-1 text-xs hover:bg-muted"
      >
        {q}
      </button>
    ))}
  </div>
)}
```

## States

| State | Visual | Behavior |
|-------|--------|----------|
| Idle | Input enabled, send button visible | — |
| Streaming | Input disabled, cancel/stop button, streaming content below messages, typing indicator if empty | Auto-scroll, preserve scroll position on manual scroll-up |
| Complete | Full assistant message added, streaming state cleared | Suggested questions appear |
| Error | Error banner with message + retry button | Preserve user message, allow resend |
| Cancelled | "Response cancelled" banner | Clear partial content, enable input |
| Empty history | Suggested questions visible | — |

## Auto-scroll behavior

```tsx
const messagesEndRef = useRef<HTMLDivElement>(null);
const userScrolledUp = useRef(false);

useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages, streamingContent]);

// Detect user scroll-up to prevent forcing position
const handleScroll = () => {
  const el = messagesContainerRef.current;
  if (!el) return;
  userScrolledUp.current = el.scrollHeight - el.scrollTop - el.clientHeight > 100;
};
```

## History management

- Maintain a `messages` array with `{ role: "user" | "assistant", content: string }`.
- Send the full history with each request so the LLM has conversational context.
- For long conversations, summarize or truncate old messages to fit the model's context window.
- Persist conversation to localStorage or the database only when the user explicitly saves.

## Accessibility

- Live region: announce when new content arrives.
  ```html
  <div aria-live="polite" aria-atomic="false">{streamingContent}</div>
  ```
- Typing indicator has `aria-label="Generating response"`.
- Error messages use `role="alert"`.
- Enter sends, Shift+Enter newline. Communicate this in placeholder or tooltip.
- Focus stays in the input after send.

## Do's and Don'ts

- **Do:** Use AbortController for cancellation — both client and server must respect it.
- **Do:** Show a clear visual state for streaming, complete, error, and cancelled.
- **Do:** Allow keyboard Send (Enter) without Shift; use Shift+Enter for newline.
- **Do:** Auto-scroll to new content, but respect manual scroll-up.
- **Do:** Preserve the user's message in the input or history on error so they can retry.
- **Don't:** Block the entire UI during streaming — the input should remain accessible for the next message or abort.
- **Don't:** Render streaming content dangerously (no `dangerouslySetInnerHTML` without sanitization).
- **Don't:** Send the entire raw response text in the history — trim or structure it.
- **Don't:** Assume the server will send well-formed JSON in every chunk — handle partial lines gracefully.
