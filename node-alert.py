import requests
import json

# Liste des dépôts à surveiller, les rôles et les liens des channels associés
REPOS = {
    "t3rn/executor-release": {
        "role_id": "1328789711048806470",  # ID du rôle @t3rn
        "channel_url": "https://discord.com/channels/1199141848946577428/1323700696297508969"  # Lien vers le channel t3rn
    },
    "hemilabs/heminetwork": {
        "role_id": "1328789607336116316",  # ID du rôle @Hemi Network
        "channel_url": "https://discord.com/channels/1199141848946577428/1287483692805259264"  # Lien vers le channel Hemi
    }
}

# Fichier pour sauvegarder les versions actuelles
VERSIONS_FILE = "current_versions.json"

# Webhook Discord pour les notifications
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1329543415221715108/kq1wMw5QkBTOXcubyWJbzkLoJBUUP1Kg5j4iSxNYtfQZOgui_jaHCs4XBhQqazOXyYOT"

# Charger les versions sauvegardées
def load_versions():
    try:
        with open(VERSIONS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Sauvegarder les versions actuelles
def save_versions(versions):
    with open(VERSIONS_FILE, "w") as f:
        json.dump(versions, f, indent=4)

# Vérifier les dernières versions des dépôts
def check_releases():
    headers = {"Accept": "application/vnd.github.v3+json"}
    current_versions = load_versions()
    new_versions = {}

    for repo, data in REPOS.items():
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            release_data = response.json()
            latest_version = release_data.get("tag_name")
            release_url = release_data.get("html_url")

            if latest_version:
                # Si la version a changé, envoyer une notification
                if repo not in current_versions or current_versions[repo] != latest_version:
                    send_discord_notification(repo, latest_version, release_url, data["role_id"], data["channel_url"])

                # Mettre à jour les versions actuelles
                new_versions[repo] = latest_version
            else:
                print(f"Impossible de trouver une version pour le dépôt : {repo}")
        else:
            print(f"Erreur lors de la récupération des données pour {repo}: {response.status_code}")

    # Sauvegarder les nouvelles versions
    save_versions(new_versions)

# Envoyer une notification Discord
def send_discord_notification(repo, version, url, role_id, channel_url):
    message = {
        "content": (
            f"<@&{role_id}> 🚀 Nex release detected !\n"
            f"**Project**: `{repo}`\n"
            f"**Version**: `{version}`\n"
            f"🔗 [See the release]({url})\n"
            f"💬 [Channel]({channel_url})"
        )
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)

    if response.status_code == 204:
        print(f"Notification envoyée pour {repo} version {version}.")
    else:
        print(f"Erreur lors de l'envoi de la notification Discord : {response.status_code}")

# Exécution principale
if __name__ == "__main__":
    print("Vérification des dernières versions...")
    check_releases()
