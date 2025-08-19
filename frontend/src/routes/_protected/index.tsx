import { Chat } from '@/components/chat';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_protected/')({
  component: ChatPage,
});

function ChatPage() {
  return <Chat />;
}
