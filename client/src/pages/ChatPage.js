import React, { useState, useEffect, useRef } from 'react';
import { support } from '../api';

function ChatPage() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        loadHistory();
    }, []);

    useEffect(() => {
        // Auto-scroll to bottom on new messages
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    async function loadHistory() {
        try {
            const history = await support.chatHistory(20);
            const formattedMessages = [];
            history.forEach(msg => {
                formattedMessages.push({ type: 'user', text: msg.user_message });
                formattedMessages.push({ type: 'ai', text: msg.ai_response });
            });
            setMessages(formattedMessages);
        } catch (err) {
            // First time user - show welcome
            setMessages([{
                type: 'ai',
                text: "Hey! I'm your PocketBuddy AI assistant. I can help with budgeting, food ideas, stress management, study tips, or just chat. What's on your mind?"
            }]);
        }
    }

    async function sendMessage(text) {
        if (!text.trim()) return;

        const userMessage = text.trim();
        setInput('');
        setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
        setLoading(true);
        setSuggestions([]);

        try {
            const result = await support.chat(userMessage);
            setMessages(prev => [...prev, { type: 'ai', text: result.response }]);
            setSuggestions(result.suggestions || []);
        } catch (err) {
            setMessages(prev => [...prev, { type: 'ai', text: 'Sorry, something went wrong. Please try again.' }]);
        } finally {
            setLoading(false);
        }
    }

    function handleSubmit(e) {
        e.preventDefault();
        sendMessage(input);
    }

    return (
        <div className="chat-container">
            <h1 style={{ marginBottom: '16px' }}>💬 AI Support Chat</h1>

            {/* Messages */}
            <div className="chat-messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`chat-message ${msg.type}`}>
                        {msg.text}
                    </div>
                ))}
                {loading && (
                    <div className="chat-message ai" style={{ opacity: 0.6 }}>
                        Thinking...
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestions */}
            {suggestions.length > 0 && (
                <div className="chat-suggestions">
                    {suggestions.map((s, i) => (
                        <button key={i} onClick={() => sendMessage(s)}>{s}</button>
                    ))}
                </div>
            )}

            {/* Input */}
            <form className="chat-input-container" onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask me anything about your wellness, budget, or habits..."
                    disabled={loading}
                    aria-label="Chat message input"
                />
                <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
                    Send
                </button>
            </form>
        </div>
    );
}

export default ChatPage;
