#!/usr/bin/env python
import os
import sys


import uptrace
from opentelemetry import trace

# copy your project DSN here or use UPTRACE_DSN env var
uptrace.configure_opentelemetry(
    dsn=os.getenv("UPTRACE_DSN"),
    service_name="My Grateful Jar Service",
    service_version="1.0.0",
    deployment_environment="development",
)

tracer = trace.get_tracer("app_or_package_name", "1.0.0")


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

