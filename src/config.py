import models

feeds: list[models.FeedConfig] = [
    models.FeedConfig(
        name="sshclient",
        url="https://darklist.de/raw.php",
        source="darklist.de",
        disabled=False
    ),
]
