"""
OS metrics collection using psutil.
"""
import psutil
import logging
from typing import Dict, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class OSMetrics:
    """OS-level metrics."""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_free_gb: float
    disk_total_gb: float
    load_average: tuple
    timestamp: float


class OSMonitor:
    """Monitor OS-level metrics using psutil."""
    
    def __init__(self, disk_path: str = '/'):
        """
        Initialize OS monitor.
        
        Args:
            disk_path: Disk path to monitor (default: root)
        """
        self.disk_path = disk_path
        logger.info("OS Monitor initialized")
    
    def get_cpu_metrics(self) -> Dict[str, float]:
        """Get CPU metrics."""
        # Get CPU percent (averaged over 1 second)
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get per-CPU percentages
        per_cpu = psutil.cpu_percent(interval=0, percpu=True)
        
        # Get load average (Unix only)
        try:
            load_avg = psutil.getloadavg()
        except (AttributeError, OSError):
            load_avg = (0.0, 0.0, 0.0)
        
        return {
            'cpu_percent': cpu_percent,
            'per_cpu': per_cpu,
            'load_average_1m': load_avg[0],
            'load_average_5m': load_avg[1],
            'load_average_15m': load_avg[2],
            'cpu_count': psutil.cpu_count()
        }
    
    def get_memory_metrics(self) -> Dict[str, float]:
        """Get memory metrics."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_mb': mem.total / (1024 * 1024),
            'available_mb': mem.available / (1024 * 1024),
            'used_mb': mem.used / (1024 * 1024),
            'percent': mem.percent,
            'swap_total_mb': swap.total / (1024 * 1024),
            'swap_used_mb': swap.used / (1024 * 1024),
            'swap_percent': swap.percent
        }
    
    def get_disk_metrics(self) -> Dict[str, float]:
        """Get disk metrics."""
        try:
            disk = psutil.disk_usage(self.disk_path)
            
            return {
                'total_gb': disk.total / (1024 * 1024 * 1024),
                'used_gb': disk.used / (1024 * 1024 * 1024),
                'free_gb': disk.free / (1024 * 1024 * 1024),
                'percent': disk.percent
            }
        except Exception as e:
            logger.error(f"Failed to get disk metrics: {e}")
            return {
                'total_gb': 0,
                'used_gb': 0,
                'free_gb': 0,
                'percent': 0
            }
    
    def get_network_metrics(self) -> Dict[str, Any]:
        """Get network I/O metrics."""
        try:
            net_io = psutil.net_io_counters()
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout
            }
        except Exception as e:
            logger.error(f"Failed to get network metrics: {e}")
            return {}
    
    def get_process_count(self) -> int:
        """Get total number of running processes."""
        try:
            return len(psutil.pids())
        except Exception as e:
            logger.error(f"Failed to get process count: {e}")
            return 0
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all OS metrics."""
        import time
        
        return {
            'cpu': self.get_cpu_metrics(),
            'memory': self.get_memory_metrics(),
            'disk': self.get_disk_metrics(),
            'network': self.get_network_metrics(),
            'process_count': self.get_process_count(),
            'timestamp': time.time()
        }
    
    def to_os_metrics(self) -> OSMetrics:
        """Convert to OSMetrics dataclass."""
        import time
        
        cpu = self.get_cpu_metrics()
        memory = self.get_memory_metrics()
        disk = self.get_disk_metrics()
        
        return OSMetrics(
            cpu_percent=cpu['cpu_percent'],
            memory_percent=memory['percent'],
            memory_available_mb=memory['available_mb'],
            memory_total_mb=memory['total_mb'],
            disk_percent=disk['percent'],
            disk_free_gb=disk['free_gb'],
            disk_total_gb=disk['total_gb'],
            load_average=(
                cpu['load_average_1m'],
                cpu['load_average_5m'],
                cpu['load_average_15m']
            ),
            timestamp=time.time()
        )
