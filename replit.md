# MeMo Bot Pro

## Overview
MeMo Bot Pro is a Binance Advisory & Live Trading assistant with Telegram integration. This application provides real-time cryptocurrency price tracking, trading signal generation, a web dashboard, and a Telegram bot for remote monitoring and control. Its main purpose is to offer real-time crypto advisory and trading signals, aiming to be a market-leading tool for cryptocurrency traders, particularly with its unique Arabic language support.

## User Preferences
No specific user preferences recorded yet.

## System Architecture

### Core Functionality
- **Dual Workflow**: The application runs both a Web Dashboard and an Enhanced Telegram Bot simultaneously.
- **Real-time Monitoring**: Features ultra-sensitive price monitoring with 60 checks per minute, alerting on any price change (0% threshold). Includes 5-minute cooldown per symbol to prevent spam.
- **Trading Signals**: Generates BUY/SELL/HOLD trading signals with each alert and in 2-hour summary reports.
- **Reporting**: Provides 2-hour summary reports comparing "WAS vs NOW" prices for the top 10 trending cryptocurrencies.
- **User Engagement**: Implements smart re-engagement for inactive users and an admin broadcast system.

### UI/UX Decisions
- **Telegram Bot**: Features interactive button menus, persistent main menu, and dual language support (English/Arabic) with Arabic-Indic numerals. Alerts include currency logos (₿ Ξ 🔶 ◎ ✕ ₳ Ð ● ⬡ 🐕) and clickable links to Binance markets.
- **Telegram Mini App UI**: Opera GX gaming-inspired dark theme with:
  - Deep black backgrounds (#0d0d10) for main surface, dark card backgrounds (#1a1a1e, #25252b)
  - Hot pink accents (#FF0050) for primary actions, gradients, and highlights
  - Brighter pink variant (#FF3377) for text elements ensuring WCAG AA accessibility
  - Neon glow effects on buttons and active states for gaming aesthetic
  - All contrast ratios meet or exceed 4.5:1 for accessibility compliance
  - Consistent token-based design system via Tailwind CSS
- **Web Dashboard**: A Flask-based web interface showing live market data and signals, designed for real-time updates every 30 seconds.
- **Monitoring Dashboard**: Includes big alert banners, looping sound alerts, and an acknowledgment system for critical issues.

### Technical Implementations
- **Binance Client**: Abstracts Binance API interactions, supporting mock mode for testing and focusing on the top 10 trending currencies.
- **Signal Generator**: Analyzes price data to generate trading recommendations.
- **Scalping Signals**: Advanced signal generator with entry/exit prices, stop-loss, and take-profit calculations for $50 scalping trades targeting $100 daily profit.
- **Database Layer**: PostgreSQL database with adapter pattern for graceful fallback to Excel-based UserStorage. Includes users, trade_history, and trading_config tables. Automatic fallback when DATABASE_URL unavailable.
- **Trading Commands**: Real-time Binance wallet integration with /balance, /trade, /history commands. Manual buy/sell execution with risk management. Auto-trading feature disabled (coming soon).
- **User Storage**: Dual-layer system - PostgreSQL (production) with Excel (`openpyxl`) fallback for development/testing.
- **Translations**: Dedicated module for English and Arabic language support, including all trading features.
- **Configuration**: Environment-based configuration with support for `MOCK_MODE`.
- **Webhook Integration**: Telegram bot runs via webhooks inside Flask web app (no separate polling process), enabling Autoscale deployment with secret token security.
- **Deployment**: Configured for Reserved VM deployment (required for 24/7 background monitoring tasks). Bot runs via webhooks inside Flask web app with continuous price monitoring (60/min), 2-hour summaries, and heartbeat tracking. Uses Gunicorn production server with single worker, webhook secret token security, automatic mock mode in deployment, and graceful error handling.

### Features
- **Interactive Telegram Bot**: FIRST-TO-MARKET Arabic crypto trading assistant with dual language support, interactive menus, real-time signals, and user settings management. Includes instant price alerts and 2-hour summaries.
- **Telegram Mini App**: Modern React-based web application embedded inside Telegram with:
  - Wallet-style UI matching Telegram Wallet design (React + Vite + Tailwind CSS)
  - Real-time balance display with USDT/AED conversion
  - Trading interface with buy/sell confirmation and haptic feedback
  - Scalping signals page with entry/exit/stop-loss/take-profit data
  - Trade history with profit/loss tracking
  - Telegram SDK integration (themes, navigation, user authentication)
  - Secured REST API with Telegram initData validation (init-data-py)
  - Auto-price fetching from Binance for trades
  - Comprehensive input validation (symbols, amounts, trade types)
  - CORS restricted to Telegram domains only
  - Production-ready authentication (disabled in dev mode via REPLIT_DEPLOYMENT check)
- **Live Trading System**: Real Binance integration with /balance showing wallet holdings in USDT/AED, /trade for manual buy/sell execution with confirmation, /history for trade tracking, and /auto command (feature coming soon).
- **Trading Profit Calculator**: Real-time profit/loss tracking for 1000 AED investment across 10 currencies. Shows current value, weekly projections, top performers, and trading activity metrics. Accessible via /profit command or main menu.
- **Production Monitoring System**: 24/7 deployment health tracking with:
  - Heartbeat monitoring (60-second intervals) for both development and production environments
  - Dual-environment dashboard showing dev vs production status side-by-side
  - Critical alerts (visual + sound) when production bot goes offline (3-minute timeout)
  - Deployment configuration validator (checks VM type, startup scripts, production readiness)
  - Real-time heartbeat tracking with "last seen" timestamps
  - Automatic environment detection (development vs deployed)
- **Web Dashboard**: Provides a live view of market data and signals.
- **Health Monitoring**: Dedicated dashboard with real-time checks, visual and sound alerts, and a remote control panel for bot management.
- **Market Data**: Tracks real-time prices for top 10 cryptocurrencies from Binance.
- **Trading Signals**: Automated generation with trend analysis.
- **Reports**: Daily, Weekly, and Monthly crypto performance reports.
- **CLI Interface**: Command-line access to all features for local interaction.

## External Dependencies
- **python-binance**: Binance API wrapper for market data and trading.
- **psycopg2-binary**: PostgreSQL database adapter for Python.
- **requests**: HTTP library for making web requests.
- **python-telegram-bot**: Framework for building the Telegram bot.
- **python-dotenv**: Manages environment variables.
- **flask**: Web framework for the dashboard.
- **flask-cors**: CORS support for secure API access.
- **gunicorn**: Production WSGI server for deployment.
- **openpyxl**: Used for Excel-based user settings storage fallback.
- **nest-asyncio**: Enables nested event loops for concurrent operations.
- **APScheduler**: Used for scheduling background tasks like auto-notifications.
- **init-data-py**: Telegram Mini App authentication library for validating initData.

## Recent Changes (November 2024)
- **PostgreSQL Migration**: Migrated from Excel-based storage to PostgreSQL with graceful fallback. Includes adapter pattern in EnhancedTelegramBot for seamless switching.
- **Trading System Integration**: Added /balance, /trade, /history commands with real Binance API integration. Trade history and profit/loss tracking stored in database.
- **Scalping Signals**: Implemented advanced signal generator with entry/exit prices, stop-loss (0.5%), and take-profit (1.5%) calculations.
- **Production Hardening**: Database initialization with graceful fallback, error handling in all API endpoints, conditional trading command registration.
- **Auto-Trading Placeholder**: Auto-trading scheduler infrastructure in place, feature disabled with "coming soon" message until full implementation.
- **Telegram Mini App Implementation (November 15, 2025)**:
  - Built complete React + Vite + Tailwind CSS frontend with wallet-style UI
  - Created 6 secured REST API endpoints with Telegram initData authentication
  - Implemented auto-price fetching for trades (no manual price input needed)
  - Added comprehensive input validation (symbols, amounts, types)
  - Auto-user creation for foreign key constraint compliance
  - CORS locked to Telegram domains only
  - Dev mode bypass enabled when REPLIT_DEPLOYMENT != 1
  - Build script (build_miniapp.sh) for deployment preparation
  - Served at /miniapp endpoint with static file handling
  - **Opera GX Dark Theme**: Complete UI overhaul to gaming aesthetic with deep black backgrounds, hot pink gradients, neon glow effects, and WCAG AA accessibility compliance (all contrast ratios ≥4.5:1)