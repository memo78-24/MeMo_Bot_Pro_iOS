import { init, retrieveLaunchParams, miniApp, themeParams, viewport, backButton, initData } from '@telegram-apps/sdk';

let telegramApp = null;
let theme = null;
let user = null;

export const initTelegram = () => {
  try {
    // Initialize SDK
    init();
    
    // Get launch parameters
    const launchParams = retrieveLaunchParams();
    
    // Initialize components
    miniApp.mount();
    themeParams.mount();
    viewport.mount();
    backButton.mount();
    
    // Expand viewport to full height
    if (viewport.expand.isAvailable()) {
      viewport.expand();
    }
    
    // Get user info from initData
    if (initData.restore()) {
      user = initData.user();
    }
    
    // Set theme colors
    theme = themeParams.getState();
    
    telegramApp = {
      miniApp,
      themeParams,
      viewport,
      backButton,
      user,
      launchParams,
    };
    
    console.log('✅ Telegram SDK initialized', { user, theme });
    return telegramApp;
  } catch (error) {
    console.error('❌ Failed to initialize Telegram SDK:', error);
    // Return mock data for local development
    return {
      miniApp: {
        setHeaderColor: () => {},
        close: () => {},
        ready: () => {},
      },
      themeParams: {
        backgroundColor: () => '#ffffff',
        textColor: () => '#000000',
      },
      viewport: {
        height: 600,
        width: 400,
      },
      backButton: {
        show: () => {},
        hide: () => {},
        onClick: () => {},
      },
      user: {
        id: 123456789,
        firstName: 'Test',
        lastName: 'User',
        username: 'testuser',
      },
      launchParams: {},
    };
  }
};

export const getTelegramApp = () => telegramApp || initTelegram();

export const getTelegramUser = () => {
  const app = getTelegramApp();
  return app.user;
};

export const getTelegramTheme = () => {
  const app = getTelegramApp();
  return app.themeParams;
};

export const showBackButton = (onClick) => {
  const app = getTelegramApp();
  if (app.backButton && app.backButton.show) {
    app.backButton.show();
    if (onClick) {
      app.backButton.onClick(onClick);
    }
  }
};

export const hideBackButton = () => {
  const app = getTelegramApp();
  if (app.backButton && app.backButton.hide) {
    app.backButton.hide();
  }
};

export const closeMiniApp = () => {
  const app = getTelegramApp();
  if (app.miniApp && app.miniApp.close) {
    app.miniApp.close();
  }
};

export const hapticFeedback = (type = 'impact', style = 'light') => {
  try {
    if (window.Telegram && window.Telegram.WebApp) {
      if (type === 'impact') {
        window.Telegram.WebApp.HapticFeedback.impactOccurred(style);
      } else if (type === 'notification') {
        window.Telegram.WebApp.HapticFeedback.notificationOccurred(style);
      }
    }
  } catch (error) {
    console.log('Haptic feedback not available');
  }
};
