echo "→ Rodando black..."
black apps/

echo "→ Rodando isort..."
isort apps/

echo "→ Rodando flake8..."
flake8 apps/

echo "✓ Feito!"