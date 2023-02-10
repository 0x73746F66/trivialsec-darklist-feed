import models

feeds: list[models.FeedConfig] = [
    models.FeedConfig(
        name="fail2ban",
        url="https://darklist.de/raw.php",
        source="darklist.de",
        disabled=False
    ),
]
