import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { MoreVertical, Phone, Video, Info } from "lucide-react";
import { ScrollArea } from "./ui/scroll-area";

interface Message {
  id: string;
  content: string;
  timestamp: string;
  isOwn: boolean;
  status?: 'sent' | 'delivered' | 'read';
}

interface Contact {
  id: string;
  name: string;
  avatar: string;
  isOnline: boolean;
}

interface ChatAreaProps {
  contact: Contact;
  messages: Message[];
}

export function ChatArea({ contact, messages }: ChatAreaProps) {
  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Chat Header */}
      <div className="p-4 border-b border-border bg-card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Avatar className="w-10 h-10">
                <AvatarImage src={contact.avatar} alt={contact.name} />
                <AvatarFallback>{contact.name.charAt(0)}</AvatarFallback>
              </Avatar>
              {contact.isOnline && (
                <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 border-2 border-card rounded-full"></div>
              )}
            </div>
            
            <div>
              <h3>{contact.name}</h3>
              <p className="text-sm text-muted-foreground">
                {contact.isOnline ? 'Online' : 'Last seen recently'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon">
              <Phone className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon">
              <Video className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon">
              <Info className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.isOwn ? 'justify-end' : 'justify-start'}`}
            >
              {!message.isOwn && (
                <Avatar className="w-8 h-8">
                  <AvatarImage src={contact.avatar} alt={contact.name} />
                  <AvatarFallback>{contact.name.charAt(0)}</AvatarFallback>
                </Avatar>
              )}
              
              <div className={`max-w-xs lg:max-w-md ${message.isOwn ? 'order-first' : ''}`}>
                <div
                  className={`p-3 rounded-lg ${
                    message.isOwn
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p>{message.content}</p>
                </div>
                
                <div className={`flex items-center gap-1 mt-1 text-xs text-muted-foreground ${
                  message.isOwn ? 'justify-end' : 'justify-start'
                }`}>
                  <span>{message.timestamp}</span>
                  {message.isOwn && message.status && (
                    <Badge variant="outline" className="text-xs">
                      {message.status}
                    </Badge>
                  )}
                </div>
              </div>
              
              {message.isOwn && (
                <Avatar className="w-8 h-8">
                  <AvatarFallback>You</AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}