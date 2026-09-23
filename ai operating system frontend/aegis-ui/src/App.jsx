import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [interrupt, setInterrupt] = useState(null);
  const [threads, setThreads] = useState([]);
  const [activeThread, setActiveThread] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadThreads();
  }, []);

  async function loadThreads() {
    try {
      const response = await fetch(`${API_URL}/threads`);

      if (!response.ok) {
        throw new Error("Could not load threads");
      }

      const data = await response.json();

      setThreads(data);

      if (data.length > 0) {
        setActiveThread(data[0].thread_id);
        loadThread(data[0].thread_id);
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function createNewChat() {
    try {
      const response = await fetch(`${API_URL}/threads`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Could not create thread");
      }

      const data = await response.json();

      setThreads((oldThreads) => [
        ...oldThreads,
        {
          thread_id: data.thread_id,
        },
      ]);

      setActiveThread(data.thread_id);
      setMessages([]);
    } catch (error) {
      console.error(error);
    }
  }

  async function loadThread(threadId) {
    try {
      const response = await fetch(
        `${API_URL}/threads/${threadId}`
      );

      if (!response.ok) {
        throw new Error("Could not load thread");
      }

      const data = await response.json();

      setMessages(
        data.messages
          .filter(
            (message) =>
              message.type === "human" ||
              message.type === "ai"
          )
          .map((message) => ({
            sender:
              message.type === "human"
                ? "user"
                : "aegis",
            content: message.content,
          }))
      );
    } catch (error) {
      console.error(error);
    }
  }

  async function selectThread(threadId) {
    setActiveThread(threadId);
    setInterrupt(null);
    await loadThread(threadId);
  }

  async function sendMessage() {
    if (!input.trim() || !activeThread || loading) {
      return;
    }

    const message = input.trim();

    setInput("");
    setLoading(true);

    setMessages((oldMessages) => [
      ...oldMessages,
      {
        sender: "user",
        content: message,
      },
    ]);

    try {
      const response = await fetch(
        `${API_URL}/threads/${activeThread}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: message,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Could not send message");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, {
          stream: true,
        });

        const lines = buffer.split("\n");

        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim()) {
            continue;
          }

          const data = JSON.parse(line);

          if (data.type === "message") {
            setMessages((oldMessages) => {
              const updatedMessages = [...oldMessages];

              const lastMessage =
                updatedMessages[updatedMessages.length - 1];

              if (
                lastMessage &&
                lastMessage.sender === "aegis"
              ) {
                updatedMessages[
                  updatedMessages.length - 1
                ] = {
                  ...lastMessage,
                  content:
                    lastMessage.content + data.content,
                };
              } else {
                updatedMessages.push({
                  sender: "aegis",
                  content: data.content,
                });
              }

              return updatedMessages;
            });
          }

          if (data.type === "interrupt") {
            setInterrupt(data.message);
            setLoading(false);
            return;
          }
        }
      }
    } catch (error) {
      console.error(error);

      setMessages((oldMessages) => [
        ...oldMessages,
        {
          sender: "aegis",
          content: "Unable to connect to Aegis.",
        },
      ]);
    }

    setLoading(false);
  }

  async function resumeAction(approved) {
    setInterrupt(null);
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/threads/${activeThread}/resume`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            approved: approved,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Could not resume action");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, {
          stream: true,
        });

        const lines = buffer.split("\n");

        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim()) {
            continue;
          }

          const data = JSON.parse(line);

          if (data.type === "message") {
            setMessages((oldMessages) => {
              const updatedMessages = [...oldMessages];

              const lastMessage =
                updatedMessages[updatedMessages.length - 1];

              if (
                lastMessage &&
                lastMessage.sender === "aegis"
              ) {
                updatedMessages[
                  updatedMessages.length - 1
                ] = {
                  ...lastMessage,
                  content:
                    lastMessage.content + data.content,
                };
              } else {
                updatedMessages.push({
                  sender: "aegis",
                  content: data.content,
                });
              }

              return updatedMessages;
            });
          }

          if (data.type === "interrupt") {
            setInterrupt(data.message);
            setLoading(false);
            return;
          }
        }
      }
    } catch (error) {
      console.error(error);

      setMessages((oldMessages) => [
        ...oldMessages,
        {
          sender: "aegis",
          content: "Unable to resume the action.",
        },
      ]);
    }

    setLoading(false);
  }

  return (
    <div className="app">

      {/* HITL POPUP */}

      {interrupt && (
        <div className="popup-overlay">

          <div className="confirmation-popup">

            <div className="popup-title">
              Aegis Confirmation
            </div>

            <div className="popup-message">
              {interrupt}
            </div>

            <div className="popup-buttons">

              <button
                className="popup-no"
                onClick={() => resumeAction(false)}
              >
                No
              </button>

              <button
                className="popup-yes"
                onClick={() => resumeAction(true)}
              >
                Yes
              </button>

            </div>

          </div>

        </div>
      )}

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="logo">
          AEGIS
        </div>

        <button
          className="new-chat"
          onClick={createNewChat}
        >
          + New Chat
        </button>

        <div className="recent-title">
          Recent Chats
        </div>

        <div className="chat-list">

          {threads.map((thread, index) => (
            <button
              key={thread.thread_id}
              className={`chat-item ${
                activeThread === thread.thread_id
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                selectThread(thread.thread_id)
              }
            >
              Chat {index + 1}
            </button>
          ))}

        </div>

      </aside>

      {/* CHAT */}

      <main className="chat-area">

        <div className="messages">

          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${
                message.sender === "user"
                  ? "user-message"
                  : "aegis-message"
              }`}
            >

              <div className="message-name">
                {message.sender === "user"
                  ? "YOU"
                  : "AEGIS"}
              </div>

              <div className="message-content">
                {message.content}
              </div>

            </div>
          ))}

        </div>

        <div className="input-area">

          <input
            type="text"
            placeholder="Type a message..."
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                sendMessage();
              }
            }}
            disabled={loading || !activeThread}
          />

          <button
            className="send-button"
            onClick={sendMessage}
            disabled={loading || !activeThread}
          >
            ↑
          </button>

        </div>

      </main>

    </div>
  );
}

export default App;