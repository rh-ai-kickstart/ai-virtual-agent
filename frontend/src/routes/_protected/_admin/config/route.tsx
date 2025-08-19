import {
  Page,
  PageSidebar,
  PageSidebarBody,
  Card,
  CardBody,
  Title
} from '@patternfly/react-core';
import { createFileRoute, Link, Outlet, useLocation } from '@tanstack/react-router';
import React from 'react';
import { Masthead } from '../../../../components/masthead';
import {
  UsersIcon,
  CogIcon,
  DatabaseIcon,
  ServerIcon
} from '@patternfly/react-icons';

export const Route = createFileRoute('/_protected/_admin/config')({
  component: ConfigLayout,
});

function ConfigLayout() {
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);

  const onSidebarToggle = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const masthead = (
    <Masthead
      showSidebarToggle={true}
      isSidebarOpen={isSidebarOpen}
      onSidebarToggle={onSidebarToggle}
    />
  );

  const configItems = [
    {
      path: '/config/agents',
      label: 'Agents',
      icon: CogIcon,
      description: 'Manage AI agents and their configurations'
    },
    {
      path: '/config/knowledge-bases',
      label: 'Knowledge Bases',
      icon: DatabaseIcon,
      description: 'Configure knowledge bases and data sources'
    },
    {
      path: '/config/mcp-servers',
      label: 'MCP Servers',
      icon: ServerIcon,
      description: 'Manage MCP server connections'
    },
    {
      path: '/config/users',
      label: 'Users',
      icon: UsersIcon,
      description: 'User management and permissions'
    }
  ];

  const sidebar = (
    <PageSidebar isSidebarOpen={isSidebarOpen} id="config-sidebar">
      <PageSidebarBody>
        <div style={{ padding: '1rem' }}>
          <Card isCompact>
            <CardBody>
              <Title headingLevel="h4" size="md" style={{ marginBottom: '1rem' }}>
                Configuration
              </Title>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {configItems.map((item) => {
                  const isActive = location.pathname === item.path;
                  const IconComponent = item.icon;

                  return (
                    <Card
                      key={item.path}
                      isClickable
                      isSelected={isActive}
                      style={{
                        width: '100%',
                        border: isActive
                          ? '2px solid var(--pf-v5-global--primary-color--100)'
                          : '1px solid var(--pf-v5-global--BorderColor--100)',
                        backgroundColor: isActive
                          ? 'var(--pf-v5-global--primary-color--200)'
                          : 'var(--pf-v5-global--BackgroundColor--100)',
                        boxShadow: isActive
                          ? '0 2px 4px rgba(0, 0, 0, 0.1)'
                          : 'none'
                      }}
                    >
                      <CardBody style={{ padding: '0.75rem' }}>
                        <Link
                          to={item.path}
                          search={item.path === '/config/users' ? { userId: undefined } : undefined}
                          style={{
                            textDecoration: 'none',
                            color: 'inherit',
                            display: 'block'
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <IconComponent
                              style={{
                                fontSize: '1.25rem',
                                color: isActive
                                  ? 'var(--pf-v5-global--primary-color--100)'
                                  : 'var(--pf-v5-global--Color--100)'
                              }}
                            />
                            <div style={{ flex: 1, minWidth: 0 }}>
                              <div style={{
                                fontWeight: isActive ? 600 : 500,
                                fontSize: '0.875rem',
                                marginBottom: '0.25rem',
                                color: isActive
                                  ? 'var(--pf-v5-global--primary-color--100)'
                                  : 'var(--pf-v5-global--Color--100)',
                                lineHeight: '1.3'
                              }}>
                                {item.label}
                              </div>
                              <div style={{
                                fontSize: '0.75rem',
                                color: isActive
                                  ? 'var(--pf-v5-global--primary-color--200)'
                                  : 'var(--pf-v5-global--Color--200)',
                                lineHeight: '1.2',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}>
                                {item.description}
                              </div>
                            </div>
                          </div>
                        </Link>
                      </CardBody>
                    </Card>
                  );
                })}
              </div>
            </CardBody>
          </Card>
        </div>
      </PageSidebarBody>
    </PageSidebar>
  );

  return (
    <Page sidebar={sidebar} mainContainerId={'config-page-container'} masthead={masthead}>
      <Outlet />
    </Page>
  );
}
