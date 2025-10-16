#!/bin/bash

REPO_URL="https://github.com/kdefycom/-KDFY.git"
COMMIT_MSG="Atualização automática"

cd "$(dirname "$0")"

read -p "Usuário GitHub: " USER
read -sp "Token GitHub: " TOKEN
echo

if [ ! -d ".git" ]; then
    git init
fi

if ! git remote | grep -q origin; then
    git remote add origin "$REPO_URL"
fi

git add .
git commit -m "$COMMIT_MSG" 2>/dev/null

git push https://$USER:$TOKEN@github.com/kdefycom/-KDFY.git main --force
