import React, { createContext, useContext, ReactNode, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchCurrentUser, User } from '@/services/users';

interface UserContextType {
  currentUser: User | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<any>;
  loginHtml: string | null;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProps {
  children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const [loginHtml, setLoginHtml] = React.useState<string | null>(null);

  const {
    data: currentUser,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      try {
        return await fetchCurrentUser();
      } catch (err: any) {
        if (err.message === 'OAUTH_LOGIN_REQUIRED' && err.loginHtml) {
          setLoginHtml(err.loginHtml);
        }
        throw err;
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on authentication errors or login required
      if (
        error.message === 'User not authenticated' ||
        error.message === 'User not found' ||
        error.message === 'OAUTH_LOGIN_REQUIRED'
      ) {
        return false;
      }
      return failureCount < 3;
    },
  });

  // Clear login HTML when user successfully authenticates
  useEffect(() => {
    if (currentUser && loginHtml) {
      setLoginHtml(null);
    }
  }, [currentUser, loginHtml]);

  const value: UserContextType = {
    currentUser: currentUser || null,
    isLoading,
    error: error?.message === 'OAUTH_LOGIN_REQUIRED' ? null : (error?.message || null),
    refetch,
    loginHtml,
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};

/**
 * Custom hook to access the current user
 *
 * Uses React Query to fetch the current authenticated user from the /profile endpoint.
 * The backend determines the current user based on authentication headers.
 *
 * TODO: Handle authentication flow properly:
 * 1. Redirect to login page when user is not authenticated (401/403 errors), this
 *    might be default behavior when using oauth-proxy.
 * 2. Implement proper login/logout flows, need to determine oauth-proxy logout flow
 * 3. Handle token refresh and session management this may not be needed as oauth-proxy
 *    will handle this in our current implementation.
 *
 * @returns {UserContextType} Object containing:
 *   - currentUser: The current authenticated user object or null
 *   - isLoading: Loading state from React Query
 *   - error: Error message if any (including authentication errors)
 *   - refetch: Function to manually refetch user data
 */
export const useCurrentUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useCurrentUser must be used within a UserProvider');
  }
  return context;
};
