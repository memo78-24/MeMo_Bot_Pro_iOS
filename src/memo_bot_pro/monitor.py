"""
Bot Health Monitoring System
Continuously monitors the trading bot and alerts on issues
"""
import time
import os
import psutil
from datetime import datetime
from typing import Dict, List
from .config import Config


class BotHealthMonitor:
    """Monitors the health of the trading bot and system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.alerts = []
        self.last_check = None
        self.acknowledged_alerts = set()
        self.last_telegram_check = 0  # Timestamp of last Telegram API call
        self.telegram_check_interval = 30  # Only check Telegram every 30 seconds
        self.cached_telegram_status = None
        
    def check_health(self) -> Dict:
        """Perform comprehensive health check"""
        # Reload config to detect credential changes
        self.config = Config.from_env()
        
        self.last_check = datetime.now()
        health_status = {
            'timestamp': self.last_check.isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'active_alerts': []
        }
        
        # Check 1: Binance API connectivity
        api_status = self._check_binance_api()
        health_status['checks']['binance_api'] = api_status
        if not api_status['healthy']:
            health_status['overall_status'] = 'critical'
            health_status['active_alerts'].append({
                'severity': 'critical',
                'message': 'Binance API connection failed!',
                'details': api_status.get('error', 'Unknown error')
            })
        
        # Check 2: Telegram Bot connectivity
        telegram_status = self._check_telegram_bot()
        health_status['checks']['telegram_bot'] = telegram_status
        if not telegram_status['healthy']:
            health_status['overall_status'] = 'critical'
            health_status['active_alerts'].append({
                'severity': 'critical',
                'message': 'Telegram Bot connection failed!',
                'details': telegram_status.get('error', 'Unknown error')
            })
        
        # Check 3: System resources
        resource_status = self._check_system_resources()
        health_status['checks']['system_resources'] = resource_status
        if not resource_status['healthy']:
            if health_status['overall_status'] != 'critical':
                health_status['overall_status'] = 'warning'
            health_status['active_alerts'].append({
                'severity': 'warning',
                'message': 'System resources low!',
                'details': resource_status.get('error', 'Check CPU/Memory')
            })
        
        # Check 4: Configuration validity
        config_status = self._check_configuration()
        health_status['checks']['configuration'] = config_status
        if not config_status['healthy']:
            health_status['overall_status'] = 'critical'
            health_status['active_alerts'].append({
                'severity': 'critical',
                'message': 'Configuration error!',
                'details': config_status.get('error', 'Invalid config')
            })
        
        # Check 5: Mock mode check
        mock_status = self._check_mock_mode()
        health_status['checks']['mock_mode'] = mock_status
        if not mock_status['healthy']:
            if health_status['overall_status'] == 'healthy':
                health_status['overall_status'] = 'warning'
            health_status['active_alerts'].append({
                'severity': 'warning',
                'message': 'Running in MOCK MODE!',
                'details': 'Switch to live mode for real data'
            })
        
        return health_status
    
    def _check_binance_api(self) -> Dict:
        """Check Binance API connection with real API call"""
        try:
            if not self.config.binance_api_key or not self.config.binance_api_secret:
                return {
                    'healthy': False,
                    'error': 'Binance API credentials not configured',
                    'status': 'No API keys found'
                }
            
            # Make a real lightweight API call to test connectivity
            # IMPORTANT: Don't use mock mode for health checks - we need to test REAL API
            from .binance_client import BinanceClient
            try:
                # Force live mode for health check (bypass deployment mock mode)
                client = BinanceClient(
                    api_key=self.config.binance_api_key,
                    api_secret=self.config.binance_api_secret,
                    mock=False  # Always test real API for health monitoring
                )
                
                # Try to get prices - lightweight operation
                prices = client.get_all_prices()
                
                if not prices or len(prices) == 0:
                    return {
                        'healthy': False,
                        'error': 'Binance API returned no data',
                        'status': 'No data received'
                    }
                
                return {
                    'healthy': True,
                    'status': 'Connected',
                    'mode': 'Mock' if self.config.mock_mode else 'Live',
                    'pairs_available': len(prices)
                }
            except Exception as api_error:
                return {
                    'healthy': False,
                    'error': f'Binance API call failed: {str(api_error)}',
                    'status': 'Connection Failed'
                }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'status': 'Error'
            }
    
    def _check_telegram_bot(self) -> Dict:
        """Check Telegram bot connection with real API call (rate-limited)"""
        try:
            if not self.config.telegram_bot_token:
                return {
                    'healthy': False,
                    'error': 'Telegram bot token not configured',
                    'status': 'No token found'
                }
            
            # Rate limiting: Only check Telegram API every 30 seconds to avoid hitting rate limits
            current_time = time.time()
            if current_time - self.last_telegram_check < self.telegram_check_interval:
                # Return cached status if within rate limit window
                if self.cached_telegram_status:
                    return self.cached_telegram_status
            
            # Make a real lightweight API call to test bot connectivity
            import requests
            try:
                self.last_telegram_check = current_time
                # Use getMe endpoint - lightweight operation to verify bot is alive
                url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/getMe"
                response = requests.get(url, timeout=5)
                
                if response.status_code != 200:
                    return {
                        'healthy': False,
                        'error': f'Telegram API returned status {response.status_code}',
                        'status': 'Invalid Token'
                    }
                
                data = response.json()
                if not data.get('ok'):
                    return {
                        'healthy': False,
                        'error': 'Telegram API returned error',
                        'status': 'Bot Not Found'
                    }
                
                bot_info = data.get('result', {})
                result = {
                    'healthy': True,
                    'status': 'Connected',
                    'admins': len(self.config.admin_user_ids),
                    'bot_username': bot_info.get('username', 'unknown')
                }
                self.cached_telegram_status = result  # Cache for rate limiting
                return result
            except requests.Timeout:
                result = {
                    'healthy': False,
                    'error': 'Telegram API timeout (>5s)',
                    'status': 'Connection Timeout'
                }
                self.cached_telegram_status = result
                return result
            except Exception as api_error:
                result = {
                    'healthy': False,
                    'error': f'Telegram API call failed: {str(api_error)}',
                    'status': 'Connection Failed'
                }
                self.cached_telegram_status = result
                return result
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'status': 'Error'
            }
    
    def _check_system_resources(self) -> Dict:
        """Check system CPU and memory usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            healthy = True
            issues = []
            
            if cpu_percent > 90:
                healthy = False
                issues.append(f'High CPU usage: {cpu_percent}%')
            
            if memory.percent > 90:
                healthy = False
                issues.append(f'High memory usage: {memory.percent}%')
            
            return {
                'healthy': healthy,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'error': ', '.join(issues) if issues else None,
                'status': 'OK' if healthy else 'Warning'
            }
        except Exception as e:
            return {
                'healthy': True,  # Don't fail on resource check errors
                'error': str(e),
                'status': 'Unable to check'
            }
    
    def _check_configuration(self) -> Dict:
        """Check configuration validity"""
        try:
            issues = []
            
            if not self.config.validate_binance():
                issues.append('Binance credentials invalid')
            
            if not self.config.validate_telegram():
                issues.append('Telegram token invalid')
            
            return {
                'healthy': len(issues) == 0,
                'error': ', '.join(issues) if issues else None,
                'status': 'Valid' if len(issues) == 0 else 'Invalid'
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'status': 'Error'
            }
    
    def _check_mock_mode(self) -> Dict:
        """Check if running in mock mode"""
        return {
            'healthy': not self.config.mock_mode,
            'status': 'Mock Mode' if self.config.mock_mode else 'Live Mode',
            'error': 'Running in mock mode with simulated data' if self.config.mock_mode else None
        }
    
    def acknowledge_alert(self, alert_id: str):
        """Mark an alert as acknowledged"""
        self.acknowledged_alerts.add(alert_id)
    
    def get_unacknowledged_alerts(self, health_status: Dict) -> List[Dict]:
        """Get alerts that haven't been acknowledged"""
        alerts = health_status.get('active_alerts', [])
        unack = []
        for alert in alerts:
            alert_id = f"{alert['severity']}_{alert['message']}"
            if alert_id not in self.acknowledged_alerts:
                alert['id'] = alert_id
                unack.append(alert)
        return unack
