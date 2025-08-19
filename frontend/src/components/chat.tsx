import React, { useEffect, useState, useCallback } from 'react';
import {
  Chatbot,
  ChatbotContent,
  ChatbotDisplayMode,
  ChatbotFooter,
  ChatbotFootnote,
  FileDetailsLabel,
  Message,
  MessageBar,
  MessageBox,
  MessageProps,
} from '@patternfly/chatbot';
import {
  Modal,
  ModalVariant,
  Button,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Panel,
  PanelMain,
  PanelMainBody,
  Page,
  PageSidebar,
  PageSidebarBody,
  PageSection,
  Select,
  SelectOption,
  MenuToggle,
  MenuToggleElement,
  Title,
  Card,
  CardBody,
  Split,
  SplitItem,
} from '@patternfly/react-core';
import { Agent } from '@/types/agent';
import { fetchUserAgents } from '@/services/agents';
import { useChat } from '@/hooks/useChat';
import { useCurrentUser } from '@/contexts/UserContext';
import {
  fetchChatSessions,
  createChatSession,
  deleteChatSession,
  ChatSessionSummary,
} from '@/services/chat-sessions';
import { useMutation } from '@tanstack/react-query';
import botAvatar from '../assets/img/bot-avatar.svg';
import userAvatar from '../assets/img/user-avatar.svg';
import { ATTACHMENTS_API_ENDPOINT } from '@/config/api';
import { SimpleContentItem } from '@/types/chat';
import { Masthead } from './masthead';
import { TrashIcon, PlusIcon } from '@patternfly/react-icons';

const footnoteProps = {
  label: 'ChatBot uses AI. Check for mistakes.',
  popover: {
    title: 'Verify information',
    description: `While ChatBot strives for accuracy, AI is experimental and can make mistakes. We cannot guarantee that all information provided by ChatBot is up to date or without error. You should always verify responses using reliable sources, especially for crucial information and decision making.`,
    bannerImage: {
      src: 'https://cdn.dribbble.com/userupload/10651749/file/original-8a07b8e39d9e8bf002358c66fce1223e.gif',
      alt: 'Example image for footnote popover',
    },
    cta: {
      label: 'Dismiss',
      onClick: () => {
        alert('Do something!');
      },
    },
    link: {
      label: 'View AI policy',
      url: 'https://www.redhat.com/',
    },
  },
};

