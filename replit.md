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
- **Web Dashboard**: A Flask-based web interface showing live market data and signals, designed for real-time updates every 30 seconds.
- **Monitoring Dashboard**: Includes big alert banners, looping sound alerts, and an acknowledgment system for critical issues.

### Technical Implementations
- **Binance Client**: Abstracts Binance API interactions, supporting mock mode for testing and focusing on the top 10 trending currencies.
- **Signal Generator**: Analyzes price data to generate trading recommendations.
- **User Storage**: Utilizes Excel (`openpyxl`) for storing user settings and preferences.
- **Translations**: Dedicated module for English and Arabic language support.
- **Configuration**: Environment-based configuration with support for `MOCK_MODE`.
- **Deployment**: Configured for Reserved VM deployment (required for 24/7 Telegram bot operation) with bash interpreter, Gunicorn production server, lightweight health checks, automatic mock mode in deployment, and graceful error handling. Uses start_production.sh for supervised bot startup with auto-restart.

### Features
- **Interactive Telegram Bot**: FIRST-TO-MARKET Arabic crypto trading assistant with dual language support, interactive menus, real-time signals, and user settings management. Includes instant price alerts and 2-hour summaries.
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
- **requests**: HTTP library for making web requests.
- **python-telegram-bot**: Framework for building the Telegram bot.
- **python-dotenv**: Manages environment variables.
- **flask**: Web framework for the dashboard.
- **gunicorn**: Production WSGI server for deployment.
- **openpyxl**: Used for Excel-based user settings storage.
- **nest-asyncio**: Enables nested event loops for concurrent operations.
- **APScheduler**: Used for scheduling background tasks like auto-notifications.