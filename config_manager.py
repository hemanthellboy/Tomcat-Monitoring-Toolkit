"""
Configuration management module with fail-fast validation.
"""
import os
import sys
import yaml
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


class Config:
    """Configuration manager with validation."""
    
    REQUIRED_KEYS = {
        'jmx': ['host', 'port'],
        'tomcat': ['access_log_path', 'slow_request_threshold'],
        'monitoring': ['heap_warn_threshold', 'heap_critical_threshold'],
        'alerts': ['enabled'],
        'ui': ['host', 'port']
    }
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize configuration from YAML file."""
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config:
                raise ConfigurationError("Configuration file is empty")
            
            return config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML syntax: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def _validate_config(self):
        """Validate configuration structure and values."""
        # Check required sections
        for section, keys in self.REQUIRED_KEYS.items():
            if section not in self.config:
                raise ConfigurationError(f"Missing required section: {section}")
            
            for key in keys:
                if key not in self.config[section]:
                    raise ConfigurationError(f"Missing required key: {section}.{key}")
        
        # Validate specific values
        self._validate_jmx()
        self._validate_thresholds()
        self._validate_health_score_weights()
    
    def _validate_jmx(self):
        """Validate JMX configuration."""
        jmx = self.config['jmx']
        
        if not isinstance(jmx['port'], int) or jmx['port'] < 1 or jmx['port'] > 65535:
            raise ConfigurationError(f"Invalid JMX port: {jmx['port']}")
        
        if not isinstance(jmx['host'], str) or not jmx['host']:
            raise ConfigurationError("JMX host must be a non-empty string")
    
    def _validate_thresholds(self):
        """Validate monitoring thresholds."""
        monitoring = self.config['monitoring']
        
        threshold_keys = [
            'heap_warn_threshold', 'heap_critical_threshold',
            'oldgen_warn_threshold', 'oldgen_critical_threshold',
            'cpu_warn_threshold', 'cpu_critical_threshold',
            'memory_warn_threshold', 'memory_critical_threshold',
            'disk_warn_threshold', 'disk_critical_threshold'
        ]
        
        for key in threshold_keys:
            if key in monitoring:
                value = monitoring[key]
                if not isinstance(value, (int, float)) or value < 0 or value > 1:
                    raise ConfigurationError(f"{key} must be between 0 and 1")
        
        # Validate warn < critical
        pairs = [
            ('heap_warn_threshold', 'heap_critical_threshold'),
            ('oldgen_warn_threshold', 'oldgen_critical_threshold'),
            ('cpu_warn_threshold', 'cpu_critical_threshold'),
            ('memory_warn_threshold', 'memory_critical_threshold'),
            ('disk_warn_threshold', 'disk_critical_threshold')
        ]
        
        for warn_key, crit_key in pairs:
            if monitoring.get(warn_key, 0) >= monitoring.get(crit_key, 1):
                raise ConfigurationError(f"{warn_key} must be less than {crit_key}")
    
    def _validate_health_score_weights(self):
        """Validate health score weights sum to 1.0."""
        if 'health_score' not in self.config:
            return
        
        weights = self.config['health_score']
        total = sum(weights.values())
        
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ConfigurationError(f"Health score weights must sum to 1.0, got {total}")
    
    def get(self, *keys, default=None):
        """Get configuration value by nested keys."""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def __getitem__(self, key):
        """Get configuration section."""
        return self.config[key]


def load_config(config_path: str = 'config.yaml') -> Config:
    """Load and validate configuration with fail-fast behavior."""
    try:
        config = Config(config_path)
        logger.info(f"Configuration loaded successfully from {config_path}")
        return config
    except ConfigurationError as e:
        logger.error(f"Configuration validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        sys.exit(1)
