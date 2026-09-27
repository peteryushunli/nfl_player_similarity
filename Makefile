.PHONY: help install ingest test push-dry-run

HUB ?= $(HOME)/fantasy_football_manager_hub

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install the ingest's dependencies
	pip install -r requirements.txt

ingest: ## Rebuild data/nfl_similarity.db from nflverse (1999 through the latest completed season)
	python -m src.db.ingest

test: ## Check data/nfl_similarity.db still satisfies the hub's data contract
	python -m pytest -v

push-dry-run: ## Compare this DB with the hub's Supabase tables (read-only; --write stays manual)
	cd "$(HUB)" && node scripts/push-nfl-comps.mjs --db="$(CURDIR)/data/nfl_similarity.db"