export function Chat() {
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [isAgentSelectOpen, setIsAgentSelectOpen] = useState<boolean>(false);
  const [announcement, setAnnouncement] = useState<string>('');
  const [chatSessions, setChatSessions] = useState<ChatSessionSummary[]>([]);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState<boolean>(false);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);
  const scrollToBottomRef = React.useRef<HTMLDivElement>(null);

  // Get current user context
  const {
    currentUser,
    isLoading: isUserLoading,
    error: userError,
    refetch: refetchUser,
  } = useCurrentUser();

  // Get the agent type for the selected agent
  const selectedAgentObj = availableAgents.find((agent) => agent.id === selectedAgent);
  const agentType = selectedAgentObj?.agent_type === 'ReAct' ? 'ReAct' : 'Regular';

  // Use our custom hook for chat functionality - only when we have a valid agent
  const {
    messages: chatMessages,
    input,
    handleInputChange,
    append,
    isLoading,
    loadSession,
    sessionId,
    attachedFiles,
    handleAttach,
    clearAttachedFiles,
    setAttachedFiles,
  } = useChat(selectedAgent || 'default', agentType, {
    onError: (error: Error) => {
      console.error('Chat error:', error);
      setAnnouncement(`Error: ${error.message}`);
    },
    onFinish: () => {
      setAnnouncement(`Message from assistant complete`);
      scrollToBottom();
    },
  });

  // Auto-scroll function
  const scrollToBottom = useCallback(() => {
    if (scrollToBottomRef.current) {
      scrollToBottomRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'end',
        inline: 'nearest'
      });
    }
  }, []);

    // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, scrollToBottom]);

  // Auto-scroll when session changes (session selection)
  useEffect(() => {
    if (sessionId) {
      // Small delay to ensure messages are loaded before scrolling
      const timer = setTimeout(() => {
        scrollToBottom();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [sessionId, scrollToBottom]);

  // Auto-scroll during streaming (when loading)
  useEffect(() => {
    if (isLoading) {
      // Scroll immediately when starting to load
      scrollToBottom();

      // Set up interval to keep scrolling during message generation
      const scrollInterval = setInterval(() => {
        scrollToBottom();
      }, 100); // Scroll every 100ms while loading

      return () => clearInterval(scrollInterval);
    }
  }, [isLoading, scrollToBottom]);
  const contentToText = (content: SimpleContentItem): string => {
    if (content.type === 'text') {
      return content.text || '';
    }

    // The backend does not set/store the sourceType, so we need to check for the url property
    if (content.type === 'image' && 'url' in content.image) {
      return `![Image](${content.image.url.uri})`;
    }

    return '';
  };

  const multipleContentToText = React.useCallback((content: SimpleContentItem[]): string => {
    return content.map((m) => contentToText(m)).join('\n');
  }, []);

  // Convert our chat messages to PatternFly format
  const messages = React.useMemo(
    () =>
      chatMessages.map(
        (msg): MessageProps => ({
          id: msg.id,
          role: msg.role === 'user' ? 'user' : 'bot',
          content: multipleContentToText(msg.content),
          name: msg.role === 'user' ? 'You' : 'Assistant',
          timestamp: msg.timestamp.toLocaleString(),
          avatar: msg.role === 'user' ? userAvatar : botAvatar,
          avatarProps: { isBordered: true },
          isLoading:
            msg.role === 'assistant' &&
            isLoading &&
            msg.id === chatMessages[chatMessages.length - 1]?.id,
        })
      ),
    [chatMessages, isLoading, multipleContentToText]
  );

  const displayMode = ChatbotDisplayMode.embedded;

  const onSidebarToggle = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const onSelectAgent = (_event: React.MouseEvent<Element, MouseEvent> | undefined, value: string | number | undefined) => {
    if (value) {
      const agentId = value.toString();
      console.log('Agent selected:', agentId);
      setSelectedAgent(agentId);
      setIsAgentSelectOpen(false);
    }
  };

  const onSelectSession = (sessionId: string) => {
    void (async () => {
      try {
        await loadSession(sessionId);
      } catch (error) {
        console.error('Error loading session:', error);
        setAnnouncement('Failed to load chat session');
      }
    })();
  };

  const onNewSession = () => {
    if (!selectedAgent) return;

    void (async () => {
      try {
        // Generate unique session name with timestamp
        const timestamp = new Date()
          .toISOString()
          .slice(0, 19)
          .replace(/[-:]/g, '')
          .replace('T', '-');
        const randomSuffix = Math.random().toString(36).substring(2, 6);
        const uniqueSessionName = `Chat-${timestamp}-${randomSuffix}`;

        // Create a new session for the current agent with unique name
        const newSession = await createChatSession(selectedAgent, uniqueSessionName);

        // Load the new session
        await loadSession(newSession.id);

        // Refresh sessions list to include the new session
        await fetchSessionsData(selectedAgent);
      } catch (error) {
        console.error('Error creating new session:', error);
        setAnnouncement('Failed to create new chat session');
      }
    })();
  };

  const handleDeleteSession = useCallback((sessionId: string) => {
    setSessionToDelete(sessionId);
    setIsDeleteModalOpen(true);
  }, []);

  const deleteSessionMutation = useMutation<void, Error, string>({
    mutationFn: (sessionId: string) => {
      if (!selectedAgent) throw new Error('No agent selected');
      return deleteChatSession(sessionId, selectedAgent);
    },
    onSuccess: async () => {
      if (!selectedAgent) return;

      setAnnouncement('Session deleted successfully');
      // Simply refresh sessions data - fetchSessionsData handles everything:
      // - If sessions remain: updates UI and loads first session if current was deleted
      // - If no sessions remain: creates new session, loads it, and updates UI
      await fetchSessionsData(selectedAgent);
    },
    onError: (error) => {
      console.error('Error deleting session:', error);
      setAnnouncement(`Failed to delete session: ${error.message}`);
    },
    onSettled: () => {
      // Always clean up modal state when mutation completes
      setIsDeleteModalOpen(false);
      setSessionToDelete(null);
    },
  });

  const confirmDeleteSession = () => {
    if (!sessionToDelete) return;

    // Trigger the mutation
    deleteSessionMutation.mutate(sessionToDelete);
  };

  const cancelDeleteSession = () => {
    setIsDeleteModalOpen(false);
    setSessionToDelete(null);
  };



  const fetchSessionsData = useCallback(
    async (agentId?: string) => {
      try {
        console.log('fetchSessionsData called with agentId:', agentId);
        const sessions = await fetchChatSessions(agentId);
        console.log('Fetched sessions:', sessions);
        setChatSessions(sessions);

        // Auto-select first session if no session is currently selected and sessions exist
        // OR if the current sessionId doesn't exist in the fetched sessions (i.e., from different agent)
        console.log('Current sessionId:', sessionId, 'sessions.length:', sessions.length);
        const currentSessionExists =
          sessionId && sessions.some((session) => session.id === sessionId);
        console.log('Current session exists in fetched sessions:', currentSessionExists);

        if ((!sessionId || !currentSessionExists) && sessions.length > 0) {
          const firstSession = sessions[0]; // Sessions should be ordered by updated_at desc (most recent first)
          console.log('Auto-selecting first session:', firstSession.id);
          await loadSession(firstSession.id);
        } else if (sessions.length === 0 && agentId) {
          // Create a new session if agent has no sessions
          try {
            console.log('No sessions found, creating new session for agent:', agentId);
            // Generate unique session name with timestamp
            const timestamp = new Date()
              .toISOString()
              .slice(0, 19)
              .replace(/[-:]/g, '')
              .replace('T', '-');
            const randomSuffix = Math.random().toString(36).substring(2, 6);
            const uniqueSessionName = `Chat-${timestamp}-${randomSuffix}`;

            const newSession = await createChatSession(agentId, uniqueSessionName);
            await loadSession(newSession.id);

            // Update UI state with the new session
            const newSessionSummary: ChatSessionSummary = {
              id: newSession.id,
              title: newSession.title,
              agent_name: newSession.agent_name,
              updated_at: newSession.updated_at,
              created_at: newSession.created_at,
            };
            setChatSessions([newSessionSummary]);
          } catch (error) {
            console.error('Error creating initial session:', error);
            setAnnouncement('Failed to create initial session');
          }
        }
      } catch (error) {
        console.error('Error fetching chat sessions:', error);
        setAnnouncement(
          `Failed to fetch sessions: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    },
    [sessionId, loadSession, setAnnouncement]
  );

  // Fetch available agents on mount - only when user is loaded
  useEffect(() => {
    const fetchAgentsData = async () => {
      // TODO: This currently fetches agents for the first user in the database.
      // Once proper authentication is implemented, this should fetch agents for the authenticated user.
      if (!currentUser) return;

      try {
        console.log('Fetching agents for user:', currentUser.id);
        const agents = await fetchUserAgents(currentUser.id);
        setAvailableAgents(agents);
        if (agents.length > 0) {
          const firstAgent = agents[0].id;
          console.log('Setting first agent:', firstAgent);
          setSelectedAgent(firstAgent);
          // Don't fetch sessions here - let the selectedAgent useEffect handle it
        } else {
          console.log('No agents found for user:', currentUser.id);
          setAnnouncement('No agents assigned to this user');
        }
      } catch (err) {
        console.error('Error fetching user agents:', err);
        setAnnouncement('Failed to load user agents');
      }
    };

    void fetchAgentsData();
  }, [currentUser]);

  // Handle selectedAgent changes - fetch sessions for the new agent
  useEffect(() => {
    if (selectedAgent) {
      console.log('selectedAgent changed to:', selectedAgent, 'fetching sessions...');
      void fetchSessionsData(selectedAgent);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAgent]); // fetchSessionsData intentionally excluded to prevent infinite loop

  // Handle message sending
  const handleSendMessage = async (message: string | number) => {
    console.log('handleSendMessage called with:', message, 'selectedAgent:', selectedAgent);
    console.log('Current session ID:', sessionId);
    if (typeof message === 'string' && message.trim() && selectedAgent) {
      console.log('Sending message via append:', message, 'using session:', sessionId);
      const contents: SimpleContentItem[] = [];
      contents.push({ type: 'text', text: message });
      for (const file of attachedFiles) {
        const attachmentUrl = await handleUploadAttachment(file, sessionId);
        contents.push({ type: 'image', image: { sourceType: 'url', url: { uri: attachmentUrl } } });
      }
      // Add the message to the chat
      append({
        role: 'user',
        content: contents,
      });
      clearAttachedFiles();
    } else {
      console.log('Message not sent - conditions not met:', {
        messageType: typeof message,
        messageLength: typeof message === 'string' ? message.trim().length : 0,
        selectedAgent: selectedAgent,
      });
    }
  };

  const handleUploadAttachment = async (file: File, sessionId: string | null): Promise<string> => {
    if (!sessionId) {
      throw new Error('Session ID is required');
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    const response = await fetch(ATTACHMENTS_API_ENDPOINT, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload attachment');
    }

    const data = (await response.json()) as { filename: string };
    console.log('Attachment uploaded successfully:', data);

    // NOTE: The frontend is not aware of its own base URL,
    // so the URL returned here is only the path portion, e.g. /api/attachments/...
    return `${ATTACHMENTS_API_ENDPOINT}${sessionId}/${data.filename}`;
  };

  // Handle loading and error states for user context
  if (isUserLoading) {
    return (
      <div>
        <p>Loading user information...</p>
      </div>
    );
  }

  if (userError || !currentUser) {
    return (
      <div>
        <p>Error loading user: {userError || 'User not found'}</p>
        <p>Please check your authentication or try logging in again.</p>
        <Button variant="primary" onClick={() => void refetchUser()}>
          Retry
        </Button>
      </div>
    );
  }

  const masthead = (
    <Masthead
      showSidebarToggle={true}
      isSidebarOpen={isSidebarOpen}
      onSidebarToggle={onSidebarToggle}
    />
  );

  const sidebar = (
    <PageSidebar isSidebarOpen={isSidebarOpen} id="chat-sidebar">
      <PageSidebarBody>
        <div style={{ padding: '1rem' }}>
          {/* Agent Selection Section */}
          <Card isCompact>
            <CardBody>
              <Title headingLevel="h4" size="md" style={{ marginBottom: '1rem' }}>
                Select Agent
              </Title>
              <Select
                  onSelect={onSelectAgent}
                selected={selectedAgent}
                onOpenChange={(isOpen: boolean) => setIsAgentSelectOpen(isOpen)}
                isOpen={isAgentSelectOpen}
                toggle={(toggleRef: React.Ref<MenuToggleElement>) => (
                  <MenuToggle
                    ref={toggleRef}
                    onClick={() => setIsAgentSelectOpen(!isAgentSelectOpen)}
                    isExpanded={isAgentSelectOpen}
                    style={{ width: '100%' }}
                  >
                    {availableAgents.find((agent) => agent.id === selectedAgent)?.name || 'Select Agent'}
                  </MenuToggle>
                )}
              >
                    {availableAgents.map((agent) => (
                  <SelectOption key={agent.id} value={agent.id}>
                        {agent.name}
                  </SelectOption>
                ))}
              </Select>
            </CardBody>
          </Card>

          {/* Chat Sessions Section */}
          <Card isCompact style={{ marginTop: '1rem' }}>
            <CardBody>
              <Split hasGutter>
                <SplitItem isFilled>
                  <Title headingLevel="h4" size="md">
                    Chat Sessions
                  </Title>
                </SplitItem>
                <SplitItem>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={onNewSession}
                    isDisabled={!selectedAgent}
                    icon={<PlusIcon />}
                  >
                    New
                  </Button>
                </SplitItem>
              </Split>

              <div style={{ marginTop: '1rem' }}>
                {chatSessions.length === 0 && selectedAgent && (
                  <div style={{ textAlign: 'center', color: 'var(--pf-v5-global--Color--200)', padding: '1rem' }}>
                    No sessions yet. Create your first session!
                  </div>
                )}

                {chatSessions.length === 0 && !selectedAgent && (
                  <div style={{ textAlign: 'center', color: 'var(--pf-v5-global--Color--200)', padding: '1rem' }}>
                    Select an agent to view sessions
                  </div>
                )}

                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {chatSessions.map((session) => (
                    <Card
                      key={session.id}
                      isClickable
                      isSelected={session.id === sessionId}
                      onClick={() => onSelectSession(session.id)}
                      style={{
                        width: '100%',
                        border: session.id === sessionId
                          ? '2px solid var(--pf-v5-global--primary-color--100)'
                          : '1px solid var(--pf-v5-global--BorderColor--100)',
                        backgroundColor: session.id === sessionId
                          ? 'var(--pf-v5-global--primary-color--200)'
                          : 'var(--pf-v5-global--BackgroundColor--100)',
                        boxShadow: session.id === sessionId
                          ? '0 2px 4px rgba(0, 0, 0, 0.1)'
                          : 'none'
                      }}
                    >
                      <CardBody style={{ padding: '0.75rem' }}>
                        <Split hasGutter style={{ minWidth: 0 }}>
                          <SplitItem isFilled style={{ minWidth: 0, overflow: 'hidden' }}>
                            <div style={{ minWidth: 0 }}>
                              <div style={{
                                fontWeight: session.id === sessionId ? 600 : 500,
                                fontSize: '0.875rem',
                                marginBottom: '0.25rem',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                minWidth: 0,
                                color: session.id === sessionId
                                  ? 'var(--pf-v5-global--primary-color--100)'
                                  : 'var(--pf-v5-global--Color--100)',
                                lineHeight: '1.3'
                              }}
                              title={session.title}
                              >
                                {session.title}
                              </div>
                              <div style={{
                                fontSize: '0.75rem',
                                color: session.id === sessionId
                                  ? 'var(--pf-v5-global--primary-color--200)'
                                  : 'var(--pf-v5-global--Color--200)',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                minWidth: 0,
                                lineHeight: '1.2'
                              }}
                              title={new Date(session.updated_at).toLocaleDateString()}
                              >
                                {new Date(session.updated_at).toLocaleDateString()}
                              </div>
                            </div>
                          </SplitItem>
                          <SplitItem style={{ flexShrink: 0 }}>
                            <Button
                              variant="plain"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteSession(session.id);
                              }}
                              icon={<TrashIcon />}
                              aria-label="Delete session"
                              style={{
                                color: session.id === sessionId
                                  ? 'var(--pf-v5-global--primary-color--100)'
                                  : 'var(--pf-v5-global--danger-color--100)'
                              }}
                            />
                          </SplitItem>
                        </Split>
                      </CardBody>
                    </Card>
                  ))}
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      </PageSidebarBody>
    </PageSidebar>
  );

    return (
    <>
      <style>{`
        #chat-page-container {
          padding: 0 !important;
          margin: 0 !important;
          height: calc(100vh - 64px) !important;
          overflow: hidden !important;
        }
        #chat-page-container .pf-v5-c-page__main-section {
          padding: 0 !important;
          margin: 0 !important;
        }
      `}</style>
      <Page
        sidebar={sidebar}
        mainContainerId={'chat-page-container'}
        masthead={masthead}
      >
        <PageSection
          hasBodyWrapper={false}
          style={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            minHeight: 0,
            padding: 0,
            margin: 0
          }}
        >
        <Chatbot displayMode={displayMode}>
            <ChatbotContent style={{
              flex: 1,
              minHeight: 0,
              overflow: 'hidden'
            }}>
              <MessageBox announcement={announcement}>
                {messages.map((message) => (
                        <Message key={message.id} {...message} />
                ))}
                {/* Scroll anchor - always at the bottom */}
                <div
                  ref={scrollToBottomRef}
                  style={{
                    height: '1px',
                    marginTop: '0.5rem',
                    visibility: 'hidden'
                  }}
                  aria-hidden="true"
                />
              </MessageBox>
            </ChatbotContent>
                        <ChatbotFooter style={{
              flexShrink: 1,
              minHeight: 0,
              overflow: 'hidden'
            }}>
              <Panel variant="secondary">
                <PanelMain>
                  <PanelMainBody style={{
                    padding: '0.25rem 0.5rem',
                    minHeight: 0
                  }}>
                    {attachedFiles.length > 0 && (
                    <div
                      style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                          paddingBottom: '0.25rem',
                          gap: '0.25rem'
                      }}
                    >
                      {attachedFiles.map((file, index) => (
                          <FileDetailsLabel
                            key={file.name}
                            fileName={file.name}
                            onClose={() => {
                              setAttachedFiles(attachedFiles.filter((_, i) => i !== index));
                            }}
                          />
                      ))}
                    </div>
                    )}
                    <MessageBar
                      onSendMessage={handleSendMessage as (message: string | number) => void}
                      hasMicrophoneButton
                      isSendButtonDisabled={isLoading || !selectedAgent}
                      value={input}
                      onChange={handleInputChange}
                      handleAttach={handleAttach}
                    />
                  </PanelMainBody>
                </PanelMain>
              </Panel>
              <div style={{
                padding: '0.125rem 0.25rem',
                textAlign: 'center',
                overflow: 'hidden',
                fontSize: '0.75rem',
                lineHeight: '1.2'
              }}>
              <ChatbotFootnote {...footnoteProps} />
              </div>
            </ChatbotFooter>
        </Chatbot>
      </PageSection>
      <Modal
        variant={ModalVariant.small}
        title="Confirm Delete"
        isOpen={isDeleteModalOpen}
        onClose={cancelDeleteSession}
      >
        <ModalHeader title="Delete Session" labelId="delete-session-modal-title" />
        <ModalBody id="delete-session-modal-desc">
          Are you sure you want to delete this session?
        </ModalBody>
        <ModalFooter>
          <Button variant="link" onClick={cancelDeleteSession}>
            Cancel
          </Button>
          <Button
            variant="danger"
            isLoading={deleteSessionMutation.isPending}
            onClick={confirmDeleteSession}
          >
            Delete
          </Button>
        </ModalFooter>
      </Modal>
    </Page>
  </>);
}
