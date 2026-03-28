"""
JMX monitoring module for Tomcat metrics collection.
Uses read-only JMX access to gather thread, heap, and thread pool metrics.
"""
import logging
import socket
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ThreadInfo:
    """Thread information from thread dump."""
    thread_id: int
    name: str
    state: str
    blocked_count: int
    blocked_time: int
    waited_count: int
    waited_time: int
    in_native: bool
    suspended: bool
    stack_trace: List[str]


@dataclass
class HeapMetrics:
    """Heap memory metrics."""
    used: int
    max: int
    committed: int
    usage_percent: float
    timestamp: float


@dataclass
class ThreadPoolMetrics:
    """Thread pool metrics."""
    current_threads: int
    current_busy: int
    max_threads: int
    utilization: float
    timestamp: float


class JMXMonitor:
    """
    JMX-based monitoring for Tomcat.
    
    Note: This is a simplified implementation using socket-based communication.
    In production, you would use jpype1 or py4j for full JMX support.
    """
    
    def __init__(self, host: str, port: int, timeout: int = 10):
        """Initialize JMX monitor."""
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connected = False
        
        # Track blocked threads
        self.thread_blocked_counts = defaultdict(int)
        self.thread_history = []
        
        # Track heap metrics for trend analysis
        self.heap_history = []
        self.oldgen_history = []
        
        logger.info(f"JMX Monitor initialized for {host}:{port}")
    
    def connect(self) -> bool:
        """
        Test JMX connection.
        
        Note: In a real implementation, this would establish JMX connection.
        For this demo, we simulate the connection check.
        """
        try:
            # Simulate connection check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                self.connected = True
                logger.info(f"JMX connection established to {self.host}:{self.port}")
                return True
            else:
                logger.warning(f"JMX port {self.port} not reachable")
                self.connected = False
                return False
        except Exception as e:
            logger.error(f"Failed to connect to JMX: {e}")
            self.connected = False
            return False
    
    def get_thread_dump(self) -> List[ThreadInfo]:
        """
        Get thread dump from JVM.
        
        Note: In production, this would use JMX ThreadMXBean.dumpAllThreads()
        For this demo, we return simulated data.
        """
        if not self.connected:
            logger.warning("Not connected to JMX, using simulated data")
        
        # Simulated thread dump data
        # In production: use jmx.invoke('java.lang:type=Threading', 'dumpAllThreads', [True, True])
        import random
        
        threads = []
        thread_states = ['RUNNABLE', 'WAITING', 'TIMED_WAITING', 'BLOCKED']
        
        for i in range(20):
            # Simulate some blocked threads
            state = random.choice(thread_states) if i < 15 else 'BLOCKED'
            blocked_count = random.randint(0, 10) if state == 'BLOCKED' else 0
            
            thread = ThreadInfo(
                thread_id=i + 1,
                name=f"http-nio-8080-exec-{i + 1}",
                state=state,
                blocked_count=blocked_count,
                blocked_time=blocked_count * 1000,
                waited_count=random.randint(0, 100),
                waited_time=random.randint(0, 10000),
                in_native=False,
                suspended=False,
                stack_trace=[
                    f"org.apache.tomcat.util.net.NioEndpoint$SocketProcessor.run(NioEndpoint.java:123)",
                    f"java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:456)"
                ]
            )
            threads.append(thread)
        
        self.thread_history.append({
            'timestamp': time.time(),
            'threads': threads
        })
        
        # Keep only last hour of history
        cutoff = time.time() - 3600
        self.thread_history = [h for h in self.thread_history if h['timestamp'] > cutoff]
        
        return threads
    
    def get_stuck_threads(self, threshold: int = 5) -> List[ThreadInfo]:
        """
        Detect stuck or blocked threads.
        
        Args:
            threshold: Number of consecutive times a thread must be blocked
        
        Returns:
            List of stuck threads
        """
        threads = self.get_thread_dump()
        
        # Update blocked counts
        for thread in threads:
            if thread.state == 'BLOCKED':
                self.thread_blocked_counts[thread.thread_id] += 1
            else:
                self.thread_blocked_counts[thread.thread_id] = 0
        
        # Find threads exceeding threshold
        stuck_threads = []
        for thread in threads:
            if self.thread_blocked_counts[thread.thread_id] >= threshold:
                stuck_threads.append(thread)
        
        if stuck_threads:
            logger.warning(f"Detected {len(stuck_threads)} stuck threads")
        
        return stuck_threads
    
    def get_heap_metrics(self) -> HeapMetrics:
        """
        Get heap memory metrics.
        
        Note: In production, use JMX MemoryMXBean.getHeapMemoryUsage()
        """
        # Simulated heap metrics
        # In production: use jmx.getAttribute('java.lang:type=Memory', 'HeapMemoryUsage')
        import random
        
        max_heap = 1024 * 1024 * 1024  # 1GB
        # Simulate growing heap
        base_used = int(max_heap * 0.5)
        variance = int(max_heap * 0.1)
        used = base_used + random.randint(-variance, variance)
        
        metrics = HeapMetrics(
            used=used,
            max=max_heap,
            committed=max_heap,
            usage_percent=used / max_heap,
            timestamp=time.time()
        )
        
        self.heap_history.append(metrics)
        
        # Keep only last hour
        cutoff = time.time() - 3600
        self.heap_history = [h for h in self.heap_history if h.timestamp > cutoff]
        
        return metrics
    
    def get_oldgen_metrics(self) -> Dict[str, Any]:
        """
        Get Old Generation memory pool metrics.
        
        Note: In production, use JMX MemoryPoolMXBean for 'PS Old Gen' or 'G1 Old Gen'
        """
        # Simulated OldGen metrics
        import random
        
        max_oldgen = 768 * 1024 * 1024  # 768MB
        base_used = int(max_oldgen * 0.6)
        variance = int(max_oldgen * 0.05)
        used = base_used + random.randint(-variance, variance)
        
        metrics = {
            'used': used,
            'max': max_oldgen,
            'committed': max_oldgen,
            'usage_percent': used / max_oldgen,
            'timestamp': time.time()
        }
        
        self.oldgen_history.append(metrics)
        
        # Keep only last hour
        cutoff = time.time() - 3600
        self.oldgen_history = [h for h in self.oldgen_history if h['timestamp'] > cutoff]
        
        return metrics
    
    def predict_oom(self, window_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """
        Predict OOM based on heap growth trend.
        
        Args:
            window_seconds: Time window for trend analysis
        
        Returns:
            Prediction dict with time_to_oom or None if no OOM predicted
        """
        if len(self.heap_history) < 2:
            return None
        
        # Filter to window
        cutoff = time.time() - window_seconds
        recent_metrics = [h for h in self.heap_history if h.timestamp > cutoff]
        
        if len(recent_metrics) < 2:
            return None
        
        # Calculate growth rate (bytes per second)
        first = recent_metrics[0]
        last = recent_metrics[-1]
        
        time_diff = last.timestamp - first.timestamp
        if time_diff <= 0:
            return None
        
        usage_diff = last.used - first.used
        growth_rate = usage_diff / time_diff
        
        # If not growing, no OOM predicted
        if growth_rate <= 0:
            return None
        
        # Calculate time to max heap
        available = last.max - last.used
        time_to_oom = available / growth_rate
        
        if time_to_oom < 0:
            time_to_oom = 0
        
        return {
            'predicted': True,
            'time_to_oom_seconds': time_to_oom,
            'growth_rate_mb_per_sec': growth_rate / (1024 * 1024),
            'current_usage_percent': last.usage_percent,
            'timestamp': time.time()
        }
    
    def get_thread_pool_metrics(self) -> ThreadPoolMetrics:
        """
        Get Tomcat thread pool metrics.
        
        Note: In production, use JMX ThreadPoolMXBean
        ObjectName: Catalina:type=ThreadPool,name="http-nio-8080"
        """
        # Simulated thread pool metrics
        import random
        
        max_threads = 200
        current_threads = random.randint(50, 150)
        current_busy = random.randint(20, current_threads)
        
        metrics = ThreadPoolMetrics(
            current_threads=current_threads,
            current_busy=current_busy,
            max_threads=max_threads,
            utilization=current_busy / max_threads,
            timestamp=time.time()
        )
        
        return metrics
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all JMX metrics in one call."""
        return {
            'heap': asdict(self.get_heap_metrics()),
            'oldgen': self.get_oldgen_metrics(),
            'thread_pool': asdict(self.get_thread_pool_metrics()),
            'stuck_threads': len(self.get_stuck_threads()),
            'oom_prediction': self.predict_oom(),
            'timestamp': time.time()
        }
