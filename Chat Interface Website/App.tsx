import { useState } from "react";
import { ChatSidebar } from "./components/ChatSidebar";
import { ChatArea } from "./components/ChatArea";
import { MessageInput } from "./components/MessageInput";

// Mock data
const mockContacts = [
  {
    id: "1",
    name: "Sarah Johnson",
    lastMessage: "Hey! How's the project going?",
    timestamp: "2m",
    unreadCount: 2,
    avatar: "https://images.unsplash.com/photo-1494790108755-2616b612c7f2?w=150&h=150&fit=crop&crop=face",
    isOnline: true,
  },
  {
    id: "2",
    name: "Mike Chen",
    lastMessage: "Perfect! Let's schedule a meeting",
    timestamp: "15m",
    unreadCount: 0,
    avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    isOnline: true,
  },
  {
    id: "3",
    name: "Emma Davis",
    lastMessage: "Thanks for your help with the design!",
    timestamp: "1h",
    unreadCount: 1,
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
    isOnline: false,
  },
  {
    id: "4",
    name: "Alex Rodriguez",
    lastMessage: "Can you review my code when you have time?",
    timestamp: "3h",
    unreadCount: 0,
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
    isOnline: false,
  },
  {
    id: "5",
    name: "Team Frontend",
    lastMessage: "Daily standup at 10 AM tomorrow",
    timestamp: "1d",
    unreadCount: 3,
    avatar: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=150&h=150&fit=crop&crop=face",
    isOnline: true,
  },
];

const mockMessages = {
  "1": [
    {
      id: "1",
      content: "Hi there! How are you doing today?",
      timestamp: "10:30 AM",
      isOwn: false,
    },
    {
      id: "2",
      content: "Hey Sarah! I'm doing great, thanks for asking. Just working on the new chat interface.",
      timestamp: "10:32 AM",
      isOwn: true,
      status: "read" as const,
    },
    {
      id: "3",
      content: "That sounds exciting! Can't wait to see what you've built.",
      timestamp: "10:33 AM",
      isOwn: false,
    },
    {
      id: "4",
      content: "Hey! How's the project going?",
      timestamp: "10:45 AM",
      isOwn: false,
    },
  ],
  "2": [
    {
      id: "1",
      content: "The mockups look great! Really love the clean design.",
      timestamp: "9:15 AM",
      isOwn: false,
    },
    {
      id: "2",
      content: "Thanks Mike! I'm glad you like them. Should we move forward with this design?",
      timestamp: "9:20 AM",
      isOwn: true,
      status: "read" as const,
    },
    {
      id: "3",
      content: "Perfect! Let's schedule a meeting",
      timestamp: "9:22 AM",
      isOwn: false,
    },
  ],
  "3": [
    {
      id: "1",
      content: "Thanks for your help with the design!",
      timestamp: "Yesterday",
      isOwn: false,
    },
  ],
  "4": [
    {
      id: "1",
      content: "Can you review my code when you have time?",
      timestamp: "Yesterday",
      isOwn: false,
    },
  ],
  "5": [
    {
      id: "1",
      content: "Daily standup at 10 AM tomorrow",
      timestamp: "Yesterday",
      isOwn: false,
    },
  ],
};

export default function App() {
  const [selectedContactId, setSelectedContactId] = useState("1");
  const [messages, setMessages] = useState(mockMessages);

  const selectedContact = mockContacts.find(contact => contact.id === selectedContactId);
  const currentMessages = messages[selectedContactId] || [];

  const handleSendMessage = (content: string) => {
    if (!selectedContactId) return;

    const newMessage = {
      id: Date.now().toString(),
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isOwn: true,
      status: 'sent' as const,
    };

    setMessages(prev => ({
      ...prev,
      [selectedContactId]: [...(prev[selectedContactId] || []), newMessage],
    }));
  };

  return (
    <div className="size-full flex bg-background">
      <ChatSidebar 
        contacts={mockContacts}
        selectedContactId={selectedContactId}
        onSelectContact={setSelectedContactId}
      />
      
      <div className="flex-1 flex flex-col">
        {selectedContact ? (
          <>
            <ChatArea 
              contact={selectedContact}
              messages={currentMessages}
            />
            <MessageInput onSendMessage={handleSendMessage} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h3>Select a conversation</h3>
              <p className="text-muted-foreground">Choose a contact to start chatting</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}