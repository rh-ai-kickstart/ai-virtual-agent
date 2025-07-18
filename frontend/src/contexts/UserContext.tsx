import React, { createContext, useContext, ReactNode, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchUsers, User } from '@/services/users';

interface UserContextType {
  currentUser: User | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProps {
  children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const {
    data: users,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });

  const currentUser = useMemo(() => {
    // TODO: Replace this with actual authentication logic
    // For now, we default to the first user in the database
    if (users && users.length > 0) {
      console.log('Defaulting to first user:', users[0]);
      return users[0];
    }
    return null;
  }, [users]);

  const value: UserContextType = {
    currentUser,
    isLoading,
    error: error?.message || (users?.length === 0 ? 'No users found in database' : null),
    refetch,
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
 * Uses React Query for efficient data fetching with caching and invalidation.
 *
 * TODO: This currently defaults to the first user in the database.
 * Replace with proper authentication logic that:
 * 1. Checks for stored auth tokens/session
 * 2. Validates user session with backend
 * 3. Handles login/logout flows
 * 4. Redirects to login if not authenticated
 *
 * @returns {UserContextType} Object containing:
 *   - currentUser: The current user object or null
 *   - isLoading: Loading state from React Query
 *   - error: Error message if any
 *   - refetch: Function to manually refetch user data
 */
export const useCurrentUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useCurrentUser must be used within a UserProvider');
  }
  return context;
};
