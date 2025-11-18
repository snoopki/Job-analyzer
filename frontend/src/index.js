import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import '@mantine/charts/styles.css';
import App from './App';

import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <MantineProvider
        withGlobalStyles
        withNormalizeCSS
        defaultColorScheme="dark"
        theme={{ dir: 'rtl' }} 
      >
        <Notifications position="top-right" />
        <App /> 
      </MantineProvider>
    </BrowserRouter>
  </React.StrictMode>
);