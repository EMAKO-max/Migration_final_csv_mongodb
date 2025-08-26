# =============================
# Utiliser une image Python légère
# =============================
FROM python:3.10-slim

# =============================
#  Définir le répertoire de travail à l'intérieur du conteneur
# =============================
WORKDIR /app

# =============================
# Installer les dépendances systèmes pour pandas/numpy
# =============================
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libbz2-dev \
    liblzma-dev \
    libsqlite3-dev \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =============================
# Copier le fichier des dépendances
# =============================
COPY requirements.txt .

# =============================
# Installer les dépendances Python
# =============================
RUN pip install --no-cache-dir -r requirements.txt

# =============================
# Copier tout le code de l'application
# =============================
COPY . .

# =============================
# Commande par défaut : exécuter le script d'import CSV
# =============================
CMD ["python", "migration_csv_mongodb.py"]