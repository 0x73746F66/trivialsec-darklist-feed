import models

feeds: list[models.FeedConfig] = [
    models.FeedConfig(
        name="fail2ban",
        description="Darklist.de is an IP blacklist that uses multiple sensors to identify network attacks (e.g. SSH brute force) and spam incidents. All reports are evaluated and in case of too many incidents the responsible IP holder is informed to solve the problem. After reporting an incident as solved the IP is removed from the blacklist",
        url="https://www.darklist.de/raw.php",
        alert_title="SSH Port Scanning and Bruteforcing Authentication",
        source="darklist.de",
        abuse="https://www.darklist.de/removal.php",
        disabled=False
    ),
]
