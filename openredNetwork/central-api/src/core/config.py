import os
from typing import List
from dataclasses import dataclass
from enum import Enum

class NodeLifeState(Enum):
    ACTIVE = "active"
    PENDING_FIRST_CHECK = "pending_1st"
    FAILED_FIRST_CHECK = "failed_1st"
    PENDING_SECOND_CHECK = "pending_2nd"
    FAILED_SECOND_CHECK = "failed_2nd"
    RETRY_48H = "retry_48h"
    RETRY_2W = "retry_2w"
    RETRY_2M = "retry_2m"
    COMA = "coma"
    DEAD = "dead"

@dataclass
class AppConfig:
    app_name: str = "OpenRed Central API"
    app_version: str = "3.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "production"
    max_nodes: int = 100000
    max_request_size: int = 10485760

@dataclass
class SecurityConfig:
    min_key_size: int = 2048
    token_lifetime_seconds: int = 300
    max_tokens_per_node: int = 10

@dataclass
class DirectoryConfig:
    max_nodes: int = 100000
    initial_registration_lifetime: int = 31536000
    heartbeat_check_interval: int = 15552000
    required_failed_checks_for_coma: int = 2
    retry_48h_seconds: int = 172800
    retry_2w_seconds: int = 1209600
    retry_2m_seconds: int = 5184000
    max_coma_duration: int = 63072000

app_config = AppConfig()
security_config = SecurityConfig()
directory_config = DirectoryConfig()
