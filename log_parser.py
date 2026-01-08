"""
Access log parser for slow request correlation.
"""
import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class AccessLogEntry:
    """Parsed access log entry."""
    timestamp: datetime
    client_ip: str
    method: str
    path: str
    status_code: int
    response_time_ms: int
    bytes_sent: int
    user_agent: str


class AccessLogParser:
    """
    Parser for Tomcat access logs with slow request correlation.
    
    Supports common Tomcat access log patterns including response time.
    Pattern: %h %l %u %t "%r" %s %b %D "%{User-Agent}i"
    """
    
    # Combined log format with response time
    # 127.0.0.1 - - [01/Jan/2024:12:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234 5000 "Mozilla/5.0"
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+)\s+'
        r'(?P<ident>[\S]+)\s+'
        r'(?P<user>[\S]+)\s+'
        r'\[(?P<timestamp>[^\]]+)\]\s+'
        r'"(?P<method>\w+)\s+(?P<path>[^\s]+)\s+(?P<protocol>[^"]+)"\s+'
        r'(?P<status>\d+)\s+'
        r'(?P<bytes>\d+|-)\s+'
        r'(?P<response_time>\d+|-)\s*'
        r'"?(?P<user_agent>[^"]*)"?'
    )
    
    def __init__(self, log_path: str, slow_threshold_ms: int = 5000, max_entries: int = 10000):
        """
        Initialize access log parser.
        
        Args:
            log_path: Path to access log file
            slow_threshold_ms: Threshold for slow requests in milliseconds
            max_entries: Maximum number of entries to keep in memory
        """
        self.log_path = log_path
        self.slow_threshold_ms = slow_threshold_ms
        self.max_entries = max_entries
        
        # Keep recent entries in memory
        self.recent_entries = deque(maxlen=max_entries)
        self.slow_requests = deque(maxlen=1000)
        
        # File position for incremental reading
        self.file_position = 0
        
        logger.info(f"Access log parser initialized for {log_path}")
    
    def parse_line(self, line: str) -> Optional[AccessLogEntry]:
        """
        Parse a single access log line.
        
        Args:
            line: Log line to parse
        
        Returns:
            AccessLogEntry or None if parsing fails
        """
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            logger.debug(f"Failed to parse log line: {line[:100]}")
            return None
        
        try:
            groups = match.groupdict()
            
            # Parse timestamp
            timestamp_str = groups['timestamp']
            # Format: 01/Jan/2024:12:00:00 +0000
            timestamp = datetime.strptime(
                timestamp_str.split()[0],
                '%d/%b/%Y:%H:%M:%S'
            )
            
            # Parse response time
            response_time_str = groups['response_time']
            response_time_ms = int(response_time_str) if response_time_str != '-' else 0
            
            # Parse bytes
            bytes_str = groups['bytes']
            bytes_sent = int(bytes_str) if bytes_str != '-' else 0
            
            entry = AccessLogEntry(
                timestamp=timestamp,
                client_ip=groups['ip'],
                method=groups['method'],
                path=groups['path'],
                status_code=int(groups['status']),
                response_time_ms=response_time_ms,
                bytes_sent=bytes_sent,
                user_agent=groups['user_agent']
            )
            
            return entry
        except Exception as e:
            logger.error(f"Error parsing log entry: {e}")
            return None
    
    def tail_log(self, num_lines: int = 1000) -> List[AccessLogEntry]:
        """
        Read the last N lines from the access log.
        
        Args:
            num_lines: Number of lines to read from the end
        
        Returns:
            List of parsed log entries
        """
        entries = []
        
        try:
            with open(self.log_path, 'r') as f:
                # Seek to end and read last N lines
                lines = deque(f, maxlen=num_lines)
                
                for line in lines:
                    entry = self.parse_line(line)
                    if entry:
                        entries.append(entry)
                        self.recent_entries.append(entry)
                        
                        # Track slow requests
                        if entry.response_time_ms >= self.slow_threshold_ms:
                            self.slow_requests.append(entry)
        
        except FileNotFoundError:
            logger.warning(f"Access log not found: {self.log_path}")
        except Exception as e:
            logger.error(f"Error reading access log: {e}")
        
        return entries
    
    def get_slow_requests(self, limit: int = 100) -> List[AccessLogEntry]:
        """
        Get recent slow requests.
        
        Args:
            limit: Maximum number of slow requests to return
        
        Returns:
            List of slow request entries
        """
        return list(self.slow_requests)[-limit:]
    
    def get_request_stats(self) -> Dict[str, Any]:
        """
        Get statistics about recent requests.
        
        Returns:
            Dictionary with request statistics
        """
        if not self.recent_entries:
            return {
                'total_requests': 0,
                'slow_requests': 0,
                'avg_response_time_ms': 0,
                'max_response_time_ms': 0,
                'status_codes': {},
                'top_paths': []
            }
        
        entries = list(self.recent_entries)
        
        # Calculate stats
        response_times = [e.response_time_ms for e in entries if e.response_time_ms > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Count status codes
        status_codes = {}
        for entry in entries:
            status = entry.status_code
            status_codes[status] = status_codes.get(status, 0) + 1
        
        # Count paths
        path_counts = {}
        for entry in entries:
            path = entry.path
            path_counts[path] = path_counts.get(path, 0) + 1
        
        # Get top paths
        top_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_requests': len(entries),
            'slow_requests': len([e for e in entries if e.response_time_ms >= self.slow_threshold_ms]),
            'avg_response_time_ms': avg_response_time,
            'max_response_time_ms': max_response_time,
            'status_codes': status_codes,
            'top_paths': [{'path': p, 'count': c} for p, c in top_paths]
        }
    
    def correlate_slow_requests_with_threads(self, stuck_thread_timestamps: List[float]) -> List[Dict[str, Any]]:
        """
        Correlate slow requests with stuck thread detections.
        
        Args:
            stuck_thread_timestamps: List of timestamps when stuck threads were detected
        
        Returns:
            List of correlated events
        """
        correlations = []
        
        slow_requests = self.get_slow_requests()
        
        for request in slow_requests:
            request_timestamp = request.timestamp.timestamp()
            
            # Check if any stuck thread detection was within 30 seconds of this request
            for stuck_timestamp in stuck_thread_timestamps:
                time_diff = abs(request_timestamp - stuck_timestamp)
                
                if time_diff <= 30:  # 30 second window
                    correlations.append({
                        'request': asdict(request),
                        'stuck_thread_timestamp': stuck_timestamp,
                        'time_difference_seconds': time_diff
                    })
                    break
        
        return correlations
