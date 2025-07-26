import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Send, Paperclip, Smile } from "lucide-react";

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export function MessageInput({ onSendMessage, disabled = false }: MessageInputProps) {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="p-4 border-t border-border bg-card">
      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <div className="flex items-center gap-2">
          <Button type="button" variant="ghost" size="icon">
            <Paperclip className="w-4 h-4" />
          </Button>
          <Button type="button" variant="ghost" size="icon">
            <Smile className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="flex-1">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            disabled={disabled}
            className="resize-none"
          />
        </div>
        
        <Button 
          type="submit" 
          size="icon"
          disabled={!message.trim() || disabled}
        >
          <Send className="w-4 h-4" />
        </Button>
      </form>
    </div>
  );
}