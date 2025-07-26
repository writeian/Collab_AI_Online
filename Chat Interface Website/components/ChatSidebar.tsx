import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Search, MessageCircle, Settings } from "lucide-react";

interface Contact {
  id: string;
  name: string;
  lastMessage: string;
  timestamp: string;
  unreadCount: number;
  avatar: string;
  isOnline: boolean;
}

interface ChatSidebarProps {
  contacts: Contact[];
  selectedContactId: string;
  onSelectContact: (contactId: string) => void;
}

export function ChatSidebar({ contacts, selectedContactId, onSelectContact }: ChatSidebarProps) {
  return (
    <div className="w-80 bg-card border-r border-border flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="flex items-center gap-2">
            <MessageCircle className="w-5 h-5" />
            Messages
          </h2>
          <Button variant="ghost" size="icon">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder="Search conversations..." 
            className="pl-10"
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {contacts.map((contact) => (
          <button
            key={contact.id}
            onClick={() => onSelectContact(contact.id)}
            className={`w-full p-4 border-b border-border hover:bg-accent/50 transition-colors text-left ${
              selectedContactId === contact.id ? 'bg-accent' : ''
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="relative">
                <Avatar className="w-12 h-12">
                  <AvatarImage src={contact.avatar} alt={contact.name} />
                  <AvatarFallback>{contact.name.charAt(0)}</AvatarFallback>
                </Avatar>
                {contact.isOnline && (
                  <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-card rounded-full"></div>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="truncate">{contact.name}</h3>
                  <span className="text-xs text-muted-foreground">{contact.timestamp}</span>
                </div>
                
                <p className="text-sm text-muted-foreground truncate mt-1">
                  {contact.lastMessage}
                </p>
              </div>
              
              {contact.unreadCount > 0 && (
                <Badge variant="destructive" className="ml-2">
                  {contact.unreadCount}
                </Badge>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}