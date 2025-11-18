// Main API export file
export { default as apiClient } from './config';
export * from './types';

// API Modules
export { default as AuthAPI } from './auth';
export { default as UsersAPI } from './users';
export { default as AgentsAPI } from './agents';
export { default as ChatAPI } from './chat';
export { default as FilesAPI } from './files';
export { default as SystemAPI } from './system';

// Utilities
export { APIUtils, APIError, StreamUtils } from './utils';

// For convenience, also export as namespace
export namespace API {
  export const Auth = require('./auth').default;
  export const Users = require('./users').default;
  export const Agents = require('./agents').default;
  export const Chat = require('./chat').default;
  export const Files = require('./files').default;
  export const System = require('./system').default;
}

// Example usage:
// import {
//   AuthAPI,
//   UsersAPI,
//   AgentsAPI,
//   ChatAPI,
//   FilesAPI,
//   SystemAPI,
//   APIUtils,
//   APIError
// } from './api';
//
// // Basic usage
// const loginResponse = await AuthAPI.login({ username, password });
// const agentsList = await AgentsAPI.getAgentCardList({ page: 1, page_size: 20 });
// const createSession = await ChatAPI.createSession({ agent_id: 'test_agent' });
//
// // With error handling
// try {
//   const userInfo = await AuthAPI.getCurrentUser();
//   if (APIUtils.isSuccess(userInfo)) {
//     console.log('User info:', userInfo.data);
//   }
// } catch (error) {
//   console.error('API Error:', APIUtils.getErrorMessage(error));
// }