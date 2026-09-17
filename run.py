import uvicorn

from sergeant.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "Sergeant.app:app",
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level.lower(),
        reload=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
